# 🤖 Smart Bin SI - Système Intelligent de Tri des Déchets

> **Poubelle autonome utilisant l'Intelligence Artificielle (YOLOv8) pour le tri automatique et intelligent des déchets. Combinaison de vision par ordinateur, machine learning et électronique embarquée.**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Arduino](https://img.shields.io/badge/Arduino-Uno-00979D.svg)
![YOLO](https://img.shields.io/badge/YOLO-v8-yellow.svg)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

---

## 📚 Table des Matières

1. [Présentation rapide](#-présentation-rapide)
2. [Démarrage rapide](#-démarrage-rapide)
3. [Architecture du système](#️-architecture-du-système)
4. [Installation](#-installation)
5. [Utilisation](#-utilisation)
6. [Documentation](#-documentation)
7. [Support](#-support)

---

## 🎯 Présentation Rapide

### Qu'est-ce que Smart Bin SI ?

Smart Bin SI est un **système de tri automatique de déchets** qui utilise l'intelligence artificielle pour trier correctement les déchets dans les bons bacs. Le système combine :

- **📷 Vision par ordinateur** : détecte les objets via une caméra
- **🧠 Apprentissage automatique** : apprend de chaque nouvelle détection
- **💾 Intelligence persistante** : mémorise les classifications dans une base de données
- **🤖 Automatisation complète** : tri automatisé via servomoteurs Arduino

### ✨ Fonctionnalités principales

✅ **Détection en temps réel** des déchets via caméra  
✅ **Classification intelligente** en 3 catégories :
- 🟡 **Jaune** : Recyclable (plastique, carton, métal, verre)
- 🟢 **Vert** : Organique/Compost (déchets alimentaires, biodégradable)
- 🟤 **Marron** : Déchets généraux (non-recyclable)

✅ **Apprentissage continu** : valide les détections et les enregistre  
✅ **Base de données intelligente** : mémorise toutes les classifications  
✅ **Deux modes d'opération** :
- Mode automatique (détection par caméra + YOLO)
- Mode manuel (saisie texte sans caméra)

✅ **Tableau de bord web** : suivi en temps réel des détections et de l'état du système  
✅ **Apprentissage incrémental** : améliore le modèle YOLO avec vos données

---

## 🚀 Démarrage Rapide

### Configuration minimale requise

```bash
# 1. Cloner le projet
git clone https://github.com/sayfox8/SmartBin_SI.git
cd SmartBin_SI

# 2. Créer et activer un environnement virtuel
python -m venv .venv
# Windows :
.venv\Scripts\activate
# Linux/Mac :
source .venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer le système en mode manuel (test sans caméra)
python src/waste_classifier.py
```

**✓ Succès !** Vous verrez le prompt interactif pour tester le tri.

> 👉 **Pour la configuration complète**, voir [docs/setup/INSTALLATION.md](docs/setup/INSTALLATION.md)

---

## 🏗️ Architecture du Système

### Schéma Simplifié

```
┌──────────────────────────────────────────────────────────────┐
│                      SMART BIN SI                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ 📷 Caméra USB  →  🧠 YOLO Detection  →  💾 DB Manager 💾   │
│                                                ↓             │
│                                          Classification      │
│                                                ↓             │
│                                          Decision Logic      │
│                                                ↓             │
│                                     📡 Serial Commands 📡   │
│                                                ↓             │
│                                     ⚙️ Arduino (Servos) ⚙️  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Les Trois Briques Principales

| Composant | Fichier | Rôle |
|-----------|---------|------|
| **Détection** | `src/yolo_detector.py` | 👁️ Capture vidéo et détecte les objets |
| **Intelligence** | `src/waste_classifier.py` | 🧠 Décide la bonne couleur de bac |
| **Contrôle Matériel** | `arduino/smart_bin_controller.ino` | 🤖 Actionne les servomoteurs |

### Flux Complet de Données

```
1. 📷 Caméra capture une image
   ↓
2. 🧠 YOLO analyse → détecte "plastic_bottle" (confiance: 0.92)
   ↓
3. 💾 Base de données cherche "plastic_bottle"
   ↓
4. 🔍 Trouvé → "yellow" (ou demande confirmation)
   ↓
5. 📡 Envoie "yellow" via USB à l'Arduino
   ↓
6. ⚙️ Arduino fait tourner les servos vers le bac jaune
   ↓
7. 🗑️ L'objet tombe dans le bon bac
   ↓
8. 📊 Enregistrement dans la base de données pour l'apprentissage
```

> 📖 **Voir la documentation complète** : [docs/technical/ARCHITECTURE.md](docs/technical/ARCHITECTURE.md)

---

## 📦 Installation

### Prérequis

- **Python 3.8+** (3.10+ recommandé)
- **pip** (gestionnaire de paquets Python)
- **Câble USB** pour Arduino
- **Caméra USB** (optionnel, pour mode automatique)
- **Arduino Uno** ou compatible
- **Système d'exploitation** : Windows, Linux, ou macOS

### Étapes d'Installation

```bash
# Naviguer vers le répertoire du projet
cd SmartBin_SI

# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement
# Windows :
.venv\Scripts\activate
# Linux / macOS :
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

**Packages installés :**
- `pyserial` : communication avec Arduino
- `opencv-python` : traitement d'images
- `numpy` : calculs matriciels
- `Pillow` : manipulation d'images
- `matplotlib` : visualisation
- `pandas` : gestion de données

### Configuration Arduino

Télécharger l'IDE Arduino et téléverser `arduino/smart_bin_controller.ino` sur l'Arduino.

### Configuration du Système

Éditer [src/config.py](src/config.py) selon votre matériel :

```python
# Pour Windows
ARDUINO_PORT = 'COM3'  # Vérifier dans le Gestionnaire des périphériques

# Pour Linux/Mac
ARDUINO_PORT = '/dev/ttyACM0'
```

> 📖 **Documentation détaillée** : [docs/setup/INSTALLATION.md](docs/setup/INSTALLATION.md)

---

## 💻 Utilisation

### Mode Manuel (Sans Caméra)

Parfait pour tester sans matériel :

```bash
cd src
python waste_classifier.py
```

**Commandes disponibles :**
- Entrer un nom d'objet (ex: `plastic_bottle`, `banana`)
- `stats` → afficher les statistiques de classification
- `quit` → quitter

### Mode Automatique (Avec Caméra)

Utilise YOLO pour détecter les objets en temps réel :

```bash
cd src
python yolo_detector.py
```

**Actions pendant la détection :**
- `y` → confirmer la détection (sauvegarde pour apprentissage)
- `n` → rejeter la détection
- `q` → quitter

### Interface Web (Tableau de Bord)

Accéder au monitoring en temps réel :

```bash
cd admin_interface
python app.py
```

Ouvrir le navigateur : **http://localhost:5000**

> 📖 **Guide complet d'utilisation** : [docs/usage/UTILISATION.md](docs/usage/UTILISATION.md)

---

## 📖 Documentation

| Document | Contenu |
|----------|---------|
| [docs/setup/INSTALLATION.md](docs/setup/INSTALLATION.md) | Installation complète avec prérequis |
| [docs/setup/CONFIGURATION.md](docs/setup/CONFIGURATION.md) | Configuration avancée du système |
| [docs/usage/UTILISATION.md](docs/usage/UTILISATION.md) | Guide d'utilisation des modes |
| [docs/usage/QUICK_START.md](docs/usage/QUICK_START.md) | Démarrage rapide détaillé |
| [docs/technical/ARCHITECTURE.md](docs/technical/ARCHITECTURE.md) | Architecture technique détaillée |
| [docs/technical/APPENTISSAGE.md](docs/technical/APPENTISSAGE.md) | Système d'apprentissage et d'amélioration |
| [docs/technical/ENTRAINEMENT_IA.md](docs/technical/ENTRAINEMENT_IA.md) | Réentraînement du modèle YOLO |
| [docs/technical/DEPANNAGE.md](docs/technical/DEPANNAGE.md) | Troubleshooting et solutions |

---

## 🆘 Support

### Problèmes Courants

**Q : "Arduino non détecté"**  
R : Vérifier le port COM dans `config.py` et installer les drivers CH340/FTDI si nécessaire.

**Q : "CUDA not available"**  
R : Normal si vous n'avez pas de GPU NVIDIA. PyTorch utilisera le CPU (plus lent).

**Q : "Caméra non reconnue"**  
R : Essayer `CAMERA_SOURCE = 1` dans `config.py` ou vérifier les permissions.

> 📖 **FAQ complète** : [docs/technical/DEPANNAGE.md](docs/technical/DEPANNAGE.md)

---

## 📊 Structure du Projet

```
SmartBin_SI/
├── src/                          # Code Python principal
│   ├── config.py                # Configuration centralisée
│   ├── yolo_detector.py         # Détection YOLO
│   ├── waste_classifier.py      # Gestion base de données
│   └── models/
│       └── best.pt              # Modèle YOLO entraîné
│
├── admin_interface/             # Tableau de bord web
│   ├── app.py                   # Application Flask
│   ├── requirements.txt          # Dépendances admin
│   └── static/
│       ├── index.html
│       ├── script.js
│       └── style.css
│
├── arduino/                     # Code Arduino
│   ├── smart_bin_controller.ino
│   └── wokwi-project.txt        # Simulation Wokwi
│
├── docs/                        # Documentation organisée
│   ├── setup/
│   │   ├── INSTALLATION.md
│   │   └── CONFIGURATION.md
│   ├── usage/
│   │   ├── UTILISATION.md
│   │   └── QUICK_START.md
│   └── technical/
│       ├── ARCHITECTURE.md
│       ├── APPENTISSAGE.md
│       ├── ENTRAINEMENT_IA.md
│       └── DEPANNAGE.md
│
├── data/                        # Données du système
│   ├── waste_items.db           # Base SQLite
│   ├── training_images/         # Images pour apprentissage
│   └── logs/                    # Fichiers journaux
│
└── requirements.txt             # Dépendances principales
```

---

## 🎓 Apprentissage et Amélioration

Smart Bin SI utilise un système d'apprentissage continu :

1. **Détection** : YOLO propose une classification
2. **Validation** : L'utilisateur confirme ou rejette
3. **Enregistrement** : Les données sont sauvegardées
4. **Apprentissage** : Réentraînement du modèle avec les nouvelles données

Cela permet au système de s'améliorer progressivement !

> 📖 **Guide complet** : [docs/technical/APPENTISSAGE.md](docs/technical/APPENTISSAGE.md)

---

## 📄 Licence

Ce projet est sous licence Creative Commons Attribution-NonCommercial (CC BY-NC). Interdiction d'usage commercial - voir [LICENSE](LICENSE) pour les détails.

---

## 👥 Contributeurs

- **Auteur Principal** : Équipe SmartBin (FlowCreativeStudio"Florian"; Cyrille; Valentin)
- **Contributions** : Améliorations bienvenues via Pull Requests

---

## 📞 Contact & Ressources

- **Problèmes** : Ouvrir une [Issue GitHub](https://github.com/sayfox8/SmartBin_SI/issues)
- **Documentation** : Voir le dossier [docs/](docs/)

---

**Dernière mise à jour** : Février 2026  
**Version** : 9.0 - Documentation Complète