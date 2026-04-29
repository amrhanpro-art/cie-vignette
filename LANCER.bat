@echo off
echo.
echo  ================================================
echo   CIE - Generateur de Vignettes
echo  ================================================
echo.
echo  Demarrage du serveur...
echo  Ouvre ton navigateur sur: http://localhost:5000
echo.
echo  Pour arreter: ferme cette fenetre
echo  ================================================
echo.
cd /d "%~dp0"
python server.py
pause
