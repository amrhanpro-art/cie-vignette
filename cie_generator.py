#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CIE Vignette Generator
Remplit automatiquement les templates CIE à partir d'un input brut.
"""

from PIL import Image, ImageDraw, ImageFont
import random
import re
import os
from datetime import datetime

# ── Chemins ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
FONT_PATH = os.path.join(BASE_DIR, "big_noodle_titling.ttf")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Couleurs ──────────────────────────────────────────────────────────────────
COLOR_DATE = "#FFFFFF"
COLOR_TEXTE_PRINCIPAL = "#545454"
COLOR_NOM_LIGNE = "#000000"
COLOR_ZONES_TITRE = "#FFFFFF"
COLOR_ZONES_TEXTE = "#FFFFFF"
COLOR_STATUT = "#2E3133"

# ── Coordonnées par template (détectées automatiquement) ─────────────────────
# Format: { template_id: { 'date': (x,y), 'bloc1': (x1,y1,x2,y2), 'zones_y': y, 'zones_x': x, 'bloc2': (x1,y1,x2,y2) } }
TEMPLATE_COORDS = {
    1:  {'date': (555,28), 'bloc1': (459,441,1067,635), 'zones_y': 710, 'zones_x': 479, 'zones_w': 568, 'bloc2': (459,852,1067,945)},
    2:  {'date': (555,28), 'bloc1': (449,441,1067,635), 'zones_y': 710, 'zones_x': 469, 'zones_w': 578, 'bloc2': (449,852,1067,945)},
    3:  {'date': (555,28), 'bloc1': (444,441,1067,635), 'zones_y': 710, 'zones_x': 464, 'zones_w': 583, 'bloc2': (444,852,1067,945)},
    4:  {'date': (555,28), 'bloc1': (471,441,1067,635), 'zones_y': 710, 'zones_x': 491, 'zones_w': 556, 'bloc2': (471,852,1067,945)},
    5:  {'date': (555,28), 'bloc1': (451,387,1067,579), 'zones_y': 655, 'zones_x': 471, 'zones_w': 576, 'bloc2': (451,914,1067,970)},
    6:  {'date': (555,28), 'bloc1': (451,379,1067,581), 'zones_y': 655, 'zones_x': 471, 'zones_w': 576, 'bloc2': (452,886,1067,970)},
    7:  {'date': (555,28), 'bloc1': (449,379,1067,581), 'zones_y': 655, 'zones_x': 469, 'zones_w': 578, 'bloc2': (449,886,1067,970)},
    8:  {'date': (555,28), 'bloc1': (444,362,1061,564), 'zones_y': 638, 'zones_x': 464, 'zones_w': 577, 'bloc2': (444,858,1051,938)},
    9:  {'date': (555,28), 'bloc1': (450,400,1061,603), 'zones_y': 677, 'zones_x': 470, 'zones_w': 571, 'bloc2': (450,914,1062,992)},
    10: {'date': (555,28), 'bloc1': (466,340,1061,534), 'zones_y': 608, 'zones_x': 486, 'zones_w': 555, 'bloc2': (468,907,1060,983)},
    11: {'date': (555,28), 'bloc1': (452,382,1061,578), 'zones_y': 652, 'zones_x': 472, 'zones_w': 569, 'bloc2': (453,883,1064,970)},
    12: {'date': (555,28), 'bloc1': (448,384,1061,558), 'zones_y': 632, 'zones_x': 468, 'zones_w': 573, 'bloc2': (448,877,1060,970)},
    13: {'date': (555,28), 'bloc1': (448,384,1061,558), 'zones_y': 632, 'zones_x': 468, 'zones_w': 573, 'bloc2': (448,888,1060,970)},
    14: {'date': (555,28), 'bloc1': (451,384,1061,558), 'zones_y': 632, 'zones_x': 471, 'zones_w': 570, 'bloc2': (451,894,1061,970)},
    15: {'date': (555,28), 'bloc1': (466,384,1061,558), 'zones_y': 632, 'zones_x': 486, 'zones_w': 555, 'bloc2': (468,877,1060,970)},
    16: {'date': (555,28), 'bloc1': (451,384,1061,558), 'zones_y': 632, 'zones_x': 471, 'zones_w': 570, 'bloc2': (451,894,1061,970)},
}

# ── Base de données géographique Côte d'Ivoire ───────────────────────────────
# Communes d'Abidjan
COMMUNES_ABIDJAN = [
    'ABOBO', 'ADJAME', 'ATTECOUBO', 'COCODY', 'KOUMASSI', 'MARCORY',
    'PLATEAU', 'PORT-BOUET', 'PORT BOUET', 'TREICHVILLE', 'YOPOUGON',
    'ANYAMA', 'BINGERVILLE', 'BROFODOUME', 'SONGON',
    'ABIDJAN NORD', 'ABIDJAN SUD', 'ABIDJAN'
]

# Quartiers et sous-quartiers d'Abidjan
QUARTIERS_ABIDJAN = [
    # COCODY
    'RIVIERA', 'RIVIERA 1', 'RIVIERA 2', 'RIVIERA 3', 'RIVIERA 4',
    'RIVIERA FAYA', 'RIVIERA AKOUEDO', 'RIVIERA PALMERAIE', 'RIVIERA BONOUMIN',
    'RIVIERA TRIANGLE', 'RIVIERA GOLF', 'RIVIERA ANONO', 'RIVIERA SYNACASSI',
    '2 PLATEAUX', 'DEUX PLATEAUX', '2PLATEAUX', 'ANGRE', 'ANGRE 8EME',
    'COCODY FAYA', 'COCODY BLOCKHAUS', 'COCODY SAINT-JEAN', 'COCOVICO',
    'FAYA COQ IVOIRE', 'COCODY FAYA COQ IVOIRE',
    'AMBASSADES', 'CITE DES ARTS', 'ATTOBAN', 'PANORAMA', 'BONOUMIN',
    'ABATTA', 'MERMOZ', 'PALMERAIE',
    # ABOBO
    'ABOBO GARE', 'ABOBO N\'DOTTRE', 'ABOBO BAOULÉ', 'ABOBO DERRIERE RAIL',
    'PK 18', 'PK 24', 'AGBAN', 'CLOUETCHA', 'WILLIAMSVILLE', 'N\'DOTTRE',
    'TRAINOU', 'AVOCATIER', 'SAGBE',
    # ADJAME
    'ADJAME BINGERVILLE', 'ADJAME COMMERCE', 'ADJAME WILLIAMSVILLE',
    'BROMAKOTE', 'WASHINGTON', 'MANGUIERS', 'LIBERTY', '220 LOGEMENTS',
    # YOPOUGON
    'YOPOUGON GESCO', 'YOPOUGON MAROC', 'YOPOUGON SELMER',
    'YOPOUGON ZONE INDUSTRIELLE', 'ZONE INDUSTRIELLE DE YOPOUGON',
    'YOPOUGON BANCO', 'YOPOUGON ANANERAIE', 'YOPOUGON KOWEÏT',
    'YOPOUGON NIANGON', 'YOPOUGON FICGAYO', 'YOPOUGON LAVAGE',
    'SODEFOR', 'BANCO', 'BATIM', 'ANANERAIE', 'COOPEC', 'GESCO',
    'CARREFOUR CHU', 'KM 17', 'MANUTENTION', 'FERME SIDIBE',
    # MARCORY
    'ZONE 4', 'BIETRY', 'MARCORY RESIDENTIELL', 'ANOUMABO',
    'ZONE INDUSTRIELLE', 'SAN PEDRO', 'GONZAGUEVILLE',
    # PORT BOUET
    'GONZAGUE', 'TERRE ROUGE', 'ADJOUFFOU', 'VRIDI', 'PORT BOUET CENTRE',
    'PETIT BASSAM', 'KOUMASSI', 'AEROPORT',
    # TREICHVILLE
    'TREICHVILLE', 'PORT D\'ABIDJAN',
    # KOUMASSI
    'KOUMASSI REMBLAI', 'KOUMASSI COMMERCE',
    # PLATEAU
    'PLATEAU', 'CENTRE VILLE',
    # ATTECOUBO
    'ATTECOUBO', 'BANCO NORD',
    # EXTENSIONS
    'SONGON KASSEMBLE', 'SONGON AGBAN',
]

# Villes de Côte d'Ivoire (hors Abidjan)
VILLES_CI = [
    'ABENGOUROU', 'ABOISSO', 'ADZOPE', 'AGBOVILLE', 'ALEPE',
    'BIANKOUMA', 'BOCANDA', 'BONDOUKOU', 'BONGOUANOU', 'BOUAKE',
    'BOUNDIALI', 'DABOU', 'DALOA', 'DANANE', 'DAOUKRO',
    'DIMBOKRO', 'DIVO', 'DUEKOUE', 'FERKESSEDOUGOU',
    'GRAND BASSAM', 'GRAND LAHOU', 'GAGNOA', 'GUIGLO',
    'ISSIA', 'JACQUEVILLE', 'KATIOLA', 'KORHOGO',
    'MAN', 'MANKONO', 'MBENGUE', 'MINIGNAN',
    'ODIENNE', 'OUME', 'SAN PEDRO', 'SASSANDRA',
    'SEGUELA', 'SIKENSI', 'SOUBRE', 'TABOU',
    'TIASSALE', 'TIEBISSOU', 'TINGRELA', 'TOUBA',
    'TOUMODI', 'VAVOUA', 'YAMOUSSOUKRO', 'ZUENOULA',
    'GRAND BEREBY', 'DIDIEVI', 'AGOU', 'BETTIE',
    'CECHI', 'HIRE', 'LAKOTA', 'MEAGUI',
    'TAABO', 'TORTIYA', 'FRESCO', 'GUEYO',
    'BUYO', 'GNAGOYA', 'BANGOLO', 'LOGOUALE',
    'ZOUAN-HOUNIEN', 'BEOUMI', 'BOTRO', 'SAKASSOU',
    'SINFRA', 'ZOUKOUGBEU', 'GUITRY', 'NIABLE',
    'TANDA', 'TRANSUA', 'NASSIAN', 'BOUNA',
    'DOROPO', 'TEHINI', 'SANDEGUE', 'GRABO',
    'SAMATIGUILA', 'KORO', 'BLOLEO', 'ZIKISSO',
    'KOUSSIKRO', 'AGNIBILEKRO', 'NIAKARAMADOUGOU',
    'DABAKALA', 'ARRAH', 'BOUAFLE', 'ZUENNOULA',
    'DIKODOUGOU', 'SINEMATIALI', 'TAFIRE',
    # Villages/localités proches de Dabou
    'SASSAKO', 'LOPOU', 'TOUPAH', 'AHOUANOU',
    'BACANDA', 'EBOUNOU', 'TOUKOUZOU', 'ATTOUTOU',
    # Villages/localités Abidjan périphérie
    'SONGON KASSEMBLE', 'SONGON AGBAN', 'BROFODOUME',
    'AKOUPÉ', 'AGOU', 'ANNEPÉ', 'ASSIKOI',
    'BECEDI-BRIGNAN', 'YAKASSE-ME', 'AFFERY',
    'BÉCOUÉFIN', 'ABOISSO-COMOE', 'ALLOSSO',
    'DANGUIRA', 'YAKASSE-ATTOBROU', 'ABONGOUA',
    # Autres localités fréquentes dans les rapports CIE
    'YOMIAN', 'BONDOUKOU', 'ODAYA', 'MOUSSAGUI', 'DIMANDOUGOU',
    'KATIANI', 'BODONON', 'FOROGUDA', 'BARARDON',
    'LELEBE', 'BONIKRO', 'KOHIBA', 'BAOULEKRO',
    'DUALLA', 'BOBBY', 'FRONAN', 'PETIONARA',
    'KATIONON', 'OUREGUEKAHA', 'TAGADI', 'SOROBANGO',
    'MAFIBLE', 'GBEUNTA', 'YOCOBOUET',
    'GRAND-BEREBY', 'SAN-PEDRO', 'M\'BENGUE', 'MBENGUE',
]

# Ensemble complet pour recherche rapide
ALL_LOCATIONS = set(COMMUNES_ABIDJAN + QUARTIERS_ABIDJAN + VILLES_CI)

def split_known_locations(text):
    """Insère des virgules entre des lieux connus qui se suivent sans séparateur.
    Ex: 'DABOU SASSAKO' -> 'DABOU, SASSAKO'
    Ne sépare pas les lieux composés connus: 'RIVIERA PALMERAIE', 'YOPOUGON ZONE INDUSTRIELLE'
    """
    all_locs = sorted(ALL_LOCATIONS, key=len, reverse=True)
    result = text.upper()

    for loc in all_locs:
        if len(loc) < 4:
            continue
        idx = result.find(loc)
        while idx != -1:
            after = result[idx + len(loc):]
            if after.startswith(' ') and not after.startswith(', '):
                after_stripped = after.lstrip()
                for loc2 in all_locs:
                    if len(loc2) < 4 or loc2 == loc:
                        continue
                    if after_stripped.startswith(loc2):
                        # Ne pas séparer si loc + loc2 forme un lieu composé connu
                        combined = loc + ' ' + loc2
                        if combined not in ALL_LOCATIONS:
                            pos = idx + len(loc)
                            result = result[:pos] + ',' + result[pos:]
                        break
            idx = result.find(loc, idx + len(loc) + 2)

    return result

def find_location_in_text(text):
    """Cherche un lieu connu dans le texte - priorité commune/ville sur quartier/village."""
    text_upper = text.upper()
    
    # 1. Chercher d'abord une commune d'Abidjan (priorité absolue)
    for loc in sorted(COMMUNES_ABIDJAN, key=len, reverse=True):
        pattern = r'(?<![A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ])' + re.escape(loc) + r'(?![A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ])'
        if re.search(pattern, text_upper):
            return loc
    
    # 2. Chercher une ville CI principale (chefs-lieux de département)
    villes_principales = [
        'ABIDJAN', 'YAMOUSSOUKRO', 'BOUAKE', 'DALOA', 'KORHOGO',
        'SAN PEDRO', 'ABENGOUROU', 'ABOISSO', 'ADZOPE', 'AGBOVILLE',
        'ALEPE', 'BIANKOUMA', 'BOCANDA', 'BONDOUKOU', 'BONGOUANOU',
        'BOUNDIALI', 'DABOU', 'DANANE', 'DAOUKRO', 'DIMBOKRO',
        'DIVO', 'DUEKOUE', 'FERKESSEDOUGOU', 'GRAND BASSAM',
        'GRAND LAHOU', 'GAGNOA', 'GUIGLO', 'ISSIA', 'JACQUEVILLE',
        'KATIOLA', 'MAN', 'MANKONO', 'MBENGUE', 'MINIGNAN',
        'ODIENNE', 'OUME', 'SASSANDRA', 'SEGUELA', 'SIKENSI',
        'SOUBRE', 'TABOU', 'TIASSALE', 'TIEBISSOU', 'TINGRELA',
        'TOUBA', 'TOUMODI', 'VAVOUA', 'ZUENOULA', 'GRAND BEREBY',
        'MEAGUI', 'TAABO', 'GUEYO', 'BUYO', 'BANGOLO',
        'BEOUMI', 'BOTRO', 'SAKASSOU', 'SINFRA', 'GUITRY',
        'NIABLE', 'TANDA', 'BOUNA', 'DOROPO', 'GRABO',
        'SAMATIGUILA', 'KORO', 'AGNIBILEKRO', 'NIAKARAMADOUGOU',
        'DABAKALA', 'ARRAH', 'BOUAFLE', 'ZUENNOULA', 'DIKODOUGOU',
        'SINEMATIALI', 'TAFIRE', 'FRESCO', 'HIRE', 'LAKOTA',
        'AGNIBILEKRO', 'BETTIE', 'TRANSUA', 'NASSIAN', 'SANDEGUE',
        'TORTIYA', 'LOGOUALE', 'DIDIEVI', 'CECHI', 'AGOU', 'DIMANDOUGOU',
        'DJEBONOUA', 'MOLONOUBLE', 'TIEPLE', 'MBRAKRO', 'BOUNDA', 'APKASSANOU',
        'BROBO', 'BAMORO', 'TOLLAKOUDIOKRO', 'GONFREVILLE', 'BEAUFORT',
        'ZAHAKRO', 'KPOUSSOUSSOU', 'LOGBAKRO', 'ATTIEGOUAKRO', 'GROUMINAKRO',
        'KAHANKRO', 'AGONDA', 'DJEKANOU', 'KOKOUMBO', 'MOSSIKRO', 'BINVANA',
        'ASSOUNVOUE', 'NZASSA', 'KODOUBO', 'ADAHOU', 'ASSEBOUKRO', 'TRIANIKRO',
        'TIEMELE-ANDOKRO', 'ABIDJI',
    ]
    for loc in sorted(villes_principales, key=len, reverse=True):
        pattern = r'(?<![A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ])' + re.escape(loc) + r'(?![A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ])'
        if re.search(pattern, text_upper):
            return loc
    
    # 3. Chercher un quartier Abidjan
    for loc in sorted(QUARTIERS_ABIDJAN, key=len, reverse=True):
        pattern = r'(?<![A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ])' + re.escape(loc) + r'(?![A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ])'
        if re.search(pattern, text_upper):
            return loc
    
    # 4. Chercher n'importe quel lieu dans la base
    for loc in sorted(VILLES_CI, key=len, reverse=True):
        if len(loc) < 5:
            continue
        pattern = r'(?<![A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ])' + re.escape(loc) + r'(?![A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ])'
        if re.search(pattern, text_upper):
            return loc
    
    return None


TEMPLATES_BY_TYPE = {
    'infos_reseaux': {
        'pylone_aerial': [1, 2],        # pylône aérien, ligne HTA
        'technicien_nuit': [3],          # technicien poteau nuit/coucher
        'grimpeurs_ht': [4],             # grimpeurs pylône haute tension
        'poteaux_terrain': [5, 16],       # poteaux terrain / zone rurale
        'cables_souterrains': [6],       # câbles souterrains endommagés
        'eclairage_public': [7],         # éclairage public / route
    },
    'travaux_reseaux': {
        'technicien_transfo': [8],       # technicien transformateur couleur
        'poste_ht_couleur': [9],         # techniciens poste HT couleur
        'cables_nb': [10],               # câbles/transformateur N&B
    },
    'travaux_programmes': {
        'poteaux_couleur': [11],         # poteaux terrain couleur
        'pylone_techniciens_nb': [12],   # techniciens pylône N&B
        'technicien_poteau_harnais': [13], # technicien poteau + harnais
        'cables_transfo_nb': [14, 16],   # câbles transformateur N&B
    }
}

# ── Mots-clés pour sélection du type de vignette ──────────────────────────────
KEYWORDS_INFOS = [
    'incident', 'déclenchement', 'hors tension', 'perturbé', 'perturbée',
    'conducteurs rompus', 'support cassé', 'tfo avarié', 'parafoudre',
    'défaut câble', 'câble souterrain', 'bretelles cassées', 'manivelle cassée',
    'réseau souterrain', 'rompu', 'avarié', 'recherche de défaut',
    'baisse de tension', 'dysfonctionnement', 'debut incident',
    'reprise partielle', 'postes restent hors tension', 'postes qui restent'
]

KEYWORDS_TRAVAUX_RESEAUX = [
    'manœuvres d\'exploitation', 'manoeuvres d\'exploitation', 'maintenance', 'défaut de câbles survenu',
    'défaut câble survenu', 'travaux de maintenance', 'mise en conformité',
    'poste source', 'debut nip', 'début nip', 'nip ht', 'remplacement cable',
    'remplacement câble', 'début de la nip', 'travaux htb', 'travaux hta',
    'travaux au poste', 'travaux sur le poste', 'travaux sur la ligne',
    'travaux sur le réseau', 'travaux sur le départ',
]

KEYWORDS_TRAVAUX_PROGRAMMES = [
    'travaux programmés', 'travaux de pose', 'pose de coffret',
    'coffret actuator', 'mise en conformité des cellules', 'travaux mise en conformite'
]

# ── Mots-clés pour sélection de la photo ──────────────────────────────────────
KEYWORDS_PHOTO = {
    'cables_souterrains': ['souterrain', 'câble souterrain', 'neutre', 'réseau souterrain', 'rompu', 'alu hge', 'défaut câble souterrain', 'câbles souterrains'],
    'eclairage_public': ['éclairage public', 'lampadaire', 'route'],
    'grimpeurs_ht': ['haute tension', 'pylône ht', 'ligne ht', 'grimpeur'],
    'poteaux_terrain': ['rurale', 'village', 'localité', 'zone rurale', 's/p ', 'sous-station'],
    'technicien_nuit': ['nuit', 'coucher', '20h', '21h', '22h', '23h', '00h', '01h', '02h', '03h', '04h', '05h'],
    'technicien_transfo': ['transformateur', 'tfo', 'transfo', 'poste', 'manivelle'],
    'poste_ht_couleur': ['poste ht', 'poste source', 'poste alimentant', 'poste d\'alimentation', '2plateaux', 'plateaux'],
    'cables_nb': ['câbles', 'câble', 'défaut de câbles'],
    'pylone_aerial': [],  # défaut
}

# ── Statuts ───────────────────────────────────────────────────────────────────
STATUT_EN_COURS = "ÉQUIPES MOBILISÉES, TRAVAUX ET REPRISE EN COURS"
STATUT_PROGRESSIVE = "ÉQUIPES MOBILISÉES , TRAVAUX EN COURS - REPRISE PROGRESSIVE"
STATUT_HEURE = "ÉQUIPES MOBILISÉES , TRAVAUX EN COURS - REPRISE PRÉVUE À {heure}"

# ── Formulations texte principal ──────────────────────────────────────────────
FORMULATIONS = {
    'incident_ligne': "EN RAISON D'UN INCIDENT SUR LA LIGNE D'ALIMENTATION ÉLECTRIQUE {lieu}, LA FOURNITURE D'ÉLECTRICITÉ EST ACTUELLEMENT PERTURBÉE.",
    'incident_reseau': "SUITE À UN INCIDENT SURVENU SUR LE RÉSEAU ÉLECTRIQUE {lieu}, LA FOURNITURE D'ÉLECTRICITÉ EST ACTUELLEMENT PERTURBÉE.",
    'incident_survenu': "EN RAISON D'UN INCIDENT SURVENU SUR LA LIGNE D'ALIMENTATION ÉLECTRIQUE {lieu}, LA FOURNITURE DE L'ÉLECTRICITÉ EST PERTURBÉE.",
    'incident_poste': "EN RAISON D'UN INCIDENT SURVENU SUR UN POSTE D'ALIMENTATION ÉLECTRIQUE {lieu}, LA FOURNITURE DE L'ÉLECTRICITÉ EST ACTUELLEMENT PERTURBÉE.",
    'defaut_cable': "EN RAISON D'UN DÉFAUT DE CÂBLES SURVENU SUR LA LIGNE D'ALIMENTATION ÉLECTRIQUE {lieu}, LA FOURNITURE DE L'ÉLECTRICITÉ EST PERTURBÉE.",
    'defaut_cable_sout': "EN RAISON D'UN DÉFAUT CÂBLE SOUTERRAIN SURVENU SUR LA LIGNE D'ALIMENTATION ÉLECTRIQUE {lieu}, LA FOURNITURE D'ÉLECTRICITÉ EST ACTUELLEMENT PERTURBÉE.",
    'manoeuvre': "EN RAISON DE MANOEUVRE EN COURS SUR UN POSTE DE LA LIGNE D'ALIMENTATION ÉLECTRIQUE {lieu}, LA FOURNITURE DE L'ÉLECTRICITÉ EST PERTURBÉE.",
    'travaux_pose': "EN RAISON DE TRAVAUX DE POSE DE COFFRET ACTUATOR SUR LA LIGNE D'ALIMENTATION ÉLECTRIQUE {lieu}, LA FOURNITURE DE L'ÉLECTRICITÉ EST PERTURBÉE.",
    'travaux_maintenance': "DANS LE CADRE DE TRAVAUX DE MAINTENANCE AU POSTE ALIMENTANT QUELQUES ZONES {lieu}, LA FOURNITURE D'ÉLECTRICITÉ EST PERTURBÉE.",
    'perturbations': "QUELQUES PERTURBATIONS RESSENTIES SUR LE RÉSEAU ÉLECTRIQUE {lieu}.",
}

# ─────────────────────────────────────────────────────────────────────────────
# FONCTIONS PRINCIPALES
# ─────────────────────────────────────────────────────────────────────────────

def parse_date(text):
    """Extrait et formate la date depuis le texte input."""
    # Chercher patterns date
    patterns = [
        r'(\d{2})/(\d{2})/(\d{4})',
        r'(\d{2})/(\d{2})/(\d{2})',
        r'le\s+(\d{2})/(\d{2})/(\d{2,4})',
        r'Date\s*:\s*(\d{2})/(\d{2})/(\d{4})',
        r'(\d{2})\.(\d{2})\.(\d{4})',
    ]
    
    jours_fr = ['', 'LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE']
    mois_fr = ['', 'JANVIER', 'FÉVRIER', 'MARS', 'AVRIL', 'MAI', 'JUIN',
               'JUILLET', 'AOÛT', 'SEPTEMBRE', 'OCTOBRE', 'NOVEMBRE', 'DÉCEMBRE']
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            day, month, year = match.groups()
            day, month = int(day), int(month)
            year = int(year)
            if year < 100:
                year += 2000
            try:
                dt = datetime(year, month, day)
                jour_semaine = jours_fr[dt.weekday() + 1]
                return f"{jour_semaine} {day} {mois_fr[month]} {year}"
            except:
                pass
    
    # Aujourd'hui par défaut
    dt = datetime.now()
    return f"{jours_fr[dt.weekday()+1]} {dt.day} {mois_fr[dt.month]} {dt.year}"


def detect_type(text):
    """Détecte le type de vignette depuis le texte input."""
    text_lower = text.lower()

    # Travaux programmés en premier (NIP, travaux planifiés)
    for kw in KEYWORDS_TRAVAUX_PROGRAMMES:
        if kw in text_lower:
            return 'travaux_programmes'

    # Chercher "travaux" dans le champ Évènement spécifiquement
    event_match = re.search(r'[ée]v[eè]nement\s*:\s*([^\n]+)', text_lower)
    if event_match:
        event_text = event_match.group(1)
        if any(k in event_text for k in ['travaux', 'manœuvres d\'exploitation', 'manoeuvres d\'exploitation', 'nip', 'maintenance']):
            return 'travaux_reseaux'
        if any(k in event_text for k in ['incident', 'déclenchement', 'hors tension']):
            return 'infos_reseaux'

    # Infos réseaux — vérifier avant travaux si incident/reprise partielle détecté
    for kw in ['déclenchement', 'reprise partielle', 'postes restent hors tension',
               'postes qui restent', 'debut incident']:
        if kw in text_lower:
            return 'infos_reseaux'

    # Travaux réseaux
    for kw in KEYWORDS_TRAVAUX_RESEAUX:
        if kw in text_lower:
            return 'travaux_reseaux'

    # Infos réseaux (défaut)
    return 'infos_reseaux'


def detect_photo_context(text, vignette_type):
    """Détecte le contexte pour choisir la bonne photo."""
    text_lower = text.lower()
    
    if vignette_type == 'infos_reseaux':
        for ctx, keywords in KEYWORDS_PHOTO.items():
            if ctx in TEMPLATES_BY_TYPE['infos_reseaux']:
                for kw in keywords:
                    if kw in text_lower:
                        return ctx
        return 'pylone_aerial'  # défaut
    
    elif vignette_type == 'travaux_reseaux':
        for ctx, keywords in KEYWORDS_PHOTO.items():
            if ctx in TEMPLATES_BY_TYPE['travaux_reseaux']:
                for kw in keywords:
                    if kw in text_lower:
                        return ctx
        # Défaut selon cause
        if any(k in text_lower for k in ['câble', 'câbles', 'défaut de câble']):
            return 'cables_nb'
        if any(k in text_lower for k in ['poste', '2plateaux', 'plateaux']):
            return 'poste_ht_couleur'
        return 'technicien_transfo'
    
    else:  # travaux_programmes
        for ctx, keywords in KEYWORDS_PHOTO.items():
            if ctx in TEMPLATES_BY_TYPE['travaux_programmes']:
                for kw in keywords:
                    if kw in text_lower:
                        return ctx
        return 'poteaux_couleur'


def select_template(vignette_type, photo_context):
    """Choisit aléatoirement un template parmi tous les templates du type."""
    # Récupérer tous les templates du type sans distinction de contexte
    all_options = []
    for v in TEMPLATES_BY_TYPE.get(vignette_type, {}).values():
        all_options.extend(v)
    if not all_options:
        all_options = [1]
    return random.choice(all_options)


def get_article(lieu):
    """Retourne l'article/préposition correct selon le lieu."""
    lieu_upper = lieu.upper().strip()
    # DES + chiffre ou commence par un chiffre
    if re.match(r'^\d', lieu_upper):
        return 'DES'
    # DE LA + noms féminins connus
    feminine = ['RIVIERA', 'ZONE', 'ROUTE', 'COTE']
    if any(lieu_upper.startswith(f) for f in feminine):
        return 'DE LA'
    # D' + voyelle
    if lieu_upper[0] in 'AEIOUÀÂÄÉÈÊËÎÏÔÙÛÜ':
        return "D'"
    # DE par défaut
    return 'DE'


