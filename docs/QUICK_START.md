# 🚀 Quick Start - Smart Bin SI

## 📋 Vue d'Ensemble Rapide

**Temps total : ~30 minutes**

```
Installation (15 min) → Téléchargement Modèle (5 min) → Test (5 min) → Utilisation (5 min)
```

---

## ⚡ Installation Ultra-Rapide

### 1️⃣ Cloner/Créer le Projet (1 min)

```bash
# Si tu as déjà les fichiers
cd SmartBin_SI

# OU créer de zéro
mkdir SmartBin_SI && cd SmartBin_SI
```

### 2️⃣ Lancer l'Installation Automatique (15 min)

```bash
# Rendre le script exécutable
chmod +x scripts/setup.sh

# Lancer l'installation
bash scripts/setup.sh
```

☕ **Pause café pendant que ça installe...**

### 3️⃣ Déconnexion/Reconnexion (IMPORTANT!)

```bash
# Pour appliquer les permissions série
logout
# Puis reconnecte-toi
```

---

## 🧠 Télécharger un Modèle Pré-entraîné (5 min)

### Option A : Modèle Léger (Recommandé pour débuter)

```bash
python3 scripts/download_model.py
# Choisis [1] YOLOv8n Waste (Nano - Fast)
# Méthode [2] Ultralytics Generic
```

### Option B : Téléchargement Manuel

Si le script ne marche pas :

