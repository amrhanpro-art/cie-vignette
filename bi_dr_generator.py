"""
Module bi-DR : gestion des vignettes avec 2 directions régionales.
Complètement séparé du code standard - ne touche à rien dans cie_generator.py
"""

import re
import os
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# CONFIGURATION
# ============================================================

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'big_noodle_titling.ttf')

BI_DR_TEMPLATES = [19, 20, 21, 22]

DR_NAMES = {
    'DRABO': 'ABOBO',
    'DRYOP': 'YOPOUGON',
    'DRAN': 'ABIDJAN NORD',
    'DRAS': 'ABIDJAN SUD',
    'DRBC': 'BANCÉ-CENTRE',
    'DRC': 'BOUAKÉ (CENTRE)',
    'DRCEN': 'CENTRE',
    'DRE': 'EST',
    'DRSE': 'SUD-EST',
    'DRN': 'NORD',
    'DRO': 'OUEST',
    'DRCO': 'CENTRE-OUEST',
    'DRCS': 'CENTRE-SUD',
    'DRBO': 'BONDOUKOU',
    'DRSO': 'SUD-OUEST',
    'DRLO': 'LITTORAL OUEST',
    'DRCOU': 'CENTRE-OUEST',
    'DRCSU': 'CENTRE-SUD',
}

# Dictionnaire DEPART -> COMMUNE (source: rattachement HTA nov 2022)
# Uniquement les départs textuels (pas les numéros)
DEPART_COMMUNE = {
    'ABLE': 'ADJAME', 'ABATTA': 'BINGERVILLE', 'ABOBO NORD': 'ABOBO',
    'ABOBO SUD': 'ABOBO', 'ADJOUFFOU': 'PORT BOUET', 'AGBAN': 'ADJAME',
    'AGBAN VILLAGE': 'ADJAME', 'AGREGVILLE': 'PORT BOUET',
    'AKANDJÉ': 'COCODY', 'AKANDJE': 'COCODY',
    'AKOUEDO': 'COCODY', 'ALLABA': 'YOPOUGON',
    'ANONO': 'COCODY', 'ANONO RIVIERA': 'COCODY',
    'ATTECOUBE': 'ATTECOUBE', 'ATTOBAN': 'COCODY',
    'AVODIRE': 'YOPOUGON', 'AVODIRÉ': 'YOPOUGON',
    'BAFOUET': 'YOPOUGON', 'BANCO': 'YOPOUGON',
    'BELLE VIE': 'YOPOUGON', 'BIABOU': 'ABOBO',
    'BLOCKHAUSS': 'COCODY', 'BLOCKAUSS': 'COCODY',
    'BONOUMIN': 'COCODY', 'BRINGAKRO': 'COCODY',
    'BUREAU': 'PLATEAU',
    'CARENA': 'KOUMASSI', 'CARREFOUR': 'YOPOUGON',
    'CCIA': 'PLATEAU', 'CHU COCODY': 'COCODY',
    'CITE ADM. A': 'PLATEAU', 'CITE ADM. B': 'PLATEAU',
    'CITE DES ARTS': 'COCODY', 'CNPS': 'COCODY',
    'COCODY': 'COCODY', 'CORNICHE': 'PLATEAU',
    'DABOU': 'YOPOUGON', 'DANGA': 'COCODY',
    'DCH': 'YOPOUGON', 'DIVO': 'YOPOUGON',
    'EBIMPE': 'ANYAMA', 'EBIMPÉ': 'ANYAMA',
    'ENP': 'COCODY', 'EPHRATA': 'COCODY',
    'FEH KESSE': 'COCODY', 'FEHE': 'COCODY',
    'FORUM': 'PLATEAU', 'GBAGBA': 'ABOBO',
    'GONZAGUEVILLE': 'PORT BOUET',
    'GRAND CARREFOUR': 'YOPOUGON',
    'HARMONIE': 'PLATEAU', 'HEVEAS': 'PLATEAU',
    'INFS': 'COCODY', 'IPR': 'COCODY',
    'KATIA': 'ABOBO', 'KOUMASSI': 'KOUMASSI',
    'LAMY': 'ADJAME', 'LAVAGE': 'YOPOUGON',
    'MAIRIE': 'YOPOUGON', 'MAIN D\'ŒUVRE': 'PLATEAU',
    'MAROC': 'YOPOUGON', 'MEECI': 'COCODY',
    'MERMOZ': 'COCODY', 'MILITAIRE': 'ADJAME',
    'N\'DOTRE': 'ABOBO', 'NDOTRE': 'ABOBO',
    'N\'DOTRÉ': 'ABOBO',
    'NIANGON': 'YOPOUGON', 'NORD': 'ABOBO',
    'ORLY': 'PORT BOUET', 'PALMERAIE': 'COCODY',
    'PANORAMA': 'COCODY', 'PAILLET': 'ADJAME',
    'PHARMACIE': 'YOPOUGON', 'PORT BOUET': 'PORT BOUET',
    'RIVIERA': 'COCODY', 'RIVIERA ANONO': 'COCODY',
    'SANTE': 'ATTECOUBE', 'SIDECI': 'YOPOUGON',
    'SODEPALMBA': 'PLATEAU', 'SOPALM': 'PLATEAU',
    'TINARD': 'ADJAME', 'TOIT ROUGE': 'YOPOUGON',
    'TREIZE': 'ADJAME', 'TSF': 'ADJAME',
    'UNIVERSITE': 'COCODY', 'WILLIAMSVILLE': 'ADJAME',
    'YAO SEHI': 'ABOBO', 'ZEUDJI': 'ABOBO',
    'ZOE BRUNO': 'KOUMASSI', 'ZOÉ BRUNO': 'KOUMASSI',
    'ZONE INDUSTRIELLE': 'YOPOUGON',
}

# Départs dont le nom est remplacé par la commune (villes externes)
DEPART_NOM_EXCLUS = {
    'DABOU', 'BASSAM', 'GRAND BASSAM', 'JACQUEVILLE', 'SONGON',
}