def extract_lieu(text):
    """Extrait le lieu géographique (poste source / quartier) depuis le texte."""
    text_upper = text.upper()

    # 0.1 Pattern @DRX Début incident/NOM (sans tiret)
    match = re.search(r'@DR[A-Z]+\s+D[ÉE]BUT\s+(?:INCIDENT|NIP)[/\s]+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ\s\-\']+?)(?:\s*\d|\s*\n|$)', text_upper)
    if match:
        lieu = match.group(1).strip()
        if 2 < len(lieu) < 30:
            return lieu

    # 0. Pattern @DRX- Début incident/ LIEU ou @DRX-Début Incident/LIEU
    match = re.search(r'@DR[A-Z]+[-–]\s*(?:D[ÉE]BUT\s+(?:INCIDENT|NIP)\s*(?:HT|BT)?\s*[/\-]\s*)([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ\s\-\']+?)(?:\s*\n|\s*\d|\s*[,.]|$)', text_upper)
    if match:
        lieu = match.group(1).strip()
        if 2 < len(lieu) < 30:
            return lieu

    # 1. Poste source explicite: "au poste source de NOM"
    match = re.search(r'POSTE\s+SOURCE\s+DE\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ\s\-\']+?)(?:\s*[,.\n]|\s+\d|\s*$)', text_upper)
    if match:
        lieu = match.group(1).strip()
        if 2 < len(lieu) < 40:
            return lieu

    # 1.4 Pattern "Départ NOM." ou "Départ NOM\n" -> lieu propre sans zones
    match = re.search(r'D[ÉE]PART\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ\s\-\'0-9]+?)[.\n]', text_upper)
    if match:
        lieu = match.group(1).strip()
        lieu = re.sub(r'^(\d+\s*KV\s+|HTA\s+|HTB\s+|\*)', '', lieu).strip()
        if 2 < len(lieu) < 30:
            paren_match = re.search(r'\(([^)]+)\)', text_upper, re.DOTALL)
            if paren_match:
                paren_text = paren_match.group(1)
                # Chercher d'abord VILLE NOM dans les parenthèses
                ville_match = re.search(r'VILLE\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ\s\-\']+?)(?:\s+ET|\s*,|\s*$)', paren_text)
                if ville_match:
                    return ville_match.group(1).strip()
                # Sinon chercher lieu connu en ignorant S/P et ce qui suit
                paren_clean = re.sub(r'\*?S/P\s+[A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ/]+', '', paren_text)
                paren_clean = re.sub(r',.*', '', paren_clean)  # Prendre seulement le premier élément
                loc_in_paren = find_location_in_text(paren_clean)
                if loc_in_paren:
                    return loc_in_paren
            return lieu

    # 1.5 Pattern "Départ NOM (" ou "départ NOM impactant" -> lieu depuis nom du départ
    match = re.search(r'D[ÉE]PART\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ\s\-\'0-9]+?)\s+(?:IMPACTANT|DONT)', text_upper)
    if match:
        lieu = match.group(1).strip()
        lieu = re.sub(r'^(\d+\s*KV\s+|HTA\s+|HTB\s+|\*)', '', lieu).strip()
        if 2 < len(lieu) < 30:
            return lieu

    match = re.search(r'D[ÉE]CLENCHEMENT\s+D[ÉE]PART\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ\s\-\'0-9]+?)\s*\(', text_upper)
    if match:
        lieu = match.group(1).strip()
        lieu = re.sub(r'^(\d+\s*KV\s+|\d+\s*K\s+|HTA\s+|HTB\s+|\*)', '', lieu).strip()
        if 2 < len(lieu) < 30:
            return lieu

    match = re.search(r'D[ÉE]PART\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ\s\-\'0-9]+?)\s*\(', text_upper)
    if match:
        lieu = match.group(1).strip()
        lieu = re.sub(r'^(\d+\s*KV\s+|\d+\s*K\s+|HTA\s+|HTB\s+|\*|33KV\s+|15KV\s+)', '', lieu).strip()
        if 2 < len(lieu) < 30:
            return lieu

    # 1.9 Chercher commune/quartier connu dans les parenthèses
    paren_match = re.search(r'\(([^)]+)\)', text_upper)
    if paren_match:
        paren_text = re.sub(r'\*?S/P\s+[A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ]+', '', paren_match.group(1))
        loc_in_paren = find_location_in_text(paren_text)
        if loc_in_paren:
            return loc_in_paren

    # 2. "PS NOM :" -> le PS est le lieu géographique
    match = re.search(r'\*?PS\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ\s\-\']+?)\s*[:\-]', text_upper)
    if match:
        lieu = match.group(1).strip()
        if 2 < len(lieu) < 30:
            return lieu

    # 2.5 NIP sur départ NOM - nettoyer préfixes techniques (15KV, HTA, etc.)
    match = re.search(r'NIP\s+\d+\s+SUR\s+LE\s+D[ÉE]PART\s+(?:\d+\s*KV\s+)?([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ\s\-\'0-9]+?)(?:\s*[.,\n]|\s+COUPE|\s+POUR)', text_upper)
    if match:
        depart = match.group(1).strip()
        depart = re.sub(r'^(\d+\s*KV\s+|HTA\s+|HTB\s+)', '', depart).strip()
        # Chercher d'abord dans la base géo pour avoir le vrai lieu
        loc = find_location_in_text(text_upper)
        if loc:
            return loc
        if 2 < len(depart) < 30:
            return depart

    # 2.6 Chercher dans la base géographique CI - commune/ville prioritaire
    loc = find_location_in_text(text_upper)
    if loc:
        return loc

    # 3. "départ NOM (LIEU...)" avec point
    match = re.search(r'D[ÉE]PART\s+[A-Z0-9\s\-\']+\.\s*\(([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][^)]+)\)', text_upper)
    if match:
        zones_text = match.group(1).strip()
        first = zones_text.split(',')[0].strip()
        words = first.split()
        if words:
            return words[0]

    # 4. "départ NOM (LIEU...)" sans point
    match = re.search(r'D[ÉE]CLENCHEMENT\s+D[ÉE]PART\s+[A-Z0-9\s\-\']+\(([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][^)]+)\)', text_upper)
    if match:
        zones_text = match.group(1).strip()
        first = zones_text.split(',')[0].strip()
        words = first.split()
        if words:
            return words[0]

    # 5. Zones concernées -> extraire quartier principal
    match = re.search(r'ZONES?\s+CONCERN[ÉE]ES?\s*:\s*([^\n]+)', text_upper)
    if match:
        zones = match.group(1).strip()
        first_zone = zones.split(',')[0].strip()
        words = first_zone.split()
        if words:
            return ' '.join(words[:2]) if len(words) > 1 and len(words[0]) < 5 else words[0]

    # 6. "réseau électrique de NOM"
    match = re.search(r'R[ÉE]SEAU\s+[ÉE]LECTRIQUE\s+DE\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ\s\-\']+?)(?:\s*[,.]|\s+LA\s)', text_upper)
    if match:
        lieu = match.group(1).strip()
        if 2 < len(lieu) < 40:
            return lieu

    # 7. Départ simple comme dernier recours
    match = re.search(r'D[ÉE]PART\s+\*?([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ\s\-\'0-9]+?)(?:\s*[,.(:\n]|\s+AU\s|\s+DE\s|\s+D[ÉE])', text_upper)
    if match:
        lieu = re.sub(r'\s+\d+$', '', match.group(1)).strip()
        if 2 < len(lieu) < 30:
            return lieu

    return "LA ZONE"


