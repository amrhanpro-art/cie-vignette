#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CIE Vignette Generator - Serveur Web
Lancer avec: python3 server.py
Puis ouvrir: http://localhost:5000
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from cie_generator import generate_vignette, detect_type, extract_lieu, extract_zones, detect_statut, parse_date, merge_reports, normalize_abbreviations
from bi_dr_generator import detect_bi_dr, generate_bi_dr_vignette, get_dr_name, extract_zones_for_dr, _get_dr_header_name
import os
import traceback

app = Flask(__name__, static_folder='web')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/detect', methods=['POST'])
def detect():
    """Appelle l'API Claude et retourne les champs détectés."""
    try:
        data = request.get_json()
        input_text = data.get('input', '').strip()
        if not input_text:
            return jsonify({'error': 'Input vide'}), 400

        # Détecter bi-DR en priorité (avant Claude API)
        input_text_norm = normalize_abbreviations(input_text)
        bi_drs = detect_bi_dr(input_text_norm)
        if bi_drs:
            lieu1 = _get_dr_header_name(input_text_norm, bi_drs[0]) or get_dr_name(bi_drs[0])
            lieu2 = _get_dr_header_name(input_text_norm, bi_drs[1]) or get_dr_name(bi_drs[1])
            zones1 = extract_zones_for_dr(input_text_norm, bi_drs[0])
            zones2 = extract_zones_for_dr(input_text_norm, bi_drs[1])
            # Claude valide/enrichit les zones (si API disponible, sinon fallback regex)
            from bi_dr_generator import validate_zones_with_claude, _get_dr_block
            zones1 = validate_zones_with_claude(_get_dr_block(input_text_norm, bi_drs[0]), bi_drs[0], zones1)
            zones2 = validate_zones_with_claude(_get_dr_block(input_text_norm, bi_drs[1]), bi_drs[1], zones2)
            return jsonify({
                'type': 'bi_dr',
                'lieu': f'{lieu1} / {lieu2}',
                'date': parse_date(input_text_norm),
                'zones': f'{lieu1}: {"; ".join(zones1)} | {lieu2}: {"; ".join(zones2)}',
                'statut': 'TRAVAUX DE REPRISE PROGRESSIVE EN COURS',
                'bi_dr': True,
                'dr1': bi_drs[0],
                'dr2': bi_drs[1],
            })

        # Appeler l'API Claude pour les inputs standard
        try:
            from claude_extractor import extract_with_claude, API_AVAILABLE
            if API_AVAILABLE:
                result = extract_with_claude(input_text)
                if result:
                    return jsonify({
                        'type': result.get('type', 'infos_reseaux'),
                        'lieu': result.get('lieu', ''),
                        'date': result.get('date', ''),
                        'zones': result.get('zones', ''),
                        'statut': result.get('statut', ''),
                    })
        except Exception as e:
            print(f"API error: {e}")

        # Fallback regex standard
        base_text, merged_zones = merge_reports(input_text_norm)
        lieu = extract_lieu(base_text)
        zones = merged_zones if merged_zones else extract_zones(base_text)
        return jsonify({
            'type': detect_type(base_text),
            'lieu': lieu,
            'date': parse_date(base_text),
            'zones': zones,
            'statut': detect_statut(base_text),
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate():
    try:
        from flask import send_file
        import io
        data = request.get_json()
        input_text = data.get('input', '').strip()
        overrides = data.get('overrides', {})
        overrides = {k: v for k, v in overrides.items() if v and v not in ['—', '...', 'null']}
        if not input_text:
            return jsonify({'error': 'Input vide'}), 400
        
        # Détecter bi-DR
        bi_drs = detect_bi_dr(input_text)
        if bi_drs:
            buffer, _ = generate_bi_dr_vignette(input_text, bi_drs[0], bi_drs[1], overrides=overrides)
        else:
            buffer = generate_vignette(input_text, overrides=overrides)
        
        # Générer un nom de fichier pour le téléchargement
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vignette_CIE_{timestamp}.png"
        
        return send_file(
            buffer,
            mimetype='image/png',
            as_attachment=False,
            download_name=filename
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/cie_logo.jpg')
def serve_logo():
    return send_from_directory('web', 'cie_logo.jpg')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*50)
    print("  CIE VIGNETTE GENERATOR")
    print("="*50)
    print(f"  Serveur démarré sur le port {port}")
    print("="*50 + "\n")
    app.run(debug=False, host='0.0.0.0', port=port)