# ============================================================
# DETECTION BI-DR
# ============================================================

def detect_bi_dr(text):
    """Détecte si le texte contient exactement 2 blocs DR distincts.
    Gère le cas où plusieurs codes sont sur la même ligne (@DRC / @DRCO).
    Retourne une liste de 2 éléments (codes simples ou composites 'DRC+DRCO').
    """
    # Trouver les lignes qui contiennent au moins un tag @DR
    dr_lines = re.findall(r'^[^\n]*@DR[A-Z]+[^\n]*$', text, re.MULTILINE | re.IGNORECASE)
    if len(dr_lines) != 2:
        return None
    result = []
    for line in dr_lines:
        codes = re.findall(r'@(DR[A-Z]+)', line.upper())
        if not codes:
            return None
        # Dédoublonner tout en gardant l'ordre
        seen = set()
        unique_codes = []
        for c in codes:
            if c not in seen:
                seen.add(c)
                unique_codes.append(c)
        result.append('+'.join(unique_codes) if len(unique_codes) > 1 else unique_codes[0])
    return result if len(result) == 2 else None

def get_dr_name(dr_code):
    """Retourne le nom lisible d'un DR (supporte codes composites 'DRC+DRCO')."""
    if '+' in dr_code:
        parts = dr_code.split('+')
        names = [DR_NAMES[p] for p in parts if p in DR_NAMES]
        if names:
            return ' / '.join(names)
        return dr_code
    name = DR_NAMES.get(dr_code.upper())
    if name:
        return name
    return dr_code.replace('DR', '').strip()

def _get_dr_header_name(text, dr_code):
    """Extrait le nom lisible depuis la ligne header @DR du texte (ex: '(Centre / Centre-Ouest)').
    Retourne None si pas de texte descriptif dans le header.
    """
    primary_code = dr_code.split('+')[0] if '+' in dr_code else dr_code
    m = re.search(rf'^[^\n]*@{re.escape(primary_code)}\b[^\n]*$', text, re.MULTILINE | re.IGNORECASE)
    if not m:
        return None
    line = m.group(0)
    # Chercher du texte entre parenthèses en fin de ligne : "(Centre / Centre-Ouest)"
    paren = re.search(r'\(([^)]+)\)\s*$', line)
    if paren:
        return paren.group(1).strip().upper()
    return None

# ============================================================
# EXTRACTION ZONES BI-DR
# ============================================================

def _normalize(s):
    """Normalise une chaîne pour comparaison (enlève accents)."""
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').upper()

def _clean_zone(z):
    """Nettoie une zone : majuscules. Ne modifie PAS "Ville de/et X" — gardé tel quel."""
    z = re.sub(r'\bYOP\b(?!OUGON)', 'YOPOUGON', z, flags=re.IGNORECASE)
    z = re.sub(r'\bS/P\s+', 'SOUS-PRÉFECTURE DE ', z)
    z = z.strip().rstrip(',').strip()
    return z.upper()

def _is_junk(p):
    """Retourne True si p est un code/heure/phrase à ignorer."""
    p = p.strip()
    if not p or len(p) < 2:
        return True
    pu = p.upper()
    if re.match(r'^\d{2}[:/]', p):  # heure 13:07
        return True
    if re.match(r'^\d+[Hh]\d+', p):  # heure 13h07
        return True
    if re.match(r'^\d+$', p):  # nombre seul
        return True
    if re.match(r'^\d+[Vv]$', p):  # tension: 21V, 220V
        return True
    if re.match(r'^etc\.?$', p, re.IGNORECASE):  # "etc." ou "etc"
        return True
    if re.match(r'^[A-Z]{1,3}\d+$', pu):  # code type R318, A8, P1
        return True
    if re.match(r'^[A-Z]{1,3}\d+[-]\d+$', pu):  # code type P1-010, R3-210
        return True
    if re.match(r'^PK\d+$', pu):  # PK17, PK24
        return True
    if re.match(r'^(reprise|situation|recherche|maintenance|remplacement|'
                r'réseau|court|poste|bon transmis|nécessite|câble|'
                r'manœuvre|travaux|impactant|plusieurs|alerte|incident|'
                r'assistance|critique|suite)', p, re.IGNORECASE):
        return True
    if re.match(r'^ses\s+localit', p, re.IGNORECASE):  # "ses localités rattachées" (seul)
        return True
    # NE PAS filtrer "Ville et villages rattachés" — l'utilisateur veut le voir
    if re.match(r'^NIP\s+\d+', pu):  # code neutre type NIP 326, NIP 201
        return True
    return False