def clean_zones(zones):
    """Nettoie les zones: supprime articles/préfixes génériques, préserve désignations officielles."""
    zones = zones.strip()
    # Supprimer UNIQUEMENT les préfixes génériques non informatifs
    zones = re.sub(r'^(LES\s+LOCALIT[ÉE]S\s+DE\s+|LES\s+ZONES?\s+DE\s+|DE\s+LA\s+(?!VILLE|COMMUNE)|DES\s+|D[\']\s*(?=[A-Z])|DANS\s+LA\s+ZONE\s+DE\s+)', '', zones, flags=re.IGNORECASE)
    zones = re.sub(r'\s+', ' ', zones).strip()
    # YOP -> YOPOUGON (seulement si pas déjà YOPOUGON)
    zones = re.sub(r'\bYOP\b(?!OUGON)', 'YOPOUGON', zones, flags=re.IGNORECASE)
    # DS/P -> S/P
    zones = re.sub(r'\bDS/P\s+', 'S/P ', zones, flags=re.IGNORECASE)
    # NL = Non loin de
    zones = re.sub(r'\bNL\s+DE\s+', 'NON LOIN DE ', zones, flags=re.IGNORECASE)
    zones = re.sub(r'\bNL\s+', 'NON LOIN DE ', zones, flags=re.IGNORECASE)
    # Normaliser séparateurs
    zones = re.sub(r'(?<!S)/(?!P)', ', ', zones)  # N/L -> N, L mais préserve S/P
    # Supprimer NOM_VILLE ( en début seulement si pas suivi de VILLE
    zones = re.sub(r'^(?!VILLE\s)[A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ]+\s*\(', '', zones, flags=re.IGNORECASE)
    zones = re.sub(r'[;,]\s*', ', ', zones)
    zones = re.sub(r'\s*ET\s+LOCALIT[EÉ]ES?\s+RATTACH[EÉ]ES?', '', zones, flags=re.IGNORECASE)
    zones = re.sub(r'\s*\)', '', zones)
    zones = re.sub(r'^ET\s+', '', zones.strip())
    zones = zones.rstrip(', ')
    # Supprimer points de suspension
    zones = re.sub(r'\.{2,}', '', zones).strip()
    zones = zones.rstrip('.')
    zones = zones.upper()
    # Séparer les lieux connus qui se suivent sans virgule (ex: DABOU SASSAKO -> DABOU, SASSAKO)
    zones = split_known_locations(zones)
    # Supprimer les éléments d'une seule lettre (ex: "N" venant de N/L)
    parts = [p.strip() for p in zones.split(',')]
    # Remplacer S/P par SOUS-PRÉFECTURE DE
    import re as _re
    cleaned_parts = []
    for p in parts:
        p = p.strip().strip('*').strip()

        # S/P NOM/NOM2 -> SOUS-PRÉFECTURE DE NOM, NOM2
        def replace_sp(m):
            noms = m.group(1).split('/')
            return ', '.join('SOUS-PRÉFECTURE DE ' + n.strip() for n in noms if n.strip())
        p = _re.sub(r'\*?S/P\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜA-Za-z/\-]+)', replace_sp, p)
        p = p.strip()
        cleaned_parts.append(p)
    # Aplatir les virgules internes
    flat = []
    for p in cleaned_parts:
        for sub in p.split(','):
            sub = sub.strip()
            if len(sub) > 2:
                flat.append(sub)
    parts = flat
    # Supprimer doublons tout en préservant l'ordre
    seen = []
    for p in parts:
        if p not in seen:
            seen.append(p)
    return ', '.join(seen)


