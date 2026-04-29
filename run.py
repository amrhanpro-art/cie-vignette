#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CIE Vignette Generator - Utilisation simple
Usage: python3 run.py
"""
from cie_generator import generate_vignette
import sys

print("=" * 60)
print("  CIE VIGNETTE GENERATOR")
print("=" * 60)
print("Colle ton input (plusieurs lignes OK)")
print("Tape FIN sur une ligne seule pour générer\n")

lines = []
while True:
    try:
        line = input()
        if line.strip().upper() == "FIN":
            break
        lines.append(line)
    except EOFError:
        break

input_text = "\n".join(lines)

if input_text.strip():
    output = generate_vignette(input_text)
    print(f"\n✅ Fichier généré : {output}")
else:
    print("❌ Aucun input fourni.")
