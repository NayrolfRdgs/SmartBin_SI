# ⚙️ Guide de Configuration - Smart Bin SI

> Configurer Smart Bin SI selon votre matériel et vos besoins.

**Dernière mise à jour** : Février 2026

---

## 📋 Table des Matières

1. [Configuration Principale](#configuration-principale)
2. [Paramètres Caméra](#paramètres-caméra)
3. [Paramètres Arduino](#paramètres-arduino)
4. [Paramètres YOLO](#paramètres-yolo)
5. [Base de Données](#base-de-données)
6. [Chemins et Répertoires](#chemins-et-répertoires)
7. [Mode Apprentissage](#mode-apprentissage)

---

## 🔧 Configuration Principale

Le fichier principal est : **`src/config.py`**

### Structure de Base

```python
"""
Smart Bin SI - Configuration Centrale
Éditez ce fichier pour adapter le système à votre matériel
"""

from pathlib import Path

# Configuration de base
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "waste_items.db"
```

---

## 📷 Paramètres Caméra

### Détection de la Caméra

```python
# ============================================
# CAMÉRA
# ============================================

# Source de la caméra
CAMERA_SOURCE = 0        # 0 = première USB, 1 = deuxième USB, etc.

# Pour Raspberry Pi Camera (ruban spécialisé)
USE_CSI_CAMERA = False   # True si vous utilisez une caméra RPi

# Résolution
FRAME_WIDTH = 640        # En pixels
FRAME_HEIGHT = 480       # En pixels

# Affichage
SHOW_DISPLAY = True      # True pour voir la fenêtre OpenCV en direct
```

### Tester la Caméra

```bash
# Créer un script test_camera.py
import cv2

cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print(f"✓ Caméra 0 OK - Résolution: {frame.shape}")
    else:
        print("✗ Caméra 0 trouvée mais ne capte pas")
else:
    print("✗ Caméra 0 non trouvée. Essayer CAMERA_SOURCE = 1")

cap.release()
```

### Problèmes Courants

| Problème | Solution |
|----------|----------|
| Caméra non détectée | Essayer `CAMERA_SOURCE = 1` ou 2 |
| Flou à la capture | Augmenter `FRAME_WIDTH` et `FRAME_HEIGHT` |
| Performances lentes | Réduire la résolution (640x480 → 320x240) |
| Caméra RPi | Passer `USE_CSI_CAMERA = True` |

---

## 🤖 Paramètres Arduino

### Connexion Série

```python
# ============================================
# ARDUINO
# ============================================

# Port série de l'Arduino
ARDUINO_PORT = '/dev/ttyACM0'   # Linux/macOS
# ARDUINO_PORT = 'COM3'          # Windows (changer numéro si besoin)
# ARDUINO_PORT = 'COM4'          # Deuxième port Arduino sur Windows

# Vitesse de communication (doit correspondre au code Arduino)
BAUD_RATE = 9600                 # 9600, 115200 etc.

# Durée du tri (temps d'attente pour que le déchet tombe)
SORTING_DURATION = 10            # En secondes
```

### Trouver le Port Arduino

#### Windows

1. Connecter l'Arduino à l'ordinateur
2. Ouvrir le **Gestionnaire des périphériques**
3. Chercher **"Ports (COM et LPT)"**
4. Vous verrez : `COM3`, `COM4`, etc.
5. Mettre le numéro dans `config.py`

Ou avec Python :
```bash
python -m serial.tools.list_ports
```

#### Linux

```bash
# Voir tous les ports
ls -la /dev/tty*

# Voir les ports USB
ls -la /dev/ttyACM*
ls -la /dev/ttyUSB*
```

Généralement : `/dev/ttyACM0` ou `/dev/ttyUSB0`

#### macOS

```bash
ls -la /dev/tty.usbserial*
ls -la /dev/tty.wchusbserial*
```

### Tester la Connexion Arduino

```python
# test_arduino.py
import serial
import time

try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)
    
    # Envoyer une couleur
    ser.write(b'yellow\n')
    
    print("✓ Arduino connecté et commande envoyée")
    ser.close()
except Exception as e:
    print(f"✗ Erreur : {e}")
```

---

## 🧠 Paramètres YOLO

### Modèle et Confiance

```python
# ============================================
# MODÈLE YOLO
# ============================================

# Chemin du modèle entraîné
MODEL_PATH = str(MODELS_DIR / "best.pt")

# Seuil de confiance (0-1)
# Plus bas = détecte plus de choses mais moins fiable
# Plus haut = détecte peu mais plus fiable
CONFIDENCE_THRESHOLD = 0.6           # 0.5-0.7 recommandé

# Seuil NMS (Non-Maximum Suppression)
# Évite les détections multiples du même objet
IOU_THRESHOLD = 0.45                 # 0.4-0.5 recommandé
```

### Interprétation des Seuils

```
Confiance basse (0.3)    → Beaucoup de faux positifs
Confiance normale (0.6)  → Bon équilibre ✓
Confiance haute (0.9)    → Peut rater des objets
```

### Optimiser les Performances

```python
# Mode de détection
LEARNING_MODE = True      # True = demande confirmation après chaque détection
MIN_DETECTIONS = 3        # Détections consécutives avant tri automatique
AUTO_SORT_DELAY = 2.0     # Délai entre deux tris (secondes)
```

**Conseils :**
- Si trop de faux positifs → augmenter `CONFIDENCE_THRESHOLD` à 0.7
- Si manque des détections → réduire à 0.5
- Pour performance → augmenter `AUTO_SORT_DELAY`
- Pour rapidité → réduire `MIN_DETECTIONS` à 1

---

## 💾 Base de Données

### Configuration SQLite

```python
# ============================================
# CHEMINS
# ============================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TRAINING_DIR = DATA_DIR / "training_images"
DB_PATH = DATA_DIR / "waste_items.db"
MODELS_DIR = BASE_DIR / "models"
```

### Tables de la Base de Données

**1. waste_classification** - Associations objet → bac

```sql
CREATE TABLE waste_classification (
    item_name TEXT PRIMARY KEY,      -- Nom de l'objet
    bin_color TEXT NOT NULL,         -- Couleur du bac (yellow/green/brown)
    created_at TEXT,                 -- Date de création
    usage_count INTEGER DEFAULT 1    -- Nombre de fois utilisé
)
```

**2. sorting_history** - Historique des tris

```sql
CREATE TABLE sorting_history (
    id INTEGER PRIMARY KEY,
    bin_color TEXT NOT NULL,
    item_name TEXT,
    timestamp TEXT NOT NULL,
    confidence REAL DEFAULT 1.0
)
```

**3. bin_status** - État des bacs

```sql
CREATE TABLE bin_status (
    bin_color TEXT PRIMARY KEY,
    fill_level REAL DEFAULT 0.0,     -- Pourcentage de remplissage
    item_count INTEGER DEFAULT 0,    -- Nombre d'items
    last_emptied TEXT,               -- Dernière vidange
    capacity_liters REAL DEFAULT 10.0 -- Capacité en litres
)
```

### Consulter la Base de Données

```bash
# Installer sqlite3 si nécessaire
pip install db-browser-for-sqlite

# Ou utiliser la ligne de commande
sqlite3 data/waste_items.db

# Requêtes utiles :
SELECT * FROM waste_classification;
SELECT * FROM sorting_history ORDER BY timestamp DESC LIMIT 10;
SELECT * FROM bin_status;
```

---

## 📁 Chemins et Répertoires

### Structure par Défaut

```python
# Racine du projet
BASE_DIR = Path(__file__).parent  # src/

# Données
DATA_DIR = BASE_DIR / "data"                    # data/
TRAINING_DIR = DATA_DIR / "training_images"    # data/training_images/
DB_PATH = DATA_DIR / "waste_items.db"          # data/waste_items.db

# Modèles
MODELS_DIR = BASE_DIR / "models"               # models/
MODEL_PATH = str(MODELS_DIR / "best.pt")       # models/best.pt
```

### Personnaliser les Chemins

```python
# Exemple : utiliser un disque externe
from pathlib import Path

DATA_DIR = Path("E:/SmartBin_Data")  # Disque externe
DB_PATH = DATA_DIR / "waste_items.db"
TRAINING_DIR = DATA_DIR / "training_images"

# Créer automatiquement s'ils n'existent pas
DATA_DIR.mkdir(parents=True, exist_ok=True)
TRAINING_DIR.mkdir(parents=True, exist_ok=True)
```

---

## 📚 Mode Apprentissage

### Activer/Désactiver l'Apprentissage

```python
# ============================================
# APPRENTISSAGE
# ============================================

# Mode interactif (demande confirmation)
LEARNING_MODE = True

# Sauvegarder les images pour apprentissage
SAVE_IMAGES = True

# Seuil de détections consécutives avant tri auto
MIN_DETECTIONS = 3

# Délai entre tris
AUTO_SORT_DELAY = 2.0
```

### Cas d'Utilisation

**Configuration 1 : Mode Interactif (Recommandé pour apprendre)**
```python
LEARNING_MODE = True       # Demande confirmation
SAVE_IMAGES = True         # Enregistre pour apprentissage
MIN_DETECTIONS = 1         # Trier après chaque confirmation
```

**Configuration 2 : Mode Automatique Total**
```python
LEARNING_MODE = False      # Pas de demande
SAVE_IMAGES = True         # Enregistre quand même
MIN_DETECTIONS = 3         # Attendre 3 détections confirmées
```

**Configuration 3 : Production (Sans Apprentissage)**
```python
LEARNING_MODE = False
SAVE_IMAGES = False        # Ne pas surcharger le disque
MIN_DETECTIONS = 1
```

---

## 🎨 Mapping des Objets

### Configurer les Classifications

```python
# ============================================
# BACS DE TRI
# ============================================

VALID_BINS = ["yellow", "green", "brown"]

# Mapping par défaut : objet → bac
WASTE_TO_BIN_MAPPING = {
    # Recyclable (Jaune)
    "plastic": "yellow",
    "plastic_bottle": "yellow",
    "bottle": "yellow",
    "cardboard": "yellow",
    "paper": "yellow",
    "metal": "yellow",
    "glass": "yellow",
    "can": "yellow",
    
    # Organique (Vert)
    "banana_peel": "green",
    "food": "green",
    "organic": "green",
    
    # Reste (Marron)
    "tissue": "brown",
    "trash": "brown",
}

# Couleurs pour affichage OpenCV (BGR)
BIN_COLORS = {
    "yellow": (0, 255, 255),
    "green": (0, 255, 0),
    "brown": (50, 100, 165),
}
```

### Ajouter Nouveaux Objets

```python
# Ajouter au mapping
WASTE_TO_BIN_MAPPING.update({
    "pizza_box": "yellow",
    "apple_core": "green",
    "ceramic": "brown",
})
```

**Note** : Les nouveaux objets détectés en mode apprentissage sont automatiquement ajoutés à la base de données !

---

## 🔍 Profils de Configuration

### Profil 1 : Développement / Test

```python
# config_dev.py
CAMERA_SOURCE = 0
LEARNING_MODE = True
SAVE_IMAGES = True
SHOW_DISPLAY = True
CONFIDENCE_THRESHOLD = 0.5
AUTO_SORT_DELAY = 1.0
```

### Profil 2 : Production

```python
# config_prod.py
CAMERA_SOURCE = 0
LEARNING_MODE = False
SAVE_IMAGES = False
SHOW_DISPLAY = False
CONFIDENCE_THRESHOLD = 0.7
AUTO_SORT_DELAY = 2.0
SORTING_DURATION = 15
```

### Utiliser un Profil

```python
# Dans yolo_detector.py ou waste_classifier.py
import importlib
import sys

config_name = 'config_dev'  # ou 'config_prod'
config = importlib.import_module(f'src.{config_name}')
```

---

## ✅ Checklist de Configuration

- [ ] Port Arduino trouvé et configuré dans `ARDUINO_PORT`
- [ ] Caméra testée avec `CAMERA_SOURCE` correct
- [ ] Résolution caméra définie (`FRAME_WIDTH`, `FRAME_HEIGHT`)
- [ ] Chemins de base configurés
- [ ] Mode apprentissage adapté à vos besoins
- [ ] Mapping des objets complété
- [ ] Seuils YOLO ajustés
- [ ] Tous les répertoires créés automatiquement

---

**Configuration terminée ? Consultez** [docs/UTILISATION.md](UTILISATION.md)

