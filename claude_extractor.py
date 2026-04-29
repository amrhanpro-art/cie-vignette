# -*- coding: utf-8 -*-
"""
Extraction des informations via Claude API
"""
import anthropic
import json
import re

try:
    from config import ANTHROPIC_API_KEY
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    API_AVAILABLE = True
except Exception as e:
    API_AVAILABLE = False
    print(f"API non disponible: {e}")

EXTRACTION_PROMPT = """Tu es un assistant spécialisé dans l'analyse des rapports d'incidents électriques de la CIE (Compagnie Ivoirienne d'Électricité) en Côte d'Ivoire.

Analyse ce rapport et extrais les informations suivantes en JSON UNIQUEMENT (pas d'explication, pas de markdown) :

{
  "type": "infos_reseaux" | "travaux_reseaux" | "travaux_programmes",
  "lieu": "NOM DU LIEU géographique",
  "date": "DD/MM/YYYY (juste la date, pas le jour de la semaine)",
  "zones": "liste des zones séparées par virgule",
  "statut": "le statut approprié"
}

RÈGLES STRICTES SUR LE TYPE:
- "infos_reseaux": incident, déclenchement, panne, défaut, hors tension, cellule éteinte
- "travaux_reseaux": travaux HTB/HTA, manœuvre, maintenance, NIP, remplacement câble
- "travaux_programmes": travaux planifiés avec NIP programmé

RÈGLES STRICTES SUR LE LIEU:
- Le lieu est le nom COMMUN à toutes les zones. Exemples:
  * zones "RIVIERA TRIANGLE, ABATTA CITE DON MELO, RIVIERA BONOUMIN" → lieu = "RIVIERA" (car RIVIERA est commun)
  * zones "RIVIERA FAYA, RIVIERA AKOUEDO, RIVIERA PALMERAIE" → lieu = "RIVIERA"
  * zones "YOPOUGON ZONE INDUSTRIELLE" → lieu = "YOPOUGON"
  * zones "FAYA COQ IVOIRE" → lieu = "COCODY" (commune d'Abidjan)
  * zones "LA VILLE DE DABOU" → lieu = "DABOU"
  * zones "FRONAN, PETIONARA, KATIONON" → lieu = "KATIOLA" (ville de la région)
- JAMAIS une abréviation technique comme HT, HTB, HTA, BT, NIP, PS, DR, MW, KV, TFO, DCRD comme lieu
- Pour "*PS DIMBOKRO : départ TOUMODI" → lieu = "DIMBOKRO" (PS = poste source = ville principale, le départ est juste le nom de la ligne)
- Le lieu est TOUJOURS la ville du poste source (PS), jamais le nom du départ
- RÈGLE ABSOLUE : dans le pattern "*PS VILLE : départ NOM", le lieu est TOUJOURS VILLE (après PS), jamais NOM (après départ)
- Le lieu est TOUJOURS un nom propre seul, jamais "LA VILLE DE X" — extraire uniquement "X". Exemple: "La Ville de Dabou" → lieu = "DABOU"
- Pour "départ 2 PLATEAUX" → lieu = "2 PLATEAUX" (garder le chiffre)
- RIVIERA est un quartier de COCODY — si les zones contiennent à la fois COCODY et RIVIERA, lieu = "COCODY"
- Le lieu doit toujours être UN SEUL nom, jamais deux noms séparés par une virgule
- "YOP" est une abréviation de "YOPOUGON" → toujours remplacer "YOP " par "YOPOUGON " dans les zones (ex: "YOP KOWEIT" → "YOPOUGON KOWEIT")
- "YAKRO" est une abréviation de "YAMOUSSOUKRO" → toujours remplacer "YAKRO" par "YAMOUSSOUKRO" dans le lieu et les zones
- Corriger les noms mal orthographiés vers leur nom officiel : "PALAIS DE SPORT" → "PALAIS DES SPORTS", "CATHEDRALE SAINT PAUL" → "CATHÉDRALE SAINT-PAUL D'ABIDJAN"
- "NL" ou "N/L" est une abréviation de "Non Loin" — toujours supprimer "NL " et "N/L " des zones (ex: "NL DU PALAIS DE SPORT" → "PALAIS DES SPORTS")
- Quand les zones sont listées sans virgules dans l'input (ex: "DOKUI FOREST 2 BANCO ANADOR ABOBO SAGBE"), sépare chaque quartier/localité distinct par une virgule
- Pour "départ PALMERAIE 2" → lieu = "RIVIERA PALMERAIE" si les zones sont des RIVIERA
- Garder le nom EXACT du lieu tel qu'il apparaît dans le texte, ne pas le reformuler

RÈGLES STRICTES SUR LES ZONES:
- Garder les noms COMPLETS: "RIVIERA TRIANGLE", "RIVIERA BONOUMIN", "RIVIERA FAYA"
- Ne JAMAIS supprimer "RIVIERA" ou tout autre préfixe dans les noms de zones
- Garder "LA LOCALITÉ DE X", "LA VILLE DE X", "LE VILLAGE DE X" tels quels
- Supprimer seulement "les localités de" (pluriel), "les zones hors tension"
- Supprimer les points de suspension "…" en fin de liste
- Extraire TOUTES les zones mentionnées dans le rapport, même entre parenthèses
- Exemple: "3 postes hors tension (zone industrielle)" → inclure "ZONE INDUSTRIELLE" dans les zones
- Exemple: "Ebimpé extension (fin goudron jusqu'au Lycée Sainte Claire des Bois)" → zone = "EBIMPÉ EXTENSION FIN GOUDRON JUSQU'AU LYCÉE SAINTE CLAIRE DES BOIS"

RÈGLES SUR LE STATUT (valeurs EXACTES):
- "ÉQUIPES MOBILISÉES, TRAVAUX ET REPRISE EN COURS" → incident sans heure précise
- "ÉQUIPES MOBILISÉES , TRAVAUX EN COURS - REPRISE PRÉVUE À XXH" → si heure de reprise mentionnée
- "ÉQUIPES MOBILISÉES , TRAVAUX EN COURS - REPRISE PROGRESSIVE" → si reprise partielle

Rapport à analyser:
"""

def format_date(date_str):
    """Convertit DD/MM/YYYY en JOUR DD MOIS YYYY."""
    import datetime
    jours = ['LUNDI','MARDI','MERCREDI','JEUDI','VENDREDI','SAMEDI','DIMANCHE']
    mois = ['','JANVIER','FÉVRIER','MARS','AVRIL','MAI','JUIN','JUILLET','AOÛT','SEPTEMBRE','OCTOBRE','NOVEMBRE','DÉCEMBRE']
    try:
        # Extraire DD/MM/YYYY depuis la date
        import re
        m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', date_str)
        if not m:
            return date_str
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100: y += 2000
        dt = datetime.date(y, mo, d)
        return f"{jours[dt.weekday()]} {d} {mois[mo]} {y}"
    except:
        return date_str

def extract_with_claude(input_text):
    """Extrait les informations d'un rapport CIE via l'API Claude."""
    if not API_AVAILABLE:
        return None
    
    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[
                {
                    "role": "user", 
                    "content": EXTRACTION_PROMPT + input_text
                }
            ]
        )
        
        response_text = message.content[0].text.strip()
        # Nettoyer les backticks si présents
        response_text = re.sub(r'```json\s*|\s*```', '', response_text).strip()
        
        data = json.loads(response_text)
        # Calculer le jour correct en Python (l'API se trompe parfois)
        if data.get('date'):
            data['date'] = format_date(data['date'])
        return data
        
    except Exception as e:
        print(f"Erreur API Claude: {e}")
        return None