def extract_zones(text):
    """Extrait les zones impactées."""
    text_upper = text.upper()
    
    # Pattern: "Zones concernées : NOM"
    match = re.search(r'ZONES?\s+CONCERN[ÉE]ES?\s*:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\nPOINT|\nSMS|\nDUR[ÉE]E|$)', text_upper, re.DOTALL)
    if match:
        zones = match.group(1).strip()
        zones = re.sub(r'\s+', ' ', zones)
        return clean_zones(zones)
    
    # Pattern: "SOUS-PRÉFECTURES DE NOM, NOM sont hors tension"
    match = re.search(r'SOUS-PR[ÉE]FECTURES?\s+DE\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][^.\n]+?)\s*(?:,\s*ET\s+LES\s+LOCALIT|SONT\s+HORS|ET\s+LES\s+LOCALIT|HORS\s+TENSION)', text_upper)
    if match:
        zones = match.group(1).strip()
        # Reformater: ZAKOGBEU, ZAIBO -> SOUS-PRÉFECTURE DE ZAKOGBEU, SOUS-PRÉFECTURE DE ZAIBO
        parts = [p.strip() for p in re.split(r'[,;]', zones) if p.strip()]
        formatted = ', '.join('SOUS-PRÉFECTURE DE ' + p for p in parts)
        return formatted

    # Pattern: "postes hors tension dans la zone NOM"
    match = re.search(r'(?:POSTE[S]?\s+HORS\s+TENSION\s+DANS\s+(?:LA\s+ZONE|LE\s+VILLAGE|LES?\s+ZONE[S]?)\s+)([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][^\n.]+)', text_upper)
    if match:
        return clean_zones(match.group(1).strip())
    
    # Pattern: "dans la zone NOM, NOM2..."
    match = re.search(r'DANS\s+(?:LA\s+ZONE\s+DE\s+|LA\s+ZONE\s+|LE\s+VILLAGE\s+|LA\s+LOCALIT[ÉE]\s+)([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][^\n]+?)(?:\s+POUR\s+TRAVAUX|\s+POUR\s+MISE|\s+POUR\s+REMPLACEMENT|\.\s|\.$|$)', text_upper)
    if match:
        return clean_zones(match.group(1).strip())
    
    # Pattern: "impactant la zone de NOM. NOM. NOM."
    match = re.search(r'IMPACTANT\s+(?:LA\s+ZONE\s+DE\s+|LES\s+ZONES?\s+DE\s+)([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][^*\n]+?)(?:\.\s*\*|\s*\*|$)', text_upper)
    if match:
        zones_raw = match.group(1).strip()
        # Remplacer les points par des virgules pour séparer les zones
        zones_raw = re.sub(r'\.\s+', ', ', zones_raw)
        zones_raw = re.sub(r'\.$', '', zones_raw)
        return clean_zones(zones_raw)

    # Pattern: "@DRX- ... \nLIEU\nPoste..." - le lieu/zone est sur la ligne après le timestamp
    match = re.search(r'@DR[A-Z]+[-–][^\n]*\n\s*\d{2}/\d{2}/\d{4}\s+\d{2}[H:]\d{2}\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][^\n]+)\s*\n\s*POSTE', text_upper)
    if match:
        zone_raw = match.group(1).strip()
        for commune in COMMUNES_ABIDJAN:
            if zone_raw.startswith(commune + ' '):
                zone_raw = zone_raw[len(commune):].strip()
                break
        return clean_zones(zone_raw)

    match = re.search(r'IMPACTANT\s+LES\s+ZONES\s+DE\s+\(([^)]+)\)', text_upper)
    if match:
        return clean_zones(match.group(1).strip())
    
    # Pattern parenthèses dans déclenchement
    match = re.search(r'D[ÉE]CLENCHEMENT\s+[^\(]*\(([^)]+)\)', text_upper)
    if match:
        zones = match.group(1).strip()
        if len(zones) > 3:
            return clean_zones(zones)
    
    # Pattern NIP: "Coupe X postes (refs...) ZONES pour travaux"
    match = re.search(r'COUPE\s+\d+\s+POSTES?\s+\([^)]+\)\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ].+?)(?:\s+POUR\s+TRAVAUX|\s+POUR\s+REMPLACEMENT|\s+POUR\s+MISE)', text_upper, re.DOTALL)
    if match:
        zones = match.group(1).strip()
        zones = re.sub(r'\s+', ' ', zones)
        # Remplacer N/L par rien (abréviation technique "Non Loin")
        zones = re.sub(r'\bN/L\b', '', zones)
        zones = re.sub(r'\bNL\b', '', zones)
        # Supprimer la commune en début si présente
        for commune in COMMUNES_ABIDJAN:
            if zones.upper().startswith(commune + ' '):
                zones = zones[len(commune):].strip()
                break
        # Supprimer doublon de quartier en début (ex: "ANGRE ANGRE 8EME" -> "ANGRE 8EME")
        words = zones.split()
        if len(words) >= 2 and words[0] == words[1]:
            zones = ' '.join(words[1:])
        return clean_zones(zones)


    
    # Pattern: ligne avec date heure puis zone directement (format HT)
    match = re.search(r'\d{2}/\d{2}/\d{4}\s+\d{2}[H:]\d{2}\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][^\n.]+?)(?:\s*\.\s*POSTE|\s*\.\s*C[AÂ]BLE|\s*\.\s*CLIENT|\s*$)', text_upper, re.MULTILINE)
    if match:
        zone = match.group(1).strip()
        if len(zone) > 3:
            return clean_zones(zone)

    return ""