def extract_zones_for_dr(text, dr_code):
    """
    Extrait les zones d'un bloc DR groupées par ligne (1 ligne = 1 groupe).
    Retourne une liste de strings.
    Supporte les codes composites (ex: 'DRC+DRCO') — utilise le premier code.
    """
    # Pour les codes composites, utiliser le premier pour matcher le bloc
    primary_code = dr_code.split('+')[0] if '+' in dr_code else dr_code
    # Trouver le dernier bloc de ce DR
    pattern = rf'@{re.escape(primary_code)}\b[^\n]*\n(.*?)(?=@DR[A-Z]|\Z)'
    matches = list(re.finditer(pattern, text, re.IGNORECASE | re.DOTALL))
    if not matches:
        return []
    block = matches[-1].group(0)

    groups = []

    for line in block.split('\n'):
        line = line.strip()
        # Retirer tous les caractères non-lettre/chiffre/@ en début de ligne
        # (bullets, emojis, U+2060 WORD JOINER, etc.)
        line = re.sub(r'^[^A-Za-zÀ-ÿ@0-9]+', '', line).strip()
        # Supprimer le préfixe horaire "10:00 - " ou "21:14 - " en début de ligne
        line = re.sub(r'^\d{1,2}:\d{2}\s*[-–]?\s*', '', line).strip()
        if not line or re.match(r'@DR', line, re.IGNORECASE):
            continue
        if re.match(r'aucun incident|tous les incidents', line, re.IGNORECASE):
            continue

        # Ignorer les lignes de reprise/situation (mais capturer toutes les zones)
        if re.search(r'reprise\s+partielle|postes?\s+restent', line, re.IGNORECASE):
            reprise_zones = []
            known = ['ABOBO', 'YOPOUGON', 'COCODY', 'MARCORY', 'PLATEAU',
                     'ADJAME', 'TREICHVILLE', 'KOUMASSI', 'PORT BOUET',
                     'ANYAMA', 'BINGERVILLE', 'RIVIERA', 'ANGRÉ', 'ANGRE']

            # pré-étape : zones de la 1ère phrase "hors tension"
            # (ex: "Départ 902 : Angré 8ème tranche hors tension. Situation... Reprise partielle")
            first_clause_m = re.match(r'^([^.]+\.)', line)
            if first_clause_m:
                fc = re.sub(r'\(\s*\d{1,2}[:/]\d{2}[^)]*\)', '', first_clause_m.group(1))
                if not re.search(r'reprise\s+partielle|postes?\s+restent', fc, re.IGNORECASE):
                    pre_ht = re.search(r':\s*(.+?)\s+hors\s+tension', fc, re.IGNORECASE)
                    if pre_ht:
                        pre_txt = re.sub(r'\s+et\s+', ', ', pre_ht.group(1).strip(), flags=re.IGNORECASE)
                        for part in re.split(r'[,;]', pre_txt):
                            part = _clean_zone(part.strip())
                            if part and len(part) > 2 and not _is_junk(part):
                                reprise_zones.append(part)

            # 0. Extraction explicite "Départ X (heure) : Déclenchement (zones)"
            #    re.match ancré au début → capture MEECI et non "du départ Attoban"
            decl_match = re.match(
                r'D[ée]part\s+(?:\d+\s*k[Vv]\s*)?'
                r'([A-Za-zÀÂÄÉÈÊËÎÏÔÙÛÜàâäéèêëîïôùûü][A-Za-zÀÂÄÉÈÊËÎÏÔÙÛÜàâäéèêëîïôùûü\s\-\']*?)'
                r'\s*(?:\(\s*\d{2}[:/][^)]*\))?\s*:\s*'
                r'D[ée]clenchement\s*\(([^)]+)\)',
                line, re.IGNORECASE
            )
            if decl_match:
                dn0 = re.sub(r'^\d+\s*k[Vv]\s*', '', decl_match.group(1).strip()).strip().upper()
                if len(dn0) > 1 and not re.match(r'^\d+$', dn0):
                    commune = DEPART_COMMUNE.get(dn0)
                    # N'ajouter le nom du départ QUE s'il est reconnu (commune connue)
                    # Sinon les zones en parens suffisent (ex: LIBERTÉ → omis)
                    if commune:
                        if not any(dn0.startswith(k) for k in known):
                            reprise_zones.append(f"{commune} {dn0}")
                        else:
                            reprise_zones.append(dn0)
                for p in re.split(r'[,;]', decl_match.group(2)):
                    p = _clean_zone(p)
                    if p and len(p) > 2 and not _is_junk(p):
                        reprise_zones.append(p)

            # 1. Nom du départ (fallback si étape 0 n'a pas matché)
            if not decl_match:
                dm = re.search(
                    r'D[ée]part\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ\'\s\-0-9]+?)(?:\s*[\.\(:]|\s+Zones|\s+reste|\s+hors|\s*$)',
                    line, re.IGNORECASE
                )
                if dm:
                    dn = re.sub(r'^\d+\s*k[Vv]\s*', '', dm.group(1).strip()).strip()
                    dn_upper = dn.upper()
                    if len(dn_upper) > 1 and not re.match(r'^\d+$', dn_upper) and not _is_junk(dn_upper):
                        commune = DEPART_COMMUNE.get(dn_upper)
                        if dn_upper in DEPART_NOM_EXCLUS:
                            # Départ dont le nom est remplacé par la commune
                            if commune:
                                reprise_zones.append(commune.upper())
                        elif commune:
                            # Départ Abidjan connu → préfixer avec la commune
                            if not any(dn_upper.startswith(k) for k in known):
                                reprise_zones.append(f"{commune} {dn_upper}")
                            else:
                                reprise_zones.append(dn_upper)
                        else:
                            # Départ hors Abidjan (N'DOUMIN, HERMANKONO...) → ajouter tel quel
                            reprise_zones.append(dn_upper)

            # 2. Zones entre parenthèses (fallback si étape 0 n'a pas matché)
            if not decl_match:
                for pm in re.finditer(r'\(([^)]+)\)', line):
                    pc = pm.group(1).strip()
                    if re.match(r'^\d{2}[:/]', pc):
                        continue
                    if re.match(r'^Poste', pc, re.IGNORECASE):
                        continue
                    for p in re.split(r'[,;]', pc):
                        p = _clean_zone(p)
                        if p and len(p) > 2 and not _is_junk(p):
                            reprise_zones.append(p)

            # 2b. Zones "N postes restent HT (zones)" - toujours actif
            for hm in re.finditer(
                r'\d+\s+postes?\s+restent[^(]*\(([^)]+)\)',
                line, re.IGNORECASE
            ):
                for p in re.split(r'[,;]', hm.group(1)):
                    p = _clean_zone(p)
                    if p and len(p) > 2 and not _is_junk(p):
                        reprise_zones.append(p)

            # 3. "départ NOM reste hors tension" (toujours actif)
            for rm in re.finditer(
                r'[Dd][ée]part\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-Za-zÀÂÄÉÈÊËÎÏÔÙÛÜàâäéèêëîïôùûü\s\-\']+?)\s+reste\s+hors\s+tension',
                line, re.IGNORECASE
            ):
                nom = rm.group(1).strip().upper()
                if not re.match(r'^[A-Z]{1,2}\d+', nom) and not re.match(r'^\d+$', nom):
                    commune = DEPART_COMMUNE.get(nom)
                    z = f"{commune} {nom}" if commune else nom
                    reprise_zones.append(z)

            # Dédoublonner et ajouter
            if reprise_zones:
                seen_n = []
                dedup = []
                for z in reprise_zones:
                    zn = _normalize(z)
                    if zn not in seen_n:
                        seen_n.append(zn)
                        dedup.append(z)
                groups.append(', '.join(dedup))
            continue

        line_zones = []

        # === FORMAT "Poste CODE - NOM ZONE : description" ===
        poste_zone_match = re.match(
            r'^Poste\s+[\w\-]+\s*-\s*([^:(]+?)(?:\s*\(([^)]+)\))?\s*:',
            line, re.IGNORECASE
        )
        if poste_zone_match:
            zone_name = _clean_zone(poste_zone_match.group(1))
            paren_content = poste_zone_match.group(2)
            if zone_name and len(zone_name) > 2 and not _is_junk(zone_name):
                line_zones.append(zone_name)
                if paren_content:
                    pc = paren_content.strip()
                    if not re.match(r'^\d{2}[:/]', pc) and not re.match(r'^Poste', pc, re.IGNORECASE):
                        for pp in re.split(r'[,;]', pc):
                            pp = _clean_zone(pp)
                            if pp and len(pp) > 2 and not _is_junk(pp):
                                line_zones.append(pp)
                groups.append(', '.join(line_zones))
                continue

        # === FORMAT "Zone NOM : description" (pas de Départ) ===
        if not re.match(r'^(début|déclenchement|isolement|manœuvre|situation|poste|départ|nip)', line, re.IGNORECASE):
            before_colon = re.match(r'^([^:]{3,60}):', line)
            if before_colon:
                zone_text = before_colon.group(1).strip()
                zone_text = re.sub(r'\s*\(\d+.*$', '', zone_text).strip()  # supprimer (12:45...
                zone_text = re.sub(r'\s*\([^)]*\)\s*$', '', zone_text).strip()  # supprimer (Poste X)
                zone_text = re.sub(r'^[Cc]lient(?:èle)?\s+', '', zone_text).strip()  # supprimer "Client "
                if zone_text and len(zone_text) > 2 and not re.match(r'^\d', zone_text):
                    paren_in = re.search(r'\(([^)]+)\)', before_colon.group(1))
                    clean = re.sub(r'\s*\([^)]*\)', '', zone_text).strip()
                    line_zones.append(_clean_zone(clean))
                    if paren_in:
                        pc = paren_in.group(1).strip()
                        if (not re.match(r'^\d{2}[:/]', pc)
                                and not re.match(r'^Poste', pc, re.IGNORECASE)):
                            for pp in re.split(r'[,;]', pc):
                                pp = _clean_zone(pp)
                                if pp and len(pp) > 2 and not _is_junk(pp):
                                    line_zones.append(pp)
                    # Capturer aussi les parens APRÈS le ":" (ex: "... (Adjouffou, Wharf, SIR)")
                    colon_pos = len(before_colon.group(0))
                    for pm_after in re.finditer(r'\(([^)]+)\)', line[colon_pos:]):
                        pac = pm_after.group(1).strip()
                        if re.match(r'^[\d]{2}[:/]', pac) or re.match(r'^Poste', pac, re.IGNORECASE):
                            continue
                        for pp in re.split(r'[,;]', pac):
                            pp = _clean_zone(pp)
                            if pp and len(pp) > 2 and not _is_junk(pp) and pp not in line_zones:
                                line_zones.append(pp)
                    if line_zones:
                        # Appliquer commune si nécessaire
                        first = line_zones[0]
                        commune = DEPART_COMMUNE.get(first)
                        if commune and commune.upper() not in first and not re.match(r'^\d', first):
                            known = ['ABOBO', 'YOPOUGON', 'COCODY', 'MARCORY', 'PLATEAU',
                                     'ADJAME', 'TREICHVILLE', 'KOUMASSI', 'PORT BOUET',
                                     'ANYAMA', 'BINGERVILLE', 'RIVIERA', 'ANGRÉ', 'ANGRE']
                            if not any(first.startswith(k) for k in known):
                                line_zones[0] = f"{commune} {first}"
                        groups.append(', '.join(line_zones))
                        continue

        # === NIP CODE (zone) — EN PREMIER : la zone du NIP précède le départ ===
        nip_match = re.match(r'^NIP\s+\S+\s*\(([^)]+)\)', line, re.IGNORECASE)
        if nip_match:
            for p in re.split(r'[,;]', nip_match.group(1)):
                p = _clean_zone(p)
                if p and len(p) > 2 and not _is_junk(p) and p not in line_zones:
                    line_zones.append(p)

        # === DÉPART NOM ===
        depart_match = re.search(
            r'D[ée]part\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ\'\s\-0-9]+?)(?:\s*[\.\(:]|\s+Zones|\s*$)',
            line, re.IGNORECASE
        )

        depart_name = None
        if depart_match:
            dn = depart_match.group(1).strip()
            if not re.match(r'\d{2}[/:]', dn) and len(dn) > 2 and not re.match(r'^\d+$', dn):
                # Retirer préfixe tension (33kV, 15kV, 63kV...)
                dn = re.sub(r'^\d+\s*k[Vv]\s*', '', dn).strip()
                # Extraire ville après "de" (ex: "Nord de Bouaké" → "Bouaké")
                m_de = re.search(r'\bde\s+(.+)$', dn, re.IGNORECASE)
                if m_de:
                    dn = m_de.group(1).strip()
                dn_upper = dn.upper()
                if len(dn_upper) > 1:
                    if dn_upper in DEPART_NOM_EXCLUS:
                        depart_name = dn_upper
                        line_zones.append(depart_name)
                    else:
                        depart_name = dn_upper
                        line_zones.append(depart_name)

        # === ZONES LIBRES "Zones NOM, NOM isolées" / "Zone X hors tension" ===
        zones_libre = re.search(r'Zones\s+([^.]+?)\s+isol[ée]es', line, re.IGNORECASE)
        if not zones_libre:
            zones_libre = re.search(r'Zones[^:]*:\s*([^.]+)\.', line, re.IGNORECASE)
        if not zones_libre:
            # "Zone(s) X hors tension" sans deux-points (ex: "Zone INDUSTRIEL PK24 hors tension")
            zones_libre = re.search(r'^Zones?\s+([^.:]+?)\s+(?:hors\s+tension|sont\s+hors)', line, re.IGNORECASE)
        ht_used = False
        if zones_libre:
            parts = re.split(r'[,;]', zones_libre.group(1))
            for p in parts:
                p = _clean_zone(p)
                if p and len(p) > 2 and not _is_junk(p) and p not in line_zones:
                    line_zones.append(p)

        # === TEXTE APRÈS ":" AVANT "hors tension" ===
        elif not re.search(r'reprise\s+partielle|postes?\s+restent', line, re.IGNORECASE):
            # Supprimer les horodatages (07:30), (08:00) pour éviter faux positifs sur ":"
            line_no_ts = re.sub(r'\(\s*\d{1,2}[:/]\d{2}[^)]*\)', '', line)
            ht_match = re.search(r':\s*([^.]+?)\s+(?:hors\s+tension|sont\s+hors|sans\s+courant|sans\s+[eé]lectricit[eé])', line_no_ts, re.IGNORECASE)
            if ht_match:
                ht_text = ht_match.group(1).strip()
                ht_text = re.sub(r'\bS/P\s+', 'SOUS-PRÉFECTURE DE ', ht_text)
                ht_text = re.sub(r'\s+et\s+', ', ', ht_text, flags=re.IGNORECASE)
                # Expansion "Les sous-préfectures d'X, Y, Z" → "SOUS-PRÉFECTURE DE X, ..."
                sp_exp = re.match(r'[Ll]es?\s+sous-préfectures?\s+d[e\'][\s]?(.+)', ht_text, re.IGNORECASE)
                if sp_exp:
                    ht_text = ', '.join(
                        'SOUS-PRÉFECTURE DE ' + p.strip().upper()
                        for p in re.split(r'[,;]', sp_exp.group(1))
                        if p.strip() and len(p.strip()) > 1
                    )
                # Split par virgule en respectant les parenthèses
                _parts = []
                _depth = 0
                _cur = []
                for _c in ht_text:
                    if _c == '(':
                        _depth += 1
                        _cur.append(_c)
                    elif _c == ')':
                        _depth -= 1
                        _cur.append(_c)
                    elif _c == ',' and _depth == 0:
                        _parts.append(''.join(_cur).strip())
                        _cur = []
                    else:
                        _cur.append(_c)
                if _cur:
                    _parts.append(''.join(_cur).strip())
                ht_parts_raw = [p for p in _parts if p]

                # Chercher lieu entre parenthèses du départ AVANT le ':' (ex: Départ 15kV Ville 5 (Korhogo) :)
                paren_lieu = re.search(r'D[ée]part\s+[^(:]+\(([^)]+)\)', line, re.IGNORECASE)
                lieu_prefix = None
                if paren_lieu:
                    pc = paren_lieu.group(1).strip()
                    if not re.match(r'^\d{2}[:/]', pc):
                        lieu_prefix = pc.upper()

                # Nettoyer les parties
                cleaned = []
                seen_norm = []
                if lieu_prefix:
                    cleaned.append(lieu_prefix)
                    seen_norm.append(_normalize(lieu_prefix))

                for hp in ht_parts_raw:
                    hp_clean = _clean_zone(hp)
                    hp_norm = _normalize(hp_clean)
                    if hp_clean and len(hp_clean) > 2 and not _is_junk(hp_clean) and hp_norm not in seen_norm:
                        cleaned.append(hp_clean)
                        seen_norm.append(hp_norm)

                if cleaned:
                    if depart_name and not re.search(r'\d', depart_name):
                        # Pas de chiffre dans depart_name → c'est le nom du quartier/départ
                        dn_norm = _normalize(depart_name)
                        sp_pattern = _normalize("SOUS-PRÉFECTURE DE " + depart_name)

                        if lieu_prefix and re.search(r'\d', lieu_prefix):
                            # lieu_prefix contient un chiffre (ex: "BOUAKÉ 2") → la ville = lieu_prefix sans chiffre
                            base_city = re.sub(r'\s*\d+\s*$', '', lieu_prefix).strip()
                            filtered = []
                            for z in cleaned:
                                z_norm = _normalize(z)
                                if z_norm == _normalize(lieu_prefix):
                                    continue  # supprimer "BOUAKÉ 2"
                                if z_norm == _normalize(base_city):
                                    continue  # éviter doublon ville
                                if z_norm == sp_pattern:
                                    continue  # "SOUS-PRÉFECTURE DE X" couvert par depart_name
                                if z_norm == dn_norm:
                                    continue  # doublon exact du départ
                                filtered.append(z)
                            line_zones = [base_city, depart_name] + filtered
                        elif lieu_prefix:
                            # lieu_prefix sans chiffre = ville directe (ex: "KONG", "KORHOGO")
                            # → la ville vient en tête, les zones après le ":" suivent telles quelles
                            filtered = []
                            for z in cleaned:
                                z_norm = _normalize(z)
                                if z_norm == _normalize(lieu_prefix):
                                    continue  # sera ajouté en tête
                                filtered.append(z)
                            line_zones = [lieu_prefix] + filtered
                        else:
                            # Pas de lieu_prefix → depart_name en premier si non couvert dans les zones
                            filtered = []
                            for z in cleaned:
                                z_norm = _normalize(z)
                                if z_norm == dn_norm:
                                    continue  # doublon exact seulement
                                filtered.append(z)
                            covered = any(dn_norm in _normalize(z) for z in filtered)
                            if not covered:
                                line_zones = [depart_name] + filtered
                            else:
                                line_zones = filtered
                    elif depart_name and not lieu_prefix:
                        # depart_name contient un chiffre, pas de lieu_prefix → préfixer si non couvert
                        dn_norm = _normalize(depart_name)
                        covered = any(dn_norm in _normalize(z) for z in cleaned)
                        if not covered:
                            line_zones = [depart_name] + cleaned
                        else:
                            line_zones = cleaned
                    else:
                        # lieu_prefix sans chiffre déjà en tête de cleaned (ex: KORHOGO depuis "Ville 5 (Korhogo)")
                        line_zones = cleaned
                    ht_used = True

        # === PARENTHÈSES ===
        else:
            # Supprimer parenthèses de type "N postes (R318...) restent"
            line_clean = re.sub(r'\d+\s+postes?\s*\([^)]+\)\s*restent[^.]*\.?', '', line, flags=re.IGNORECASE)
            for pm in re.finditer(r'\(([^)]+)\)', line_clean):
                paren = pm.group(1).strip()
                if re.match(r'^[\d]{2}[:/]', paren):
                    continue
                if re.match(r'^Poste\s', paren, re.IGNORECASE):
                    continue
                for p in re.split(r'[,;]', paren):
                    p = _clean_zone(p)
                    if p and len(p) > 2 and not _is_junk(p):
                        # Remplacer si commence par nom du départ
                        if line_zones and len(line_zones) == 1 and len(line_zones[0]) >= 4:
                            if _normalize(p).startswith(_normalize(line_zones[0])[:4]):
                                line_zones[0] = p
                                continue
                        if p not in line_zones:
                            line_zones.append(p)

        # === ZONES DANS PHRASES SUIVANTES ("La ville de X est HT" / "Les S/P de X, Y sont HT") ===
        if not ht_used and not zones_libre and not re.search(r'reprise\s+partielle|postes?\s+restent', line, re.IGNORECASE):
            for sentence in re.split(r'\.(?:\s+|$)', line):
                sentence = sentence.strip()
                if not sentence:
                    continue
                # "les sous-préfectures de X, Y et Z sont hors tension"
                sp_m = re.search(
                    r'sous-préfectures?\s+d[e\'][\s]?([^.]+?)\s+sont\s+hors\s+tension',
                    sentence, re.IGNORECASE
                )
                if sp_m:
                    txt = re.sub(r'\s+et\s+', ', ', sp_m.group(1), flags=re.IGNORECASE)
                    for p in re.split(r'[,;]', txt):
                        p = _clean_zone(p.strip())
                        if p and len(p) > 2 and not _is_junk(p):
                            z = ('SOUS-PRÉFECTURE DE ' + p) if not p.upper().startswith('SOUS-') else p
                            if z not in line_zones:
                                line_zones.append(z)
                    ht_used = True
                    break
                # "la ville de X est hors tension"
                ville_m = re.search(
                    r'ville\s+de\s+([^.,]+?)\s+est\s+hors\s+tension',
                    sentence, re.IGNORECASE
                )
                if ville_m:
                    p = _clean_zone(ville_m.group(1).strip())
                    if p and len(p) > 2 and not _is_junk(p) and p not in line_zones:
                        line_zones.append(p)
                    ht_used = True
                    break
                # "X et ses localités rattachées sont hors tension"
                loc_m = re.search(
                    r'([A-Za-zÀÂÄÉÈÊËÎÏÔÙÛÜàâäéèêëîïôùûü][^.,]+?)\s+et\s+ses\s+localit[eé]s\s+rattach[eé]es\s+sont\s+hors\s+tension',
                    sentence, re.IGNORECASE
                )
                if loc_m:
                    p = _clean_zone(loc_m.group(1).strip())
                    if p and len(p) > 2 and not _is_junk(p) and p not in line_zones:
                        line_zones.append(p)
                    ht_used = True
                    break
                # "village(s)/quartier(s)/commune(s)/localité(s)/secteur(s)/cité(s) de/d' X"
                lieu_type_m = re.search(
                    r'(?:village|quartier|commune|localit[eé]|secteur|hameau|cit[eé])s?'
                    r'\s+d[e\']\s*([A-Za-zÀ-ÿ][^.,;:()]{1,80}?)'
                    r'(?=\s+(?:sont|est|reste|restent|demeure|demeurent|se\s+trouve)\b|[.,;()]|$)',
                    sentence, re.IGNORECASE
                )
                if lieu_type_m:
                    txt = re.sub(r'\s+et\s+', ', ', lieu_type_m.group(1).strip(), flags=re.IGNORECASE)
                    for p in re.split(r'[,;]', txt):
                        p = _clean_zone(p.strip())
                        if p and len(p) > 2 and not _is_junk(p) and p not in line_zones:
                            line_zones.append(p)
                    if line_zones:
                        ht_used = True
                    break

        # === PARENTHÈSES NORMALES (si pas de hors tension et pas déjà traité par ht_match) ===
        if not zones_libre and not ht_used and not re.search(r'hors\s+tension|sont\s+hors|reprise\s+partielle', line, re.IGNORECASE):
            line_clean = re.sub(r'\d+\s+postes?\s*\([^)]+\)\s*restent[^.]*\.?', '', line, flags=re.IGNORECASE)
            for pm in re.finditer(r'\(([^)]+)\)', line_clean):
                paren = pm.group(1).strip()
                if re.match(r'^[\d]{2}[:/]', paren):
                    continue
                if re.match(r'^Poste\s', paren, re.IGNORECASE):
                    continue
                # Special : "Impactant également le départ X : zones"
                impact_m = re.match(
                    r'[Ii]mpactant\b.*?\b[Dd][ée]part\s+(.+?)\s*:\s*(.+)',
                    paren
                )
                if impact_m:
                    imp_name = _clean_zone(impact_m.group(1).strip())
                    if imp_name and len(imp_name) > 1 and not _is_junk(imp_name):
                        if imp_name not in line_zones:
                            line_zones.append(imp_name)
                    for imp_z in re.split(r'[,;]', impact_m.group(2)):
                        imp_z = _clean_zone(imp_z)
                        if imp_z and len(imp_z) > 2 and not _is_junk(imp_z):
                            if imp_z not in line_zones:
                                line_zones.append(imp_z)
                    continue
                for p in re.split(r'[,;]', paren):
                    p = _clean_zone(p)
                    if p and len(p) > 2 and not _is_junk(p):
                        if line_zones and len(line_zones) == 1 and len(line_zones[0]) >= 4:
                            if _normalize(p).startswith(_normalize(line_zones[0])[:4]):
                                line_zones[0] = p
                                continue
                        if p not in line_zones:
                            line_zones.append(p)

        # === POSTE / NIP NOM (zone) ===
        if not depart_match and not line_zones:
            poste_match = re.search(r'(?:Poste|NIP)\s+[^(]+\(([^)]+)\)', line, re.IGNORECASE)
            if poste_match:
                for p in re.split(r'[,;]', poste_match.group(1)):
                    p = _clean_zone(p)
                    if p and len(p) > 2 and not _is_junk(p):
                        line_zones.append(p)

        # === "départ NOM reste hors tension" sur la ligne ===
        for rm in re.finditer(
            r'[Dd][ée]part\s+([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜ][A-Za-zÀÂÄÉÈÊËÎÏÔÙÛÜàâäéèêëîïôùûü\s\-\']+?)\s+reste\s+hors\s+tension',
            line, re.IGNORECASE
        ):
            nom = rm.group(1).strip().upper()
            if not re.match(r'^[A-Z]{1,2}\d+', nom) and not re.match(r'^\d+$', nom) and nom not in line_zones:
                commune = DEPART_COMMUNE.get(nom)
                if commune:
                    line_zones.append(f"{commune} {nom}")
                else:
                    line_zones.append(nom)

        # Appliquer commune au premier élément si départ connu
        if line_zones and depart_name:
            first = line_zones[0]
            # Pas de préfixe commune pour les villes autonomes (DABOU, BASSAM...)
            if first not in DEPART_NOM_EXCLUS:
                commune = DEPART_COMMUNE.get(first)
                if commune and commune.upper() not in first and not re.match(r'^\d', first):
                    known = ['ABOBO', 'YOPOUGON', 'COCODY', 'MARCORY', 'PLATEAU',
                             'ADJAME', 'TREICHVILLE', 'KOUMASSI', 'PORT BOUET',
                             'ANYAMA', 'BINGERVILLE', 'RIVIERA', 'ANGRÉ', 'ANGRE',
                             'SOUS-PRÉFECTURE']
                    if not any(first.startswith(k) for k in known):
                        line_zones[0] = f"{commune} {first}"

        if line_zones:
            # Supprimer les zones qui sont mot entier contenu dans une autre plus précise
            # ex: "TORTIYA" retiré si "VILLE DE TORTIYA" présent
            # ex: "VGE" retiré si "MARCORY VGE" présent
            # MAIS "MAN" n'est PAS retiré si "MANKONO" présent (pas word-boundary)
            to_remove = set()
            for i, z in enumerate(line_zones):
                zn = _normalize(z)
                if len(zn) < 3:
                    continue
                for j, other in enumerate(line_zones):
                    if i != j:
                        on = _normalize(other)
                        if re.search(r'\b' + re.escape(zn) + r'\b', on) and zn != on:
                            to_remove.add(i)
            line_zones = [z for i, z in enumerate(line_zones) if i not in to_remove]

            # Dédoublonner
            seen = set()
            seen_n = []
            dedup = []
            for z in line_zones:
                zn = _normalize(z)
                if zn not in seen_n:
                    seen.add(z)
                    seen_n.append(zn)
                    dedup.append(z)
            groups.append(', '.join(dedup))

    # Dédoublonner les groupes
    seen_g = set()
    unique = []
    for g in groups:
        if g not in seen_g:
            seen_g.add(g)
            unique.append(g)
    return unique


