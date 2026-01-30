# 🤖 Smart Bin SI - Système de Tri Intelligent des Déchets

> **Poubelle intelligente utilisant l'IA (YOLOv8) sur NVIDIA Jetson Nano pour le tri automatique des déchets.**

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![Arduino](https://img.shields.io/badge/Arduino-Uno-00979D.svg)](https://www.arduino.cc/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8-yellow.svg)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Table des Matières

- [Présentation](#-présentation)
- [Démonstration](#-démonstration)
- [Architecture](#-architecture)
- [Matériel Requis](#️-matériel-requis)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Configuration](#️-configuration)
- [Dépannage](#-dépannage)
- [Contribuer](#-contribuer)

---

## 🎯 Présentation

Smart Bin SI est un **système de tri automatique de déchets** qui utilise :
- 🧠 **Intelligence Artificielle** (YOLOv8) pour détecter les objets
- 💾 **Base de données** SQLite pour mémoriser les classifications
- 🤖 **Arduino** pour contrôler les servomoteurs
- 📷 **Caméra** pour la détection temps réel

### Fonctionnalités

✅ **Détection automatique** des déchets par caméra  
✅ **Classification intelligente** en 3 catégories :
   - 🟡 **Jaune** : Recyclable (plastique, carton, métal, verre)
   - 🟢 **Vert** : Organique (déchets alimentaires, biodégradable)
   - 🟤 **Marron** : Déchets généraux (non recyclable)  
✅ **Apprentissage automatique** : mémorise les nouveaux objets  
✅ **Apprentissage au fur et à mesure** : quand tu confirmes une détection (« oui c’est correct »), l’image est sauvegardée pour réentraîner le modèle (voir [docs/APPENTISSAGE.md](docs/APPENTISSAGE.md))  
✅ **Statistiques** : suivi des performances de tri  
✅ **Deux modes** : automatique (YOLO + caméra) ou manuel (saisie texte)

---

## 🎬 Démonstration

### Mode Automatique (détection + apprentissage)
```bash
cd src && python yolo_detector.py
# ou depuis la racine : python -m src.yolo_detector
```
**Apprentissage** : à chaque détection validée (« y »), l’image est sauvegardée dans `data/training_images/<classe>/` pour améliorer le modèle plus tard. Voir [docs/APPENTISSAGE.md](docs/APPENTISSAGE.md).
1. Place un déchet devant la caméra
2. YOLO détecte l'objet (ex: "plastic_bottle")
3. Le système vérifie en base de données
4. La plateforme tourne vers le bon bac
5. Le déchet est déposé automatiquement

### Mode Manuel (sans caméra)
```bash
cd src && python waste_classifier.py
```
1. Entre le nom d'un objet (ex: "plastic_bottle") ou "stats" / "quit"
2. Le système assigne ou récupère la couleur du bac (DB + mapping)
3. L'Arduino effectue le tri

---

## 🏗️ Architecture

### Schéma Simplifié
```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
│  Caméra  │────▶│     YOLO     │────▶│  DB Manager  │────▶│ Arduino  │
│   USB    │     │  Détection   │     │   Logique    │     │  Servos  │
└──────────┘     └──────────────┘     └──────────────┘     └──────────┘
```

### Les 3 Codes Principaux

| Fichier | Langage | Rôle |
|---------|---------|------|
| `yolo_detector.py` | Python | 👁️ Détecte les objets via caméra |
| `waste_classifier.py` | Python | 🧠 Gère la DB et décide la couleur |
| `smart_bin_controller.ino` | C++ | 🤖 Contrôle les mouvements physiques |

**Flux de données complet :**
1. 📷 **Caméra** capture une image
2. 🧠 **YOLO** détecte "plastic_bottle"
3. 💾 **DB Manager** cherche → trouve "yellow"
4. 📡 **Série USB** envoie "yellow" à l'Arduino
5. ⚙️ **Arduino** fait tourner les servos
6. 🗑️ **Déchet** tombe dans le bon bac

> 📖 Pour une explication détaillée, voir [ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 🛠️ Matériel Requis

### Électronique

| Composant | Quantité | Prix ~€ | Lien |
|-----------|----------|---------|------|
| **NVIDIA Jetson Nano** | 1 | 100€ | [NVIDIA](https://www.nvidia.com/fr-fr/autonomous-machines/embedded-systems/jetson-nano/) |
| **Arduino Uno** | 1 | 20€ | [Arduino](https://store.arduino.cc/products/arduino-uno-rev3) |
| **Servo MG996R** | 2 | 10€/pièce | Amazon |
| **Caméra USB** ou **CSI** | 1 | 15-30€ | Logitech C270 |
| **Alimentation 5V/3A** | 1 | 10€ | Pour servos |
| Câbles Dupont | - | 5€ | Connexions |

**Budget total : ~180-200€**

### Mécanique (à fabriquer)

- Plateforme rotative (impression 3D ou bois)
- Support pour servomoteurs
- Rampe d'arrivée des déchets
- 3 bacs de tri (jaune, vert, marron)

---

## 📥 Installation

### Méthode 1 : Installation Automatique (Recommandé)

```bash
# 1. Cloner le projet
git clone https://github.com/sayfox8/SmartBin_SI.git
cd SmartBin_SI

# 2. Lancer l'installation automatique
bash scripts/setup.sh

# 3. Déconnexion/Reconnexion (IMPORTANT pour permissions série)
logout

# 4. Télécharger un modèle YOLO pré-entraîné
python3 scripts/download_model.py
# Choisis [1] YOLOv8n Waste (rapide)

# 5. Uploader le code Arduino
# Ouvre Arduino IDE
# Fichier > Ouvrir > arduino/smart_bin_controller.ino
# Outils > Carte > Arduino Uno
# Outils > Port > /dev/ttyACM0
# Téléverser (→)
```

### Méthode 2 : Installation Manuelle

<details>
<summary>Cliquer pour voir les étapes détaillées</summary>

```bash
# Mise à jour système
sudo apt-get update && sudo apt-get upgrade -y

# Installer dépendances système
sudo apt-get install -y python3-pip python3-dev build-essential git

# Installer PyTorch pour Jetson
wget https://nvidia.box.com/shared/static/fjtbno0vpo676a25cgvuqc1wty0fkkg6.whl -O torch.whl
pip3 install torch.whl
rm torch.whl

# Installer dépendances Python
pip3 install pyserial opencv-python numpy Pillow ultralytics

# Permissions série
sudo usermod -a -G dialout $USER
logout  # Puis reconnecte-toi

# Créer structure
mkdir -p SmartBin_SI/{src,arduino,models,data/logs}
cd SmartBin_SI
```

</details>

### Vérification de l'Installation

```bash
# Tester les connexions matérielles
python3 scripts/test_hardware.py
```

**Résultat attendu :**
```
[1] Checking Serial Ports...
   ✓ Found 1 port(s): /dev/ttyACM0

[2] Checking Camera...
   ✓ Camera accessible at /dev/video0

[3] Checking PyTorch...
   ✓ PyTorch v1.10.0
   ✓ CUDA available

[4] Checking YOLOv8...
   ✓ Ultralytics installed
```

---

## 🚀 Utilisation

### Démarrage Rapide

#### Mode Automatique (Détection YOLO)

```bash
python3 yolo_detector.py
```

**Contrôles :**
- `q` : Quitter
- `s` : Forcer le tri de l'objet actuel
- `r` : Réinitialiser le compteur de détections

**Fenêtre de détection :**
- Les boîtes de couleur indiquent le bac cible
- Le compteur montre les détections consécutives (ex: 2/3)
- FPS affiché en haut à gauche

#### Mode Manuel (Sans Caméra)

```bash
python3 waste_classifier.py
```

**Commandes disponibles :**
- `[nom objet]` : Trier un objet (ex: "plastic_bottle")
- `stats` : Afficher les statistiques
- `quit` : Quitter le programme

**Exemple de session :**
```
Objet détecté > plastic_bottle
✓ Trouvé en base : plastic_bottle → bac yellow
🎯 Action de tri : plastic_bottle → bac yellow
→ Commande envoyée à l'Arduino : yellow
⏳ Attente de la fin du tri (10s)...
✓ Tri terminé

Objet détecté > stats

📊 STATISTIQUES DE LA BASE DE DONNÉES
Total d'objets appris : 12
  Bac yellow   :   7 objets (  35 utilisations)
  Bac green    :   3 objets (  12 utilisations)
  Bac brown    :   2 objets (   8 utilisations)
```

---

## ⚙️ Configuration

### Fichier config.py

Tous les paramètres sont centralisés dans `src/config.py` :

```python
# Modèle YOLO à utiliser
MODEL_NAME = "yolov8n_waste.pt"  # nano (rapide) ou yolov8s_waste.pt (précis)

# Seuils de détection
CONFIDENCE_THRESHOLD = 0.6  # 0.0 à 1.0 (plus haut = plus strict)
MIN_DETECTIONS = 3          # Détections consécutives requises

# Caméra
CAMERA_SOURCE = 0           # 0 = USB, 1 = deuxième caméra
USE_CSI_CAMERA = False      # True pour Raspberry Pi Camera

# Arduino
ARDUINO_PORT = "/dev/ttyACM0"  # Changer si différent
BAUD_RATE = 9600

# Mapping déchets → bacs (PERSONNALISER ICI)
WASTE_TO_BIN_MAPPING = {
    "plastic": "yellow",
    "cardboard": "yellow",
    "banana_peel": "green",
    "tissue": "brown",
    # Ajoute tes propres classes ici
}
```

### Personnaliser le Mapping

**Pour ajouter une nouvelle classe :**

1. Édite `src/config.py`
2. Ajoute dans `WASTE_TO_BIN_MAPPING` :
   ```python
   "aluminum_can": "yellow",
   ```
3. Redémarre le programme

**Pour changer un mapping existant :**
```python
# Avant
"plastic_bottle": "yellow",

# Après (si tu veux le mettre ailleurs)
"plastic_bottle": "brown",
```

---

## 🔧 Calibration Arduino

### Ajuster les Angles des Servos

Si les servos ne pointent pas vers les bons bacs :

1. Ouvre `arduino/smart_bin_controller.ino`
2. Modifie les constantes :

```cpp
// Angles d'orientation (rotation gauche/droite)
const int ANGLE_BROWN = 30;    // ← Change ici
const int ANGLE_YELLOW = 150;  // ← Change ici
const int ANGLE_GREEN = 90;    // ← Change ici

// Angles de vidage
const int TILT_UP = 20;        // ← Bascule vers le haut
const int TILT_DOWN = 160;     // ← Bascule vers le bas
```

3. Retéléverse sur l'Arduino
4. Teste avec le mode manuel

### Mode Calibration (Optionnel)

Décommente dans le `.ino` :
```cpp
void loop() {
  // Ajoute ceci pour tester tous les angles
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    if (command == "calibrate") {
      calibrationMode();  // Teste tous les angles
    }
  }
}
```

---

## 🐛 Dépannage

### Problème : Arduino non détecté

**Symptôme :** `Mode simulation (Arduino non détecté)`

**Solutions :**
```bash
# 1. Vérifier les ports disponibles
ls /dev/ttyACM* /dev/ttyUSB*

# 2. Vérifier les permissions
groups $USER  # Doit contenir "dialout"

# 3. Ajouter aux permissions si absent
sudo usermod -a -G dialout $USER
logout  # Puis reconnecte-toi

# 4. Tester manuellement
python3 -c "import serial; s = serial.Serial('/dev/ttyACM0', 9600); print('OK')"
```

### Problème : Caméra non détectée

**Symptôme :** `Échec d'ouverture de la caméra`

**Solutions :**
```bash
# 1. Lister les caméras
ls /dev/video*

# 2. Tester avec v4l2
v4l2-ctl --list-devices

# 3. Tester OpenCV
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"

# 4. Changer CAMERA_SOURCE dans config.py
CAMERA_SOURCE = 1  # Essayer 1 au lieu de 0
```

### Problème : Détection YOLO lente (< 5 FPS)

**Solutions :**

1. **Réduire la résolution** dans `config.py` :
   ```python
   FRAME_WIDTH = 416   # au lieu de 640
   FRAME_HEIGHT = 416
   ```

2. **Utiliser un modèle plus léger** :
   ```python
   MODEL_NAME = "yolov8n_waste.pt"  # Nano = plus rapide
   ```

3. **Désactiver l'affichage** :
   ```python
   SHOW_DISPLAY = False
   ```

### Problème : Modèle pas assez précis

**Solutions :**

1. **Baisser le seuil de confiance** :
   ```python
   CONFIDENCE_THRESHOLD = 0.5  # au lieu de 0.6
   ```

2. **Utiliser un modèle plus gros** :
   ```python
   MODEL_NAME = "yolov8s_waste.pt"  # Small = plus précis
   ```

3. **Entraîner ton propre modèle** avec tes données

### Problème : Mauvais tri (mauvais bac)

**Causes possibles :**

1. **Mapping incorrect** → Vérifie `WASTE_TO_BIN_MAPPING` dans `config.py`
2. **Angles servos mal réglés** → Recalibre dans le `.ino`
3. **Objet inconnu** → Ajoute-le manuellement en DB

---

## 📊 Base de Données

### Structure

```sql
-- Table principale
CREATE TABLE waste_classification (
    item_name TEXT PRIMARY KEY,      -- "plastic_bottle"
    bin_color TEXT NOT NULL,         -- "yellow"
    created_at TIMESTAMP,            -- Date de création
    usage_count INTEGER DEFAULT 1   -- Nombre d'utilisations
);
```

### Commandes Utiles

```bash
# Voir toutes les entrées
sqlite3 data/waste_items.db "SELECT * FROM waste_classification;"

# Supprimer un objet
sqlite3 data/waste_items.db "DELETE FROM waste_classification WHERE item_name='plastic_bottle';"

# Réinitialiser la DB
rm data/waste_items.db
python3 waste_classifier.py  # Recrée la DB
```

---

## 📈 Performances

### Benchmarks (Jetson Nano)

| Modèle | Taille | FPS | Précision |
|--------|--------|-----|-----------|
| YOLOv8n | 6 MB | 18-22 | ~85% |
| YOLOv8s | 22 MB | 10-14 | ~89% |
| YOLOv8m | 50 MB | 4-7 | ~92% |

### Optimisations

Pour améliorer les performances :

1. **Convertir en TensorRT** (accélération Jetson) :
   ```bash
   python3 -c "from ultralytics import YOLO; YOLO('models/best.pt').export(format='engine')"
   ```

2. **Réduire la résolution d'entrée**

3. **Désactiver l'affichage OpenCV**

---

## 🎓 Entraîner Ton Propre Modèle

### Dataset Recommandés

1. **TrashNet** (2527 images, 6 classes)
   - https://github.com/garythung/trashnet

2. **TACO** (1500+ images, 60+ classes)
   - http://tacodataset.org/

3. **Roboflow Waste** (5460 images)
   - https://universe.roboflow.com/projectverba/yolo-waste-detection

### Entraînement Rapide (Google Colab)

```python
# Dans un notebook Colab
!git clone https://github.com/ultralytics/ultralytics
%cd ultralytics
!pip install -r requirements.txt

# Télécharger ton dataset (Roboflow)
from roboflow import Roboflow
rf = Roboflow(api_key="TON_API_KEY")
project = rf.workspace().project("TON_PROJET")
dataset = project.version(1).download("yolov8")

# Entraîner
!yolo train model=yolov8n.pt data={dataset.location}/data.yaml epochs=100 imgsz=640

# Télécharger best.pt vers ta Jetson
```

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! 

### Comment contribuer

1. Fork le projet
2. Crée une branche (`git checkout -b feature/AmazingFeature`)
3. Commit tes changements (`git commit -m 'Add some AmazingFeature'`)
4. Push sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvre une Pull Request

### Idées d'Améliorations

- [ ] Interface graphique (GUI avec Tkinter)
- [ ] Support multi-caméras
- [ ] API REST pour contrôle à distance
- [ ] Application mobile
- [ ] Détection de niveau de remplissage des bacs
- [ ] Système de notification (email/SMS)
- [ ] Dashboard web avec statistiques
- [ ] Support d'autres langues

---

## 📜 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 👥 Auteurs

**Smart Bin SI Team**
- Développement : [FlowCreativeStudio]
- Contact : []
- GitHub : [@sayfox8](https://github.com/sayfox8)

---

## 🙏 Remerciements

- [Ultralytics](https://github.com/ultralytics/ultralytics) pour YOLOv8
- [NVIDIA](https://www.nvidia.com/) pour Jetson Nano
- [Arduino](https://www.arduino.cc/) pour la plateforme
- [Roboflow](https://roboflow.com/) pour les datasets

---

## 📞 Support

- **Documentation complète** : [ARCHITECTURE](ARCHITECTURE.md) [QUICK_START](QUICK_START.md)
- **Issues GitHub** : [Créer un ticket](https://github.com/sayfox8/SmartBin_SI/issues)
- **Email** : 

---

## 🗺️ Roadmap

### Version 1.0 ✅
- [ ] Détection YOLO basique
- [x] Contrôle Arduino
- [x] Base de données SQLite

### Version 2.0 🔄 (En cours)
- [ ] Optimisation TensorRT
- [ ] Interface graphique
- [ ] Statistiques avancées

### Version 3.0 📅 (Prévu)
- [ ] Multi-caméras
- [ ] API REST
- [ ] Application mobile
- [ ] Cloud sync

---

<div align="center">

**Fait avec ❤️ pour un monde plus propre 🌍♻️**

[⬆ Retour en haut](#-smart-bin-si---système-de-tri-intelligent-des-déchets)

</div>