def extract_heure_reprise(text):
    """Extrait l'heure de reprise si présente."""
    text_lower = text.lower()
    
    # "reprise estimée à Xh" ou "reprise probable : Xh"  
    patterns = [
        r'reprise\s+(?:estim[ée]e?|pr[ée]vue?|probable)\s*[à:]\s*(\d{1,2}[h:]\d{0,2})',
        r'reprise\s+probable\s+(\d{1,2}[h:]\d{2})',
        r'reprise\s+probable\s*:\s*(\d{1,2}h\d{0,2})',
        r'heure\s+de\s+reprise\s*:\s*(\d{1,2}[h:]\d{0,2})',
        r'reprise.*?(\d{1,2}h\d{2})',
        r'pour\s+reprise\s+probable\s*[:\s]+(\d{1,2}[h:]\d{2})',
    ]
    for p in patterns:
        match = re.search(p, text_lower)
        if match:
            h = match.group(1).upper().replace(':', 'H')
            # Nettoyer: 17H00 -> 17H00, 17H -> 17H, 17H0 -> 17H
            if h.endswith('H00'):
                h = h[:-2]  # 17H00 -> 17H
            elif h.endswith('H0'):
                h = h[:-1]
            return h
    return None


def detect_statut(text):
    """Détecte le statut bas approprié."""
    text_lower = text.lower()

    # Reprise progressive en priorité (reprise partielle = travaux pas finis)
    if any(k in text_lower for k in ['reprise partielle', 'reprise progressive',
                                      'acheminement du transfo', 'groupe électrogène',
                                      'postes restent hors tension', 'postes qui restent']):
        return STATUT_PROGRESSIVE

    # Heure de reprise précise
    heure = extract_heure_reprise(text)
    if heure:
        return STATUT_HEURE.format(heure=heure)

    return STATUT_EN_COURS


def build_formulation(text, lieu, vignette_type):
    """Construit la formulation du texte principal."""
    text_lower = text.lower()
    
    # Nettoyer le lieu — enlever "LA VILLE DE", "LA LOCALITÉ DE" etc. pour la formulation
    lieu_clean = lieu.upper().strip()
    for prefix in ['LA VILLE DE ', 'LA LOCALITÉ DE ', 'LA LOCALITE DE ', 'LE VILLAGE DE ', 'LA COMMUNE DE ']:
        if lieu_clean.startswith(prefix):
            lieu_clean = lieu_clean[len(prefix):].strip()
            break
    
    article = get_article(lieu_clean)
    lieu_formatted = f"{article} {lieu_clean}"

    if article == "D'":
        lieu_formatted = f"D'{lieu}"
    
    if 'souterrain' in text_lower or 'alu hge' in text_lower:
        formule = FORMULATIONS['defaut_cable_sout']
    elif 'défaut de câbles' in text_lower or 'défaut câble' in text_lower:
        formule = FORMULATIONS['defaut_cable']
    elif any(k in text_lower for k in ['manœuvres d\'exploitation', 'manoeuvres d\'exploitation', 'manœuvres d exploitation', 'manoeuvres d exploitation']):
        formule = FORMULATIONS['manoeuvre']
    elif 'remplacement cable' in text_lower or 'remplacement câble' in text_lower:
        formule = FORMULATIONS['travaux_maintenance']
        lieu_formatted = f"D'{lieu}" if lieu[0] in 'AEIOUÀÂÄÉÈÊËÎÏÔÙÛÜ' else f"DE {lieu}"
    elif 'nip' in text_lower or 'mise en conformité' in text_lower:
        formule = FORMULATIONS['travaux_maintenance']
        lieu_formatted = f"DES {lieu}" if re.match(r'^\d', lieu) else lieu_formatted
    elif 'pose' in text_lower and 'coffret' in text_lower:
        formule = FORMULATIONS['travaux_pose']
    elif 'poste' in text_lower and any(k in text_lower for k in ['abobo', 'adjame', 'williamsville', 'yopougon', 'marcory']):
        formule = FORMULATIONS['incident_poste']
    elif 'réseau électrique' in text_lower:
        formule = FORMULATIONS['incident_reseau']
    elif 'perturbation' in text_lower:
        formule = FORMULATIONS['perturbations']
    else:
        formule = random.choice([FORMULATIONS['incident_ligne'], FORMULATIONS['incident_survenu']])
    
    return formule.format(lieu=lieu_formatted)


def hex_to_rgb(hex_color):
    """Convertit hex en RGB."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def load_font(size):
    """Charge la police Big Noodle Titling."""
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()


def fit_text_in_box(draw, text, box_w, box_h, max_size=60, min_size=20, padding=20):
    """Trouve la taille de police optimale pour que le texte rentre dans la box."""
    for size in range(max_size, min_size - 1, -1):
        font = load_font(size)
        lines = wrap_text(text, font, box_w - padding * 2)
        total_h = len(lines) * (size + 8)
        if total_h <= box_h - padding * 2:
            return font, lines, size
    font = load_font(min_size)
    lines = wrap_text(text, font, box_w - padding * 2)
    return font, lines, min_size


def wrap_text(text, font, max_width):
    """Découpe le texte en lignes selon la largeur max, en respectant les \n."""
    # D'abord séparer par les \n explicites
    paragraphs = text.split('\n')
    all_lines = []

    for paragraph in paragraphs:
        if not paragraph.strip():
            all_lines.append('')
            continue
        words = paragraph.split()
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                bbox = font.getbbox(test_line)
                w = bbox[2] - bbox[0]
            except:
                w = len(test_line) * 20
            if w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    all_lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            all_lines.append(' '.join(current_line))

    return all_lines if all_lines else [text]


def draw_text_in_box(draw, text, box, color, max_font_size=55, min_font_size=18, bold_words=None, underline_words=None, align='left', v_align='center'):
    """Écrit le texte dans une box avec adaptation automatique de la taille."""
    x1, y1, x2, y2 = box
    box_w = x2 - x1
    box_h = y2 - y1
    padding = 18
    
    font, lines, size = fit_text_in_box(draw, text, box_w, box_h, max_font_size, min_font_size, padding)
    line_h = size + 10
    total_h = len(lines) * line_h
    
    if v_align == 'center':
        start_y = y1 + (box_h - total_h) // 2
    else:
        start_y = y1 + padding
    
    rgb_color = hex_to_rgb(color)
    
    for line in lines:
        if align == 'center':
            try:
                bbox = font.getbbox(line)
                tw = bbox[2] - bbox[0]
            except:
                tw = len(line) * size // 2
            x = x1 + (box_w - tw) // 2
        else:
            x = x1 + padding
        
        # Dessiner le texte ligne par ligne
        # Chercher mots à souligner et mettre en gras
        if underline_words:
            draw_line_with_underline(draw, line, x, start_y, font, rgb_color, underline_words)
        else:
            draw.text((x, start_y), line, font=font, fill=rgb_color)
        
        start_y += line_h
    
    return start_y


def draw_line_with_underline(draw, line, x, y, font, color, underline_words):
    """Dessine une ligne de texte avec certains mots soulignés et en gras."""
    words = line.split(' ')
    cursor_x = x
    
    for i, word in enumerate(words):
        word_clean = word.strip('.,;:!')
        is_special = any(uw.upper() in word_clean.upper() for uw in underline_words)
        
        draw.text((cursor_x, y), word, font=font, fill=color)
        
        if is_special:
            try:
                bbox = font.getbbox(word)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                # Soulignement
                draw.line([(cursor_x, y + h + 2), (cursor_x + w, y + h + 2)], fill=color, width=2)
            except:
                pass
        
        try:
            space_bbox = font.getbbox(' ')
            space_w = space_bbox[2] - space_bbox[0]
        except:
            space_w = font.size // 2 if hasattr(font, 'size') else 10
        
        try:
            bbox = font.getbbox(word)
            w = bbox[2] - bbox[0]
        except:
            w = len(word) * 20
        
        cursor_x += w + (space_w if i < len(words) - 1 else 0)


def draw_date(draw, date_text, template_id):
    """Écrit la date sur le template - alignée à gauche sous le titre."""
    font = load_font(42)
    rgb = hex_to_rgb(COLOR_DATE)
    # Alignée à gauche depuis x=545 (début de la partie droite)
    x = 555
    y = 48
    draw.text((x, y - 20), date_text, font=font, fill=rgb)


def get_text_offset(font, text):
    """Retourne l'offset x gauche de la police (peut être négatif)."""
    try:
        bbox = font.getbbox(text)
        return bbox[0]  # offset x gauche
    except:
        return 0