def _get_dr_block(text, dr_code):
    """Extrait le bloc brut d'un DR depuis le texte complet.
    Supporte les codes composites (ex: 'DRC+DRCO') — utilise le premier code.
    """
    primary_code = dr_code.split('+')[0] if '+' in dr_code else dr_code
    pattern = rf'@{re.escape(primary_code)}\b[^\n]*\n(.*?)(?=@DR[A-Z]|\Z)'
    matches = list(re.finditer(pattern, text, re.IGNORECASE | re.DOTALL))
    if not matches:
        return ''
    return matches[-1].group(0)


def validate_zones_with_claude(block_text, dr_code, regex_zones):
    """Valide et enrichit les zones via Claude API (bi-DR uniquement)."""
    try:
        from claude_extractor import client, API_AVAILABLE
        if not API_AVAILABLE:
            return regex_zones
        import json as _json
        dr_name = get_dr_name(dr_code)
        n = len(regex_zones)
        zones_str = '\n'.join(f'[{i+1}] {z}' for i, z in enumerate(regex_zones)) if regex_zones else '(aucune zone détectée)'
        prompt = (
            f"Tu es un expert en rapports CIE (Compagnie Ivoirienne d'Électricité).\n"
            f"Rapport pour la direction régionale {dr_name} :\n---\n{block_text}\n---\n\n"
            f"La regex a extrait {n} groupe(s). Chaque groupe = 1 ligne (bullet) dans la vignette.\n"
            f"Groupes extraits :\n{zones_str}\n\n"
            f"RÈGLES STRICTES :\n"
            f"1. Retourne EXACTEMENT {n} élément(s) dans le JSON — un par groupe.\n"
            f"2. NE JAMAIS couper un groupe en plusieurs éléments.\n"
            f"3. NE JAMAIS fusionner plusieurs groupes en un.\n"
            f"4. Dans chaque groupe : corrige les noms géographiques (villes, quartiers, villages, communes).\n"
            f"5. Retire les codes techniques (NIP XXX, P1-010, TFO, BT, HTA...) sauf s'ils font partie du nom.\n"
            f"6. Garde 'VILLE DE X', 'VILLE ET VILLAGES RATTACHÉS', 'SOUS-PRÉFECTURE DE X' tels quels.\n"
            f"7. Si une zone du rapport est ABSENTE des groupes, ajoute-la comme nouvel élément (dépasse {n}).\n\n"
            f"Réponds UNIQUEMENT en JSON : {{\"zones\": [\"groupe1\", \"groupe2\", ...]}}"
        )
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        text_resp = message.content[0].text.strip()
        text_resp = re.sub(r'```json\s*|\s*```', '', text_resp).strip()
        data = _json.loads(text_resp)
        zones = data.get('zones', [])
        if isinstance(zones, list) and zones:
            return [str(z).strip() for z in zones if str(z).strip()]
    except Exception as e:
        print(f"[bi-DR] API validation error: {e}")
    return regex_zones


