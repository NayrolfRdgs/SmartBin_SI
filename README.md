#  Smart Bin SI

> Système de tri automatique de déchets utilisant l'IA (YOLOv8) pour une classification intelligente.

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

##  Démarrage Rapide

### Prérequis
- Python 3.8+
- Arduino Uno
- Caméra USB
- Dépendances : voir [docs/setup/INSTALLATION.md](docs/setup/INSTALLATION.md)

### Installation Express
`ash
git clone https://github.com/sayfox8/SmartBin_SI.git
cd SmartBin_SI
pip install -r requirements.txt
`

### Premier Lancement
`ash
python src/waste_classifier.py
`

##  Structure
- docs/setup/ : Installation et configuration
- docs/usage/ : Guide d'utilisation
- docs/technical/ : Documentation technique
- src/ : Code source
- rduino/ : Firmware Arduino
- dmin_interface/ : Interface web d'administration

##  Documentation
- [Installation complète](docs/setup/INSTALLATION.md)
- [Guide d'utilisation](docs/usage/UTILISATION.md)
- [Architecture technique](docs/technical/ARCHITECTURE.md)

##  Licence
Ce projet est sous licence Creative Commons Attribution-NonCommercial (CC BY-NC). Interdiction d'usage commercial.