def draw_texte_principal(draw, formulation, lieu, template_id):
    """Écrit le texte principal strictement dans le conteneur blanc."""
    coords = TEMPLATE_COORDS[template_id]
    b = coords['bloc1']
    padding_left = 58   # décalé vers la droite
    padding_other = 28  # haut, bas, droite
    box_x1 = b[0] + padding_left
    box_y1 = b[1] + padding_other
    box_x2 = b[2] - padding_other
    box_y2 = b[3] - padding_other
    box_w = box_x2 - box_x1
    box_h = box_y2 - box_y1

    font, lines, size = fit_text_in_box(draw, formulation, box_w, box_h, 50, 18, padding=0)
    line_h = size + 8
    total_h = len(lines) * line_h
    start_y = box_y1 + max(0, (box_h - total_h) // 2)

    lieu_upper = lieu.upper()
    # Nettoyer le lieu pour le soulignement — enlever "LA VILLE DE" etc.
    for prefix in ['LA VILLE DE ', 'LA LOCALITÉ DE ', 'LA LOCALITE DE ', 'LE VILLAGE DE ', 'LA COMMUNE DE ']:
        if lieu_upper.startswith(prefix):
            lieu_upper = lieu_upper[len(prefix):].strip()
            break
    rgb_normal = hex_to_rgb("#545454")
    rgb_lieu = hex_to_rgb("#000000")

    for line in lines:
        if start_y + line_h > box_y2:
            break
        # Corriger l'offset de la police
        x_offset = get_text_offset(font, line)
        x = box_x1 - x_offset
        if lieu_upper in line.upper():
            draw_line_mixed(draw, line, x, start_y, font, rgb_normal, rgb_lieu, lieu_upper)
        else:
            draw.text((x, start_y), line, font=font, fill=rgb_normal)
        start_y += line_h


def draw_line_mixed(draw, line, x, y, font, color_normal, color_lieu, lieu_upper):
    """Dessine une ligne avec le lieu en couleur différente + souligné."""
    words = line.split(' ')
    cursor_x = x

    # Trouver les mots du lieu
    lieu_words = lieu_upper.split()

    i = 0
    while i < len(words):
        word = words[i]
        word_up = word.upper().strip('.,;:!')
        word_clean = re.sub(r"^(D'|DE |D')", '', word_up)

        # Vérifier si ce mot commence le lieu
        is_lieu_start = False
        lieu_word_count = 0

        if len(lieu_words) == 1:
            if word_up == lieu_words[0] or word_clean == lieu_words[0]:
                is_lieu_start = True
                lieu_word_count = 1
        else:
            check = word_clean if word_clean == lieu_words[0] else word_up
            if check == lieu_words[0] and i + len(lieu_words) <= len(words):
                if all(words[i+j].upper().strip('.,;:!') == lieu_words[j] for j in range(len(lieu_words))):
                    is_lieu_start = True
                    lieu_word_count = len(lieu_words)

        if is_lieu_start and lieu_word_count > 1:
            # Dessiner tous les mots du lieu ensemble avec soulignement continu
            start_x = cursor_x
            for j in range(lieu_word_count):
                w_text = words[i + j]
                draw.text((cursor_x, y), w_text, font=font, fill=color_lieu)
                try:
                    bbox = font.getbbox(w_text)
                    ww = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                except:
                    ww = len(w_text) * 20
                    h = 30
                try:
                    space_bbox = font.getbbox(' ')
                    sw = space_bbox[2] - space_bbox[0]
                except:
                    sw = 10
                cursor_x += ww + (sw if j < lieu_word_count - 1 else 0)
            # Souligner toute la séquence
            end_x = cursor_x
            draw.line([(start_x, y + h + 2), (end_x, y + h + 2)], fill=color_lieu, width=2)
            # Avancer l'espace après le dernier mot
            try:
                space_bbox = font.getbbox(' ')
                cursor_x += space_bbox[2] - space_bbox[0]
            except:
                cursor_x += 10
            i += lieu_word_count
            continue
        elif is_lieu_start:
            # Lieu mono-mot
            draw.text((cursor_x, y), word, font=font, fill=color_lieu)
            try:
                bbox = font.getbbox(word)
                ww = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                draw.line([(cursor_x, y + h + 2), (cursor_x + ww, y + h + 2)], fill=color_lieu, width=2)
            except:
                ww = len(word) * 20
        else:
            draw.text((cursor_x, y), word, font=font, fill=color_normal)
            try:
                bbox = font.getbbox(word)
                ww = bbox[2] - bbox[0]
            except:
                ww = len(word) * 20

        try:
            space_bbox = font.getbbox(' ')
            space_w = space_bbox[2] - space_bbox[0]
        except:
            space_w = 10

        cursor_x += ww + (space_w if i < len(words) - 1 else 0)
        i += 1


def draw_zones_impactees(draw, zones_text, template_id):
    """Écrit les zones impactées sous le label existant."""
    if not zones_text:
        return
    
    coords = TEMPLATE_COORDS[template_id]
    x = coords['zones_x']
    y = coords['zones_y']
    w = coords['zones_w']
    b2 = coords['bloc2']
    h = b2[1] - y - 15
    
    box = (x, y, x + w, y + h)
    
    draw_text_in_box(
        draw, zones_text, box,
        COLOR_ZONES_TEXTE,
        max_font_size=52,
        min_font_size=20,
        v_align='top'
    )


def draw_statut(draw, statut_text, template_id):
    """Écrit le statut dans le conteneur blanc du bas."""
    coords = TEMPLATE_COORDS[template_id]
    b = coords['bloc2']
    pad_x = 30
    pad_y = 8
    box = (b[0] + pad_x, b[1] + pad_y, b[2] - pad_x, b[3] - pad_y)

    lines = statut_text.split('\n')
    statut_clean = '\n'.join(l.strip() for l in lines)

    draw_text_in_box(
        draw, statut_clean, box,
        COLOR_STATUT,
        max_font_size=54,
        min_font_size=28,
        align='center',
        v_align='center'
    )


# ─────────────────────────────────────────────────────────────────────────────
# FONCTION PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────


def normalize_abbreviations(text):
    """Remplace les abréviations courantes."""
    import re
    text = re.sub(r'\bQt\.?\s+', 'Quartiers ', text)
    text = re.sub(r'\bQT\.?\s+', 'Quartiers ', text)
    return text

def split_reports(text):
    """Détecte si le texte contient plusieurs rapports et les sépare."""
    import re
    # Séparer sur @DR ou sur ligne vide + date
    parts = re.split(r'(?=@DR[A-Z])', text.strip())
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) <= 1:
        # Essayer séparation par virgule entre rapports
        parts = re.split(r',\s*(?=@DR[A-Z])', text.strip())
        parts = [p.strip() for p in parts if p.strip()]
    return parts if len(parts) > 1 else [text]

def merge_reports(input_text):
    """
    Si plusieurs rapports sont détectés, fusionne les zones et retourne
    (texte_principal, zones_fusionnees).
    """
    reports = split_reports(input_text)
    if len(reports) <= 1:
        return input_text, None

    # Extraire zones de chaque rapport
    all_zones = []
    for r in reports:
        r = normalize_abbreviations(r)
        z = extract_zones(r)
        if z:
            for part in z.split(','):
                part = part.strip()
                if part and part not in all_zones:
                    all_zones.append(part)

    merged_zones = ', '.join(all_zones) if all_zones else ''
    # Utiliser le premier rapport comme base
    first = normalize_abbreviations(reports[0])
    return first, merged_zones

# Départs dont le nom ne doit pas apparaître comme zone (noms de villes externes)
DEPART_NOM_EXCLUS = {
    'DABOU', 'BASSAM', 'BINGERVILLE', 'ANYAMA', 'AZAGUIE', 'GRAND BASSAM',
    'JACQUEVILLE', 'SONGON',
}

# Départs dont le nom est remplacé par la commune (villes externes utilisées comme nom de départ)
DEPART_NOM_EXCLUS = {
    'DABOU', 'BASSAM', 'BINGERVILLE', 'ANYAMA', 'AZAGUIE', 'GRAND BASSAM',
    'JACQUEVILLE', 'SONGON',
}

# Dictionnaire DEPART -> COMMUNE (source: rattachement HTA nov 2022)
DEPART_COMMUNE = {
    '12 TAG': 'PORT BOUET',
    '2 PLATEAUX': 'ADJAME',
    '271 A': 'COCODY',
    '271 B': 'COCODY',
    '34 TAG': 'PORT BOUET',
    '748 A': 'TREICHVILLE',
    '748 B': 'PORT BOUET',
    '9345 (FEEDER 3)': 'PORT BOUET',
    'A 25': 'COCODY',
    'ABATTA': 'COCODY',
    'ABLE': 'ADJAME',
    'ABOBO 1': 'ABOBO',
    'ABOBO 2': 'ABOBO',
    'ABOBO 3': 'ABOBO',
    'ACADEMIE 1': 'YOPOUGON',
    'ACADEMIE 2 (DEPART SECOURS AZITO)': 'YOPOUGON',
    'ADDOHA': 'YOPOUGON',
    'ADJAME': 'ADJAME',
    'ADJAME BINGERVILLE': 'BINGERVILLE',
    'ADJOUFFOU': 'PORT BOUET',
    'ADONKOI': 'ANYAMA',
    'AERIA': 'KOUMASSI',
    'AEROPORT': 'PORT BOUET',
    'AGHIEN': 'COCODY',
    'AGIP': 'PORT BOUET',
    'AIME CESAIRE': 'YOPOUGON',
    'AKENDJE': 'BINGERVILLE',
    'AKOUEDO': 'COCODY',
    'ALLIODAN': 'KOUMASSI',
    'ALLIODAN 2': 'MARCORY',
    'AMARA 1': 'KOUMASSI',
    'AMBASSADE DES USA': 'COCODY',
    'AN 2000': 'YOPOUGON',
    'ANA': 'BINGERVILLE',
    'ANANI 2': 'PORT BOUET',
    'ANGRE 1': 'COCODY',
    'ANGRE 2': 'COCODY',
    'ANONKOUA': 'YOPOUGON',
    'ANONO': 'COCODY',
    'ANOUMABO': 'MARCORY',
    'ANYAMA': 'ANYAMA',
    'ARCADES': 'COCODY',
    'ATL': 'TREICHVILLE',
    'ATTINGUE': 'ANYAMA',
    'ATTOBAN': 'COCODY',
    'AVOCATIER': 'ABOBO',
    'AVODIRE': 'YOPOUGON',
    'AVODIRÉ': 'YOPOUGON',
    'AZAGUIE': 'AZAGUIE',
    'AZALAI': 'MARCORY',
    'AZITO': 'YOPOUGON',
    'BAD': 'PLATEAU',
    'BANCO': 'YOPOUGON',
    'BASE SMITA': 'YOPOUGON',
    'BEAGO': 'YOPOUGON',
    'BESSIKOI': 'COCODY',
    'BIABOU': 'ABOBO',
    'BINGERVILLE': 'BINGERVILLE',
    'BINGERVILLE 2': 'COCODY',
    'BLOHORN': 'TREICHVILLE',
    'BRAZZA': 'MARCORY',
    'CAGEOT': 'YOPOUGON',
    'CALMETTE': 'MARCORY',
    'CAMELIA': 'COCODY',
    'CARGILL': 'YOPOUGON',
    'CARREFOUR': 'MARCORY',
    'CARRIERE': 'COCODY',
    'CEMOI': 'YOPOUGON',
    'CEMOI 2': 'YOPOUGON',
    'CHOCODI': 'PORT BOUET',
    'CHOCOLATIERS': 'YOPOUGON',
    'CIMAF 1': 'YOPOUGON',
    'CIMAF 2': 'YOPOUGON',
    'CIMENTER 1 (DÉPART SECOURS)': 'PORT BOUET',
    'CIMENTER 2': 'PORT BOUET',
    'CIMIVOIRE': 'TREICHVILLE',
    'CIMOD': 'ANYAMA',
    'CITE ADM. A': 'PLATEAU',
    'CITE ADM. B': 'PLATEAU',
    'CITE ADO': 'YOPOUGON',
    'CITE BLANCHE': 'COCODY',
    'CITE DES ARTS': 'COCODY',
    'CITE SIR': 'KOUMASSI',
    'CLOUETCHA': 'COCODY',
    'CNPS': 'COCODY',
    'COCODY': 'COCODY',
    'COCOTERAIE': 'PORT BOUET',
    'COMBABI': 'YOPOUGON',
    'CONTENAIRE': 'PORT BOUET',
    'COPRACI': 'COCODY',
    'COPRIM (DEPART SECOURS NIANGON)': 'YOPOUGON',
    'CORNICHE': 'PLATEAU',
    'COSMOS': 'YOPOUGON',
    'COTIERE': 'PORT BOUET',
    'CSK': 'KOUMASSI',
    'CSP': 'YOPOUGON',
    'DABOU': 'YOPOUGON',
    'DANGA': 'COCODY',
    'DCH': 'YOPOUGON',
    'DJIBI': 'COCODY',
    'DJROGOBITE': 'COCODY',
    'DOKUI 1': 'ABOBO',
    'DOKUI 2': 'ABOBO',
    'EBIMPE': 'ANYAMA',
    'EBRA': 'BINGERVILLE',
    'EECI': 'YOPOUGON',
    'ENA': 'COCODY',
    'ENP': 'COCODY',
    'EPHRATA': 'COCODY',
    'ESSO': 'PORT BOUET',
    'EXPRESS': 'COCODY',
    'FALIKOU': 'TREICHVILLE',
    'FEINDJE': 'ABOBO',
    'FEKESSE': 'COCODY/BINGERVILLE',
    'FRAT MATIN': 'ADJAME',
    'FROID (809)': 'MARCORY',
    'FROID (DÉPART SECOURS)': 'COCODY',
    'GESTOCI': 'COCODY',
    'GIS': 'YOPOUGON',
    'GMA': 'TREICHVILLE',
    'GOBELET': 'COCODY',
    'GOLF 1': 'COCODY',
    'GOLF 2': 'COCODY',
    'GONZAGUE': 'PORT BOUET',
    'HARMONIE': 'PLATEAU',
    'HEVEAS': 'PLATEAU',
    'HME': 'BINGERVILLE',
    'HOPITAL': 'YOPOUGON',
    'IDC': 'ANYAMA',
    "IN'CHALLA": 'KOUMASSI',
    'INFS': 'COCODY',
    'INJS': 'MARCORY',
    'INSTITUT PASTEUR': 'YOPOUGON',
    'INTERBAT': 'COCODY',
    'JUSTICE': 'YOPOUGON',
    'KESSY': 'YOPOUGON',
    'KING IVOIRE': 'YOPOUGON',
    'KKF': 'YOPOUGON',
    'KOBAKRO': 'ANYAMA',
    'KOSIPO': 'YOPOUGON',
    'KOUMASSI': 'KOUMASSI',
    'KOUMASSI NORD-EST': 'KOUMASSI',
    'KOWEIT': 'YOPOUGON',
    'LANGEVIN': 'MARCORY',
    'LASME': 'ADJAME',
    'LBI': 'YOPOUGON',
    'LEM': 'YOPOUGON',
    'LEMANIA': 'COCODY',
    'LIBERTE': 'ADJAME',
    'LIMAK 1': 'ANYAMA',
    'LIMAK 2': 'ANYAMA',
    'LIMAK 3': 'ANYAMA',
    'LOGECO': 'KOUMASSI',
    "M'POUTO": 'COCODY',
    'MACA': 'YOPOUGON',
    'MACACI': 'ADJAME',
    "MAIN D'ŒUVRE": 'PLATEAU',
    'MARCHE': 'KOUMASSI',
    'MAROC': 'YOPOUGON',
    'MAURITANIE': 'KOUMASSI',
    'MBATTO BOUAKE': 'BINGERVILLE',
    'MEECI': 'COCODY',
    'MENUISERIE (DEPART SECOURS SOLIC 5)': 'YOPOUGON',
    'MICAO 1': 'YOPOUGON',
    'MICAO 2': 'YOPOUGON',
    'MMCI': 'TREICHVILLE',
    'MOINEAUX': 'KOUMASSI',
    'MUTASIR': 'COCODY',
    "N'DOTRE": 'ABOBO',
    "N'DOUMIN": 'COCODY',
    'NIANGON': 'YOPOUGON',
    'NOBOU': 'YOPOUGON',
    'OCCITANE': 'COCODY',
    'OCTAZ': 'YOPOUGON',
    'OPT': 'TREICHVILLE',
    'OYAK': 'ANYAMA',
    'PALAIS 2': 'KOUMASSI',
    'PALMERAIE 1': 'COCODY',
    'PALMERAIE 2': 'COCODY',
    'PALMINDUSTRIE 1': 'PORT BOUET',
    'PALMINDUSTRIE 2': 'PORT BOUET',
    'PEXA': 'PORT BOUET',
    'PHENIX': 'YOPOUGON',
    'PK 18': 'ABOBO',
    'PK 18 N°2': 'ABOBO',
    'PK 44': 'ANYAMA',
    'PLASTICA': 'KOUMASSI',
    'PMC': 'PORT BOUET',
    'POLYMERE': 'YOPOUGON',
    'POTHY': 'MARCORY',
    'PRESTCIM': 'ANYAMA',
    'PROCACI': 'PORT BOUET',
    'PRODOMO': 'KOUMASSI',
    'RADISSON': 'PORT BOUET',
    'RAN': 'PLATEAU',
    'RAZ 3': 'COCODY',
    'RAZ 4': 'COCODY',
    "RAZ 5/M'BADON": 'COCODY',
    'REMBLAIS': 'KOUMASSI',
    'RESIDENTIEL': 'TREICHVILLE',
    'SACO': 'MARCORY',
    'SANTE': 'ATTECOUBE',
    'SAVANE': 'BINGERVILLE',
    'SCA': 'TREICHVILLE',
    'SCCI': 'ANYAMA',
    'SERVIR': 'COCODY',
    'SETU': 'YOPOUGON',
    'SICOGI': 'KOUMASSI',
    'SICOMED': 'COCODY',
    'SIDECI': 'COCODY',
    'SIDECI YOP': 'YOPOUGON',
    'SIPIM 5': 'COCODY',
    'SIPOREX': 'PORT BOUET',
    'SIPROCO': 'ABOBO',
    'SIR': 'KOUMASSI',
    'SOCIMAT': 'TREICHVILLE',
    'SODECI': 'TREICHVILLE',
    'SODEFOR': 'YOPOUGON',
    'SODEPALM': 'PLATEAU',
    'SOGEFIHA': 'YOPOUGON',
    'SOLIBRA': 'YOPOUGON',
    'SOLIC 5': 'YOPOUGON',
    'SONGON': 'YOPOUGON',
    'SOPIM (MOINEAU 2)': 'KOUMASSI',
    'SOTACI 1': 'YOPOUGON',
    'SOTACI 2': 'YOPOUGON',
    'SOTRALCI': 'YOPOUGON',
    'SOTRAPIM': 'YOPOUGON',
    'SST': 'YOPOUGON',
    'STADE': 'PLATEAU',
    'STADE OLIMPIC': 'ABOBO',
    'STAR 11': 'COCODY',
    'SUD NIANGON': 'YOPOUGON',
    'SYLMAR': 'YOPOUGON',
    'SYNATRESOR': 'COCODY',
    'TC 2 VRIDI': 'TREICHVILLE',
    'TC2 TREICHVILLE': 'TREICHVILLE',
    'TERRA': 'TREICHVILLE',
    'THEKRO': 'YOPOUGON',
    'UDEC': 'MARCORY',
    'UNIWAX': 'ADJAME',
    'VALLON': 'A27',
    'VERSANT 1': 'COCODY',
    'VERSANT 2': 'COCODY',
    'VGE': 'MARCORY',
    'WARF': 'PORT BOUET',
    'WASSAKARA': 'YOPOUGON',
    'WEST': 'ABOBO',
    'XMETAL': 'ANYAMA',
    'YSICO': 'YOPOUGON',
    'ZEUDJI (DÉPART SECOURS DÉPART ANYAMA)': 'ANYAMA',
    'ZEUDJI': 'ABOBO',
    'ZOE BRUNO (AMARA 2)': 'KOUMASSI',
    'ZONE INDUSTRIELLE': 'KOUMASSI',
    'ZOO': 'ADJAME',
}