# ============================================================
# GÉNÉRATION VIGNETTE BI-DR
# ============================================================

def _wrap_text(text, font, max_width):
    """Coupe le texte en lignes selon la largeur max."""
    from PIL import ImageDraw, Image as _Img
    tmp = _Img.new('RGB', (1, 1))
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

def generate_bi_dr_vignette(input_text, dr1_code, dr2_code, overrides=None):
    """Génère une vignette bi-DR (sans-19 à sans-22)."""
    from cie_generator import parse_date, detect_statut

    overrides = overrides or {}

    template_num = random.choice(BI_DR_TEMPLATES)
    template_path = os.path.join(TEMPLATES_DIR, f'sans-{template_num}.png')
    img = Image.open(template_path).convert('RGB')
    draw = ImageDraw.Draw(img)

    try:
        font_title  = ImageFont.truetype(FONT_PATH, 30)
        font_header = ImageFont.truetype(FONT_PATH, 24)
        font_zones  = ImageFont.truetype(FONT_PATH, 22)
        font_date   = ImageFont.truetype(FONT_PATH, 22)
        font_statut = ImageFont.truetype(FONT_PATH, 19)
    except Exception:
        font_title = font_header = font_zones = font_date = font_statut = ImageFont.load_default()

    lieu1 = _get_dr_header_name(input_text, dr1_code) or get_dr_name(dr1_code)
    lieu2 = _get_dr_header_name(input_text, dr2_code) or get_dr_name(dr2_code)
    date_str = overrides.get('date') or parse_date(input_text)
    zones1 = extract_zones_for_dr(input_text, dr1_code)
    zones2 = extract_zones_for_dr(input_text, dr2_code)

    # Overrides zones : format "LIEU1: groupe1; groupe2 | LIEU2: groupe3; groupe4"
    # Le ";" sépare les groupes (1 bullet), la "," est à l'intérieur d'un groupe
    if overrides.get('zones'):
        raw_parts = overrides['zones'].split('|')
        def _parse_ov(part):
            part = part.strip()
            zs = part.split(':', 1)[1] if ':' in part else part
            return [z.strip() for z in zs.split(';') if z.strip()]
        if len(raw_parts) >= 2:
            zones1 = _parse_ov(raw_parts[0])
            zones2 = _parse_ov(raw_parts[1])
        elif len(raw_parts) == 1:
            zones1 = _parse_ov(raw_parts[0])

    # Override lieu : format "LIEU1 / LIEU2"
    if overrides.get('lieu'):
        lieux = overrides['lieu'].split('/')
        if len(lieux) >= 2:
            lieu1 = lieux[0].strip()
            lieu2 = lieux[1].strip()

    # --- TITRE ---
    titre_prefix = "PERTURBATIONS SUR LE RESEAU ÉLECTRIQUE "
    titre_lieux  = f"{lieu1} / {lieu2}"
    w_prefix = draw.textlength(titre_prefix, font=font_title)
    w_lieux  = draw.textlength(titre_lieux,  font=font_title)
    start_x  = int((1080 - w_prefix - w_lieux) // 2)
    draw.text((start_x, 330), titre_prefix, font=font_title, fill=(40, 40, 40))
    draw.text((start_x + int(w_prefix), 330), titre_lieux, font=font_title, fill=(255, 106, 95))

    # --- DATE ---
    draw.text((1055, 393), date_str, font=font_date, fill=(255, 255, 255), anchor='ra')

    # --- COULEUR HEADERS ---
    px_left  = img.getpixel((265, 448))
    px_right = img.getpixel((810, 448))
    is_yellow_left  = px_left[0]  > 200 and px_left[1]  > 150 and px_left[2]  < 100
    is_yellow_right = px_right[0] > 200 and px_right[1] > 150 and px_right[2] < 100
    hcl = (30, 30, 30) if is_yellow_left  else (255, 255, 255)
    hcr = (30, 30, 30) if is_yellow_right else (255, 255, 255)

    # --- HEADERS ---
    draw.text((265, 448), f"ZONES IMPACTÉES - {lieu1}", font=font_header, fill=hcl, anchor='mm')
    draw.text((810, 448), f"ZONES IMPACTÉES - {lieu2}", font=font_header, fill=hcr, anchor='mm')

    # --- ZONES GAUCHE ---
    y, line_h = 490, 28
    for groupe in zones1:
        if y > 875:
            break
        lines = _wrap_text(f"• {groupe}", font_zones, 475)
        for i, line in enumerate(lines):
            if y > 875:
                break
            draw.text((45, y), line if i == 0 else f"  {line}", font=font_zones, fill=(255, 255, 255))
            y += line_h
        y += 3

    # --- ZONES DROITE ---
    y2 = 490
    for groupe in zones2:
        if y2 > 875:
            break
        lines = _wrap_text(f"• {groupe}", font_zones, 475)
        for i, line in enumerate(lines):
            if y2 > 875:
                break
            draw.text((570, y2), line if i == 0 else f"  {line}", font=font_zones, fill=(255, 255, 255))
            y2 += line_h
        y2 += 3

    # --- STATUT ---
    statut_text = overrides.get('statut') or "TRAVAUX DE REPRISE PROGRESSIVE EN COURS"
    draw.text((540, 943), statut_text.upper(),
              font=font_statut, fill=(255, 255, 255), anchor='mm')

    buf = BytesIO()
    img.save(buf, format='PNG', dpi=(300, 300))
    buf.seek(0)
    return buf, f"vignette_{lieu1}_{lieu2}.png"
