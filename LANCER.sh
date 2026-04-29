#!/bin/bash
echo ""
echo " ================================================"
echo "  CIE - Generateur de Vignettes"
echo " ================================================"
echo ""
echo " Demarrage du serveur..."
echo " Ouvre ton navigateur sur: http://localhost:5000"
echo ""
echo " Pour arreter: Ctrl+C"
echo " ================================================"
echo ""
cd "$(dirname "$0")"
python3 server.py