def generate_vignette(input_text, output_name=None, overrides=None):
    """
    Génère une vignette CIE à partir d'un texte input brut.
    overrides: dict optionnel avec lieu, date, zones, statut pour remplacer la détection auto.
    """
    if overrides is None:
        overrides = {}

    # 0. Gérer multi-rapports et abréviations
    input_text = normalize_abbreviations(input_text)
    base_text, merged_zones = merge_reports(input_text)
    if merged_zones:
        input_text = base_text
        if 'zones' not in overrides or not overrides['zones']:
            overrides['zones'] = merged_zones

    # 1. Analyser l'input
    # 1. Essayer l'extraction via Claude API
    try:
        from claude_extractor import extract_with_claude, API_AVAILABLE
        if API_AVAILABLE:
            api_result = extract_with_claude(input_text)
        else:
            api_result = None
    except:
        api_result = None

    # 2. Utiliser API si disponible, sinon regex
    if api_result:
        print("✓ Extraction via Claude API")
        vignette_type = api_result.get('type') or detect_type(input_text)
        date_str = overrides.get('date') or api_result.get('date') or parse_date(input_text)
        lieu = overrides.get('lieu') or api_result.get('lieu') or extract_lieu(input_text)
        zones = overrides.get('zones') or api_result.get('zones') or extract_zones(input_text)
        statut = overrides.get('statut') or api_result.get('statut') or detect_statut(input_text)
        # Corriger le statut si incomplet
        if statut and 'ÉQUIPES' not in statut.upper():
            statut = STATUT_EN_COURS
    else:
        print("⚠ Fallback regex")
        vignette_type = detect_type(input_text)
        date_str = overrides.get('date') or parse_date(input_text)
        lieu = overrides.get('lieu') or extract_lieu(input_text)
        zones = overrides.get('zones') or extract_zones(input_text)
        statut = overrides.get('statut') or detect_statut(input_text)

    photo_context = detect_photo_context(input_text, vignette_type)
    template_id = select_template(vignette_type, photo_context)
    formulation = build_formulation(input_text, lieu, vignette_type)
    
    print(f"\n{'='*50}")
    print(f"Type détecté    : {vignette_type}")
    print(f"Photo context   : {photo_context}")
    print(f"Template choisi : sans-{template_id}")
    print(f"Date            : {date_str}")
    print(f"Lieu/Ligne      : {lieu}")
    print(f"Zones           : {zones}")
    print(f"Statut          : {statut}")
    print(f"Formulation     : {formulation[:80]}...")
    print(f"{'='*50}")
    
    # 2. Charger le template
    template_path = os.path.join(TEMPLATES_DIR, f"sans-{template_id}.png")
    img = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    
    # 3. Écrire chaque zone
    draw_date(draw, date_str, template_id)
    draw_texte_principal(draw, formulation, lieu, template_id)
    draw_zones_impactees(draw, zones, template_id)
    draw_statut(draw, statut, template_id)
    
    # 4. Retourner l'image en mémoire
    import io
    buffer = io.BytesIO()
    img.save(buffer, "PNG", quality=95)
    buffer.seek(0)
    print(f"\n✓ Vignette générée en mémoire")
    return buffer


def generate_batch(inputs):
    """Génère plusieurs vignettes depuis une liste d'inputs."""
    results = []
    for i, inp in enumerate(inputs):
        try:
            path = generate_vignette(inp, f"vignette_{i+1:02d}.png")
            results.append({'input': inp[:50], 'output': path, 'status': 'OK'})
        except Exception as e:
            results.append({'input': inp[:50], 'output': None, 'status': f'ERREUR: {e}'})
    return results


if __name__ == "__main__":
    # Test avec un input exemple
    test_input = """
    *PS DIVO : départ YOCOBOUET: déclenchement le 14/04/26 à 05h08 avec une PC de 11,2MW. 
    9 postes hors tension dans la zone BARARDON et FOROGUDA
    Recherche de défaut en cours.
    """
    generate_vignette(test_input, "test_output.png")


# ============================================================
# TEMPLATE BI-DR (sans-19 à sans-22)
# ============================================================

DR_NAMES = {
    'DRABO': 'ABOBO',
    'DRYOP': 'YOPOUGON',
    'DRAN': 'ABIDJAN NORD',
    'DRAS': 'ABIDJAN SUD',
    'DRBC': 'BOUAKÉ',
    'DRC': 'CENTRE',
    'DRE': 'EST',
    'DRSE': 'SUD-EST',
    'DRN': 'NORD',
    'DRCO': 'CENTRE-OUEST',
    'DRCS': 'CENTRE-SUD',
    'DRBO': 'BONDOUKOU',
}

BI_DR_TEMPLATES = [19, 20, 21, 22]


def detect_bi_dr(text):
    """Détecte si le texte contient exactement 2 DR distincts."""
    import re
    drs = re.findall(r'@(DR[A-Z]+)', text.upper())
    unique_drs = list(dict.fromkeys(drs))  # ordre d'apparition, sans doublons
    if len(unique_drs) == 2:
        return unique_drs
    return None


def get_dr_name(dr_code):
    """Retourne le nom lisible d'un DR."""
    # Essayer d'abord la correspondance exacte
    name = DR_NAMES.get(dr_code.upper())
    if name:
        return name
    # Sinon extraire depuis le texte entre parenthèses
    return dr_code.replace('DR', '').strip()