1. Va sur [Roboflow Universe](https://universe.roboflow.com/fyp-bfx3h/yolov8-trash-detections)
2. Clique "Download Dataset"
3. Format : **YOLOv8**
4. Télécharge le ZIP
5. Extrais et copie `weights/best.pt` vers `models/yolov8n_waste.pt`

---

## 🧪 Test du Matériel (2 min)

```bash
python3 scripts/test_hardware.py
```

**Tu dois voir :**
```
[1] Checking Serial Ports...
   ✓ Found 1 port(s):
      - /dev/ttyACM0

[2] Checking Camera...
   ✓ Camera accessible at /dev/video0

[3] Checking PyTorch...
   ✓ PyTorch v1.10.0
   ✓ CUDA available (GPU: NVIDIA Tegra X1)

[4] Checking YOLOv8...
   ✓ Ultralytics YOLOv8 installed
```

### ⚠️ Problèmes Courants

| Problème | Solution |
|----------|----------|
| ✗ No serial ports found | `sudo usermod -a -G dialout $USER` puis logout/login |
| ✗ Camera not accessible | `ls /dev/video*` pour vérifier le port |
| ✗ PyTorch not installed | Relance `bash scripts/setup.sh` |

---

## 🎮 Utilisation

### Mode 1 : Contrôle Manuel (Sans Caméra)

**Parfait pour tester sans YOLO**

```bash
bash scripts/run_manual.sh
```

**Interface :**
```
🤖 SMART BIN SI - MANUAL CONTROL SYSTEM
======================================================

Detected item > plastic bottle
🔍 Processing: 'plastic bottle'
✓ Found in database: plastic bottle → yellow bin
🎯 Sorting action: plastic bottle → yellow bin
→ Command sent to Arduino: yellow
⏳ Waiting for sorting completion (10s)...
✓ Sorting complete
```

### Mode 2 : Détection Automatique (Avec Caméra)

**Utilise YOLO pour détecter automatiquement**

```bash
bash scripts/run_auto.sh
```

**Contrôles :**
- `q` : Quitter
- `s` : Forcer le tri immédiat
- `r` : Réinitialiser le compteur de détections

**Fenêtre OpenCV :**
```
┌────────────────────────────┐
│  Smart Bin - Detection     │
│                            │
│  FPS: 15 | Detections: 2  │
│  Tracking: plastic (2/3)   │
│                            │
│  ┌──────────────┐          │
│  │ plastic 0.87 │          │
│  │  → yellow    │          │
│  └──────────────┘          │
└────────────────────────────┘
```

---

## 📊 Vérifier les Statistiques

```bash
python3 src/waste_classifier.py
# Puis tape : stats
```

**Affichage :**
```
📊 DATABASE STATISTICS
==================================================
Total learned items: 15

  Yellow   bin:   8 items (  42 uses)
  Green    bin:   4 items (  18 uses)
  Brown    bin:   3 items (  12 uses)

Top 5 most sorted items:
  1. plastic_bottle        → yellow (15 times)
  2. banana_peel           → green  (8 times)
  3. cardboard             → yellow (6 times)
  4. paper                 → yellow (5 times)
  5. food_waste            → green  (4 times)
==================================================
```

---

## ⚙️ Personnalisation Rapide

### Changer le Mapping Déchets → Bacs

Édite `src/config.py` :

```python
WASTE_TO_BIN_MAPPING = {
    "plastic": "yellow",      # ← Change la couleur ici
    "cardboard": "yellow",
    "banana_peel": "green",   # ← Ajoute de nouvelles classes
    "tissue": "brown",
}
```

### Changer la Caméra

```python
# Dans config.py
CAMERA_SOURCE = 0  # USB camera 1
# ou
CAMERA_SOURCE = 1  # USB camera 2
# ou
USE_CSI_CAMERA = True  # Raspberry Pi Camera
```

### Ajuster la Sensibilité

```python
# Dans config.py
CONFIDENCE_THRESHOLD = 0.6  # Plus bas = détecte plus (mais + faux positifs)
MIN_DETECTIONS = 3          # Plus bas = tri plus rapide
```

---

## 🐛 Dépannage Rapide

### Problème : Arduino non détecté

```bash
# Vérifier les ports disponibles
ls /dev/ttyACM* /dev/ttyUSB*

# Changer le port dans config.py
ARDUINO_PORT = "/dev/ttyACM1"  # ou /dev/ttyUSB0
```

### Problème : Caméra non détectée

```bash
# Lister les caméras
ls /dev/video*

# Tester manuellement
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"
```

### Problème : Détection YOLO lente (< 5 FPS)

**Solution 1 : Réduire la résolution**
```python
# Dans config.py
FRAME_WIDTH = 416  # au lieu de 640
FRAME_HEIGHT = 416
```

**Solution 2 : Utiliser un modèle plus léger**
```python
MODEL_NAME = "yolov8n_waste.pt"  # Le plus rapide
```

**Solution 3 : Désactiver l'affichage**
```python
SHOW_DISPLAY = False  # Pas de fenêtre OpenCV = + rapide
```

### Problème : Modèle pas trouvé

```bash
# Vérifier que le fichier existe
ls models/*.pt

# Si vide, télécharge un modèle
python3 scripts/download_model.py
```

---

## 📝 Workflow Quotidien

### 🌅 Démarrage du Système

```bash
# 1. Allumer la Jetson Nano
# 2. Connecter l'Arduino via USB
# 3. Connecter la caméra USB
# 4. Lancer le mode auto
cd SmartBin_SI
bash scripts/run_auto.sh
```

### 🌙 Arrêt du Système

```bash
# Dans la fenêtre de détection
# Appuyer sur 'q'

# Ou Ctrl+C dans le terminal
```

### 🔄 Mise à Jour du Modèle

```bash
# Télécharger un nouveau modèle
python3 scripts/download_model.py

# Redémarrer la détection
bash scripts/run_auto.sh
```

---

## 🎯 Prochaines Étapes

### Niveau 1 : Débutant
- [x] Installer le système
- [x] Tester en mode manuel
- [ ] Tester en mode automatique
- [ ] Collecter 100 images de déchets

### Niveau 2 : Intermédiaire
- [ ] Personnaliser le mapping
- [ ] Ajouter de nouvelles classes
- [ ] Créer un dataset custom
- [ ] Entraîner ton propre modèle

### Niveau 3 : Avancé
- [ ] Optimiser avec TensorRT
- [ ] Créer une interface graphique
- [ ] Ajouter des statistiques avancées
- [ ] Déployer sur plusieurs sites

---

## 📚 Documentation Complète

Pour plus de détails, consulte :

- [INSTALLATION.md](docs/INSTALLATION.md) - Installation détaillée
- [USAGE.md](docs/USAGE.md) - Guide d'utilisation complet
- [HARDWARE_SETUP.md](docs/HARDWARE_SETUP.md) - Schémas de câblage
- [YOLO_TRAINING.md](docs/YOLO_TRAINING.md) - Entraîner ton modèle
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Dépannage avancé

---

## 🆘 Besoin d'Aide ?

1. **Vérifier les logs :**
   ```bash
   cat data/logs/system.log
   ```

2. **Tester individuellement :**
   ```bash
   python3 scripts/test_hardware.py
   ```

3. **Réinstaller :**
   ```bash
   bash scripts/setup.sh
   ```

---

## ✅ Checklist de Vérification

Avant de démarrer, assure-toi que :

- [ ] La Jetson Nano est allumée
- [ ] L'Arduino est connecté via USB
- [ ] La caméra est branchée
- [ ] Tu as téléchargé un modèle YOLO
- [ ] Tu t'es déconnecté/reconnecté après l'installation
- [ ] Le test hardware passe tous les tests

**Si tout est ✅ → Tu es prêt ! 🎉**

```bash
bash scripts/run_auto.sh
```

---

**Bon tri ! 🗑️ ♻️ 🌱**