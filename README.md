# CIE — Générateur de Vignettes

## Installation (une seule fois)

1. Installe Python 3 si pas déjà fait: https://www.python.org
2. Ouvre un terminal dans ce dossier et lance:
   ```
   pip install flask pillow
   ```

## Utilisation

### Windows
Double-clique sur **LANCER.bat**

### Mac / Linux
```bash
chmod +x LANCER.sh
./LANCER.sh
```

Puis ouvre ton navigateur sur: **http://localhost:5000**

## Structure du dossier

```
cie_generator/
├── LANCER.bat          ← Démarrage Windows
├── LANCER.sh           ← Démarrage Mac/Linux
├── server.py           ← Serveur web
├── cie_generator.py    ← Moteur de génération
├── big_noodle_titling.ttf
├── templates/          ← 15 templates PNG (sans-1 à sans-15)
├── web/
│   ├── index.html      ← Interface web
│   └── cie_logo.jpg    ← Logo CIE
└── output/             ← Vignettes générées (créé automatiquement)
```

## Raccourci clavier
- **Ctrl + Entrée** : Générer la vignette directement