def extract_zones_for_dr(text, dr_code):
    """Extrait les zones d'un bloc DR groupées par départ.
    Retourne une liste de strings, chaque string = un groupe (départ + ses zones).
    """
    import re as _re
    pattern = rf'@{_re.escape(dr_code)}\b[^\n]*(?:\([^)]*\))?\n(.*?)(?=@DR[A-Z]|\Z)'
    matches = list(_re.finditer(pattern, text, _re.IGNORECASE | _re.DOTALL))
    if not matches:
        return []
    block = matches[-1].group(0)
    groups = []  # chaque élément = une ligne de puce

    lines = block.split('\n')
    for line in lines:
        line = line.strip().lstrip('*•-').strip()
        if not line or _re.match(r'@DR', line, _re.IGNORECASE):
            continue
        if _re.match(r'aucun incident', line, _re.IGNORECASE):
            continue

        line_zones = []

        # 1. Départ NOM
        depart_match = _re.search(r'D[ée]part\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ\'\s\-0-9]+?)(?:\s*[\.\(:]|\s+Zones|\s*$)', line, _re.IGNORECASE)
        depart_name = None
        if depart_match:
            dn = depart_match.group(1).strip()
            if not _re.match(r'\d{2}[/:]\d{2}', dn) and len(dn) > 2 and not _re.match(r'^\d+$', dn):
                depart_name = dn.upper()
                if depart_name in DEPART_NOM_EXCLUS:
                    # Remplacer par la commune
                    commune_sub = DEPART_COMMUNE.get(depart_name)
                    if commune_sub:
                        depart_name = commune_sub.upper()
                        line_zones.append(depart_name)
                else:
                    line_zones.append(depart_name)

        # 2. Zones libres après "Zones ... :" ou "Zones NOM, NOM isolées"
        zones_libre = _re.search(r'Zones\s+([^.]+?)\s+isol[ée]es', line, _re.IGNORECASE)
        if not zones_libre:
            zones_libre = _re.search(r'Zones[^:]*:\s*([^.]+)\.', line, _re.IGNORECASE)
        if zones_libre:
            parts = _re.split(r'[,;]', zones_libre.group(1))
            for p in parts:
                p = p.strip()
                if p and len(p) > 1 and not _re.match(r'^[\d:]', p):
                    # Eviter doublon avec le nom du départ déjà ajouté
                    if p.upper() not in line_zones:
                        line_zones.append(p.upper())

        elif not zones_libre:
            # 3. Parenthèses
            # Ignorer parenthèses après 'postes restent'
            line_clean = _re.sub(r'\d+\s+postes?\s*\([^)]+\)\s*restent[^.]*\.?', '', line, flags=_re.IGNORECASE)
            for pm in _re.finditer(r'\(([^)]+)\)', line_clean):
                paren = pm.group(1).strip()
                if _re.match(r'^[\d]{2}[:/]', paren):
                    continue
                if _re.match(r'^Poste\s', paren, _re.IGNORECASE):
                    continue  # Ignorer les parenthèses de poste
                parts = _re.split(r'[,;]', paren)
                for p in parts:
                    p = p.strip()
                    if p and len(p) > 1:
                        pu = p.upper()
                        if not _re.match(r'^(reprise|situation|recherche|maintenance|remplacement|réseau|court|poste|bon transmis)', p, _re.IGNORECASE) and not _re.match(r'^[A-Z]{1,3}\d+', pu) and not _re.match(r'^\d+$', pu) and not _re.match(r'^PK\d+', pu):
                            pu = re.sub(r'\bYOP\b(?!OUGON)', 'YOPOUGON', pu)
                    line_zones.append(pu)

        # 4. Ligne sans "Départ" - prendre le texte avant "(" ou ":" comme zone
        has_real_zones = any(not _re.match(r'^(POSTE|P\d)', z) for z in line_zones)
        if not depart_match and not has_real_zones:
            # Format: "Zone NOM (heure) : description (Poste XXX)"
            # Prendre le texte avant la première parenthèse ou ":"
            zone_libre = _re.match(r'^([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][^(:]+?)(?:\s*[\(:])', line, _re.IGNORECASE)
            if zone_libre:
                zone_text = zone_libre.group(1).strip()
                # Ignorer si c'est juste "Début", "Déclenchement", "Isolement"
                if not _re.match(r'^(début|déclenchement|isolement|manœuvre|situation)', zone_text, _re.IGNORECASE):
                    # Pas de poste dans le nom
                    if not _re.match(r'^poste\s', zone_text, _re.IGNORECASE):
                        line_zones.append(zone_text.upper())
            else:
                # Fallback: poste avec zone entre parenthèses
                poste_match = _re.search(r'Poste\s+\S+\s*\(([^)]+)\)', line, _re.IGNORECASE)
                if poste_match:
                    parts = _re.split(r'[,;]', poste_match.group(1))
                    for p in parts:
                        p = p.strip()
                        pu = p.upper()
                        if p and len(p) > 1 and not _re.match(r'^[A-Z]{1,2}\d+', pu) and not _re.match(r'^\d+$', pu):
                            line_zones.append(pu)

        # Chercher "départ NOM reste hors tension" sur la même ligne
        import re as _re3
        for rm in _re3.finditer(r'[Dd][ée]part\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-Za-zÀÂÄÉÈÊËÎÏÔÙÛÜàâäéèêëîïôùûü\s\-\']+?)\s+reste\s+hors\s+tension', line, _re3.IGNORECASE):
            nom = rm.group(1).strip().upper()
            if not _re3.match(r'^[A-Z]{1,2}\d+', nom) and not _re3.match(r'^\d+$', nom) and len(nom) > 2 and nom not in line_zones:
                line_zones.append(nom)

        if line_zones:
            # Préfixer avec la commune si le premier élément est un départ connu
            first = line_zones[0]
            commune = DEPART_COMMUNE.get(first)
            if commune and commune.upper() not in first.upper():
                import re as _recom
                # Ne pas préfixer si le nom commence par un chiffre ou contient déjà un lieu géo
                if not _recom.match(r'^\d', first) and not _recom.match(r'^(ABOBO|YOPOUGON|COCODY|MARCORY|PLATEAU|ADJAME|TREICHVILLE|KOUMASSI|PORT BOUET|ANYAMA|BINGERVILLE)', first, _recom.IGNORECASE):
                    line_zones[0] = f"{commune} {first}"
            groups.append(", ".join(line_zones))

    # Dédoublonner les groupes
    seen = set()
    unique = []
    for g in groups:
        if g not in seen:
            seen.add(g)
            unique.append(g)
    return unique


def generate_bi_dr_vignette(input_text, dr1_code, dr2_code):
    """Génère une vignette bi-DR avec sans-19 à sans-22."""
    import random
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    import os

    # Choisir template aléatoire
    template_num = random.choice(BI_DR_TEMPLATES)
    template_path = os.path.join(TEMPLATES_DIR, f'sans-{template_num}.png')
    img = Image.open(template_path).convert('RGB')
    draw = ImageDraw.Draw(img)

    # Polices
    font_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        font_title = ImageFont.truetype(os.path.join(font_dir, 'big_noodle_titling.ttf'), 30)
        font_header = ImageFont.truetype(os.path.join(font_dir, 'big_noodle_titling.ttf'), 24)
        font_zones = ImageFont.truetype(os.path.join(font_dir, 'big_noodle_titling.ttf'), 22)
        font_date = ImageFont.truetype(os.path.join(font_dir, 'big_noodle_titling.ttf'), 22)
        font_statut = ImageFont.truetype(os.path.join(font_dir, 'big_noodle_titling.ttf'), 19)
    except:
        font_title = font_header = font_zones = font_date = font_statut = ImageFont.load_default()

    # Noms des lieux
    lieu1 = get_dr_name(dr1_code)
    lieu2 = get_dr_name(dr2_code)

    # Date
    date_str = parse_date(input_text)

    # Statut
    statut = detect_statut(input_text)

    # Zones
    zones1 = extract_zones_for_dr(input_text, dr1_code)
    zones2 = extract_zones_for_dr(input_text, dr2_code)

    # Détecter couleur header via Pillow
    px_left = img.getpixel((130, 448))
    px_right = img.getpixel((670, 448))
    is_yellow_left = px_left[0] > 200 and px_left[1] > 150 and px_left[2] < 100
    is_yellow_right = px_right[0] > 200 and px_right[1] > 150 and px_right[2] < 100
    header_color_left = (30, 30, 30) if is_yellow_left else (255, 255, 255)
    header_color_right = (30, 30, 30) if is_yellow_right else (255, 255, 255)

    # --- TITRE ---
    titre_prefix = "PERTURBATIONS SUR LE RESEAU ÉLECTRIQUE "
    titre_lieux = f"{lieu1} / {lieu2}"
    w_prefix = draw.textlength(titre_prefix, font=font_title)
    w_lieux = draw.textlength(titre_lieux, font=font_title)
    total_w = w_prefix + w_lieux
    start_x = int((1080 - total_w) // 2)
    titre_y = 330
    draw.text((start_x, titre_y), titre_prefix, font=font_title, fill=(40, 40, 40))
    draw.text((start_x + int(w_prefix), titre_y), titre_lieux, font=font_title, fill=(255, 106, 95))

    # --- DATE --- alignée à gauche côté droit
    date_y = 393
    draw.text((1055, date_y), date_str, font=font_date, fill=(255, 255, 255), anchor='ra')

    # --- HEADERS COLONNES --- centrés dans leur conteneur
    header_y = 448
    draw.text((265, header_y), f"ZONES IMPACTÉES - {lieu1}", font=font_header, fill=header_color_left, anchor='mm')
    draw.text((810, header_y), f"ZONES IMPACTÉES - {lieu2}", font=font_header, fill=header_color_right, anchor='mm')

    # --- ZONES GAUCHE ---
    zone_y = 490
    zone_x_left = 35
    zone_w_left = 490
    line_h = 28

    for groupe in zones1:
        if zone_y > 875:
            break
        lines = wrap_text(f"• {groupe}", font_zones, zone_w_left - 15)
        for i, line in enumerate(lines):
            if zone_y > 875:
                break
            txt = line if i == 0 else f"  {line}"
            draw.text((zone_x_left + 10, zone_y), txt, font=font_zones, fill=(255, 255, 255))
            zone_y += line_h
        zone_y += 3

    # --- ZONES DROITE ---
    zone_y2 = 490
    zone_x_right = 560
    zone_w_right = 490

    for groupe in zones2:
        if zone_y2 > 875:
            break
        lines = wrap_text(f"• {groupe}", font_zones, zone_w_right - 15)
        for i, line in enumerate(lines):
            if zone_y2 > 875:
                break
            txt = line if i == 0 else f"  {line}"
            draw.text((zone_x_right + 10, zone_y2), txt, font=font_zones, fill=(255, 255, 255))
            zone_y2 += line_h
        zone_y2 += 3

    # --- STATUT ---
    statut_fixe = "TRAVAUX DE REPRISE PROGRESSIVE EN COURS"
    statut_y = 943
    draw.text((540, statut_y), statut_fixe, font=font_statut, fill=(255, 255, 255), anchor='mm')

    # Sauvegarder
    output = BytesIO()
    img.save(output, format='PNG', dpi=(300, 300))
    output.seek(0)
    return output, f"vignette_{lieu1}_{lieu2}_{date_str[:4]}.png"


def wrap_text(text, font, max_width):
    """Coupe le texte en lignes selon la largeur max."""
    from PIL import ImageDraw, Image
    tmp = Image.new('RGB', (1, 1))
    d = ImageDraw.Draw(tmp)
    words = text.split()
    lines = []
    current = ''
    for word in words:
        test = (current + ' ' + word).strip()
        if d.textlength(test, font=font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines if lines else [text]

