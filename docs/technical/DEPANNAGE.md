# 🔧 Guide de Dépannage - Smart Bin SI

> Solutions aux problèmes courants et questions fréquemment posées.

**Dernière mise à jour** : Février 2026

---

## 📋 Table des Matières

1. [Problèmes d'Installation](#problèmes-dinstallation)
2. [Problèmes Arduino](#problèmes-arduino)
3. [Problèmes Caméra](#problèmes-caméra)
4. [Problèmes YOLO/Détection](#problèmes-yolodetection)
5. [Problèmes Base de Données](#problèmes-base-de-données)
6. [Problèmes de Performance](#problèmes-de-performance)
7. [FAQ Générale](#faq-générale)

---

## 📦 Problèmes d'Installation

### ❌ "Python not found" / "command not recognized"

**Symptôme** :
```
'python' is not recognized as an internal or external command
```

**Causes** :
- Python n'est pas installé
- Python n'est pas dans le PATH système

**Solutions** :

1. **Vérifier que Python est installé** :
```bash
python --version
```

2. **Si non installé** :
   - Télécharger Python 3.10+ depuis https://www.python.org
   - **Très important** : cocher "Add Python to PATH" pendant l'installation
   - Redémarrer l'ordinateur

3. **Si installé mais non reconnu** :
   - Réinstaller en cochant "Add Python to PATH"
   - Ou utiliser le chemin complet : `C:\Python310\python.exe --version`

---

### ❌ "ModuleNotFoundError: No module named 'cv2'"

**Symptôme** :
```
ModuleNotFoundError: No module named 'cv2'
```

**Causes** :
- Packages non installés
- Mauvais environnement virtuel

**Solutions** :

1. **Vérifier que l'environnement virtuel est activé** :
```bash
# Vous devez voir (.venv) au début du prompt
# Sinon, l'activer :

# Windows :
.venv\Scripts\activate

# Linux/macOS :
source .venv/bin/activate
```

2. **Réinstaller les dépendances** :
```bash
pip install --force-reinstall -r requirements.txt
```

3. **Installer le package spécifique** :
```bash
pip install opencv-python
```

---

### ❌ "No module named 'serial'"

**Symptôme** :
```
ModuleNotFoundError: No module named 'serial'
```

**Solution** :
```bash
pip install pyserial
```

---

### ❌ "Permission denied" (Linux/macOS)

**Symptôme** :
```
PermissionError: [Errno 13] Permission denied
```

**Cause** : Permissions insuffisantes

**Solution** :
```bash
# Donner les permissions sur le répertoire
chmod -R 755 ~/SmartBin_SI

# Ou exécuter avec sudo (moins recommandé)
sudo python src/waste_classifier.py
```

---

## 🤖 Problèmes Arduino

### ❌ "Arduino not found" / "Arduino non détecté"

**Symptôme** :
```
⚠ Arduino non détecté (port not found) - mode simulation
```

**Causes** :
- Arduino non connecté
- Mauvais port configuré
- Drivers manquants

**Solutions** :

1. **Vérifier la connexion physique** :
   - Brancher l'Arduino avec un câble USB valide
   - Vérifier que le câble n'est pas cassé
   - Essayer un autre port USB

2. **Trouver le bon port** :

**Windows** :
```bash
# Option 1 : Via Python
python -m serial.tools.list_ports

# Option 2 : Gestionnaire des périphériques
# Chercher "Ports (COM et LPT)" dans le Gestionnaire
# Voir les numéros COM disponibles
```

**Linux** :
```bash
# Voir les ports
ls -la /dev/tty*

# Généralement /dev/ttyACM0 ou /dev/ttyUSB0
```

**macOS** :
```bash
ls -la /dev/tty.usbserial*
ls -la /dev/tty.wchusbserial*
```

3. **Mettre à jour config.py** :
```python
# Remplacer le port trouvé
ARDUINO_PORT = 'COM3'        # Windows (adapter le numéro)
ARDUINO_PORT = '/dev/ttyACM0' # Linux/macOS
```

4. **Installer les drivers** :

**Si Arduino clone (CH340)** :
- Télécharger les drivers : https://github.com/nodemcu/ch340g-ch34g-ch34x-mac-linux-driver
- Installer et redémarrer

**Arduino officiel** :
- Les drivers viennent avec Arduino IDE

---

### ❌ Arduino connecté mais ne répond pas

**Symptôme** :
```
✓ Arduino connecté
[mais pas de mouvement des servos]
```

**Causes** :
- Code Arduino mal téléversé
- Problème d'alimentation
- Servos mal connectés

**Solutions** :

1. **Vérifier que le code Arduino est chargé** :
   - Ouvrir Arduino IDE
   - Outils → Port → Sélectionner le port Arduino
   - Sketch → Téléverser
   - Si pas d'erreurs : code chargé ✓

2. **Tester les servos manuellement** :
```cpp
// Créer un sketch de test dans Arduino IDE
#include <Servo.h>

Servo servo1;

void setup() {
  servo1.attach(9);
}

void loop() {
  servo1.write(90);
  delay(1000);
  servo1.write(0);
  delay(1000);
}
```

3. **Vérifier l'alimentation** :
   - Les servos consomment beaucoup
   - Utiliser une alimentation externe 5V/2A minimum
   - Vérifier les connexions +5V et GND

4. **Vérifier les câbles servos** :
   - Rouge = +5V
   - Noir = GND
   - Jaune/Orange = Signal (broches 9, 10, 11)

---

### ❌ "Port déjà utilisé" / "Address already in use"

**Symptôme** :
```
SerialException: port is already in use
```

**Cause** : Arduino IDE ou autre programme utilise le port

**Solution** :

1. **Fermer Arduino IDE**
2. **Ou terminer le processus Python** :

**Windows** :
```bash
tasklist | findstr python
taskkill /IM python.exe /F
```

**Linux/macOS** :
```bash
killall python
```

---

## 📷 Problèmes Caméra

### ❌ Caméra non détectée

**Symptôme** :
```
cv2.error: (-215) empty in function cvCaptureFromCAM
# Ou : Caméra 0 non trouvée
```

**Causes** :
- Caméra non connectée
- Mauvais numéro de caméra
- Caméra utilisée par autre application

**Solutions** :

1. **Vérifier la connexion** :
   - Brancher la caméra USB
   - Vérifier que le câble est bien inséré

2. **Trouver le bon numéro de caméra** :
```python
import cv2

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Caméra {i} : OK")
        cap.release()
    else:
        print(f"Caméra {i} : pas trouvée")
```

3. **Mettre à jour config.py** :
```python
CAMERA_SOURCE = 1  # Au lieu de 0 (essayer différents numéros)
```

4. **Libérer la caméra** :
```bash
# Si autre application la bloque :
# - Fermer Zoom, Teams, navigateur (fermez les onglets vidéo)
# - Redémarrer l'ordinateur
```

---

### ❌ Image floue / qualité mauvaise

**Symptôme** :
```
Détection manquée / images pixelisées
```

**Causes** :
- Résolution trop basse
- Caméra mal focalisée
- Mauvaise lumière

**Solutions** :

1. **Augmenter la résolution** :
```python
# config.py
FRAME_WIDTH = 1280    # Au lieu de 640
FRAME_HEIGHT = 720    # Au lieu de 480
```

2. **Nettoyer la caméra** :
   - Utiliser un chiffon doux et sec
   - Enlever les poussières
   - Vérifier que la lentille est claire

3. **Améliorer la lumière** :
   - Utiliser une lampe LED
   - Éviter les contre-jours
   - Placer l'objet bien visible

4. **Réduire la distance** :
   - Placer la caméra à 30-50cm de l'objet
   - Pas trop prêt, pas trop loin

---

### ❌ Caméra Raspberry Pi (CSI) ne fonctionne pas

**Symptôme** :
```
[cv2 error ou lecture impossible]
```

**Solution** :

1. **Vérifier que USE_CSI_CAMERA = True** dans config.py

2. **Installer libcamera** (Raspberry Pi OS moderne) :
```bash
sudo apt update
sudo apt install -y python3-libcamera python3-picamera2
```

3. **Ou installer picamera pour ancien OS** :
```bash
pip install picamera
```

---

## 🧠 Problèmes YOLO/Détection

### ❌ "Model file not found"

**Symptôme** :
```
FileNotFoundError: models/best.pt not found
```

**Cause** : Modèle YOLO manquant

**Solutions** :

1. **Vérifier que le fichier existe** :
```bash
# Windows
dir models\

# Linux/macOS
ls -la models/
```

2. **Si absent, télécharger le modèle** :
   - Utiliser un modèle pré-entraîné YOLO
   - Ou réentraîner : voir [docs/ENTRAINEMENT_IA.md](ENTRAINEMENT_IA.md)

3. **Mettre le fichier au bon endroit** :
```
models/
└── best.pt
```

---

### ❌ Pas de détections / Toujours vide

**Symptôme** :
```
[Aucune détection même avec objets visibles]
```

**Causes** :
- Confiance trop haute
- Objet pas entraîné
- Lumière insuffisante

**Solutions** :

1. **Réduire le seuil de confiance** :
```python
# config.py
CONFIDENCE_THRESHOLD = 0.3  # Au lieu de 0.6
```

2. **Vérifier que l'objet est entraîné** :
   - Le modèle ne détecte que ce qu'il a vu
   - Si c'est un nouvel objet, il faut le réentraîner
   - Voir [docs/ENTRAINEMENT_IA.md](ENTRAINEMENT_IA.md)

3. **Améliorer la lumière** :
   - Ajouter une lampe
   - Utiliser la lumière naturelle
   - Éviter les ombres

---

### ❌ Trop de faux positifs / détections erronées

**Symptôme** :
```
Détection: random_noise (confiance: 0.45)
Détection: shadow (confiance: 0.38)
```

**Causes** :
- Confiance trop basse
- Bruit/lumière crée des faux positifs

**Solutions** :

1. **Augmenter le seuil** :
```python
# config.py
CONFIDENCE_THRESHOLD = 0.75  # Au lieu de 0.6
```

2. **Augmenter MIN_DETECTIONS** :
```python
MIN_DETECTIONS = 5  # Au lieu de 1 (attendre 5 détections identiques)
```

3. **Augmenter AUTO_SORT_DELAY** :
```python
AUTO_SORT_DELAY = 5.0  # Attendre plus longtemps
```

4. **Réentraîner le modèle** :
   - Ajouter des images de bruit
   - Voir [docs/ENTRAINEMENT_IA.md](ENTRAINEMENT_IA.md)

---

### ❌ "CUDA out of memory"

**Symptôme** :
```
RuntimeError: CUDA out of memory
```

**Cause** : GPU NVIDIA surchargé

**Solutions** :

1. **Réduire la résolution** :
```python
FRAME_WIDTH = 320   # Au lieu de 640
FRAME_HEIGHT = 240  # Au lieu de 480
```

2. **Réduire batch size** :
```python
# Dans yolo_detector.py (si applicable)
batch_size = 4  # Réduire
```

3. **Utiliser CPU au lieu de GPU** :
```python
# Dans yolo_detector.py
device = 'cpu'  # Au lieu de 'cuda'
```

---

## 💾 Problèmes Base de Données

### ❌ "Database locked" / "Base de données verrouillée"

**Symptôme** :
```
sqlite3.OperationalError: database is locked
```

**Cause** : Deux processus accèdent à la DB simultanément

**Solution** :

```bash
# Arrêter tous les processus Python
# Windows :
taskkill /IM python.exe /F

# Linux/macOS :
killall python

# Puis redémarrer
python src/waste_classifier.py
```

---

### ❌ Base de données corrompue

**Symptôme** :
```
sqlite3.DatabaseError: database disk image is malformed
```

**Solutions** :

1. **Restaurer depuis backup** :
```bash
cp data/waste_items.db.backup data/waste_items.db
```

2. **Ou créer une nouvelle DB** :
```bash
# Sauvegarder les données
mv data/waste_items.db data/waste_items.db.old

# La DB sera recréée vierge au prochain lancement
python src/waste_classifier.py
```

3. **Récupérer les données** :
```bash
# Exporter l'ancienne DB si possible
sqlite3 data/waste_items.db.old .dump > backup.sql
```

---

### ❌ DB trop volumineuse

**Symptôme** :
```
data/waste_items.db > 500 MB
```

**Cause** : Trop d'historique de détections

**Solution** :

1. **Archiver les vieux enregistrements** :
```bash
# Créer une copie avant modifications
cp data/waste_items.db data/waste_items.db.backup

# Supprimer les détections de plus de 30 jours
sqlite3 data/waste_items.db
DELETE FROM sorting_history WHERE date(timestamp) < date('now', '-30 days');
VACUUM;
```

2. **Ou vider complètement l'historique** :
```sql
DELETE FROM sorting_history;
VACUUM;
```

---

## ⚡ Problèmes de Performance

### ❌ Application très lente / CPU à 100%

**Symptôme** :
```
CPU usage: 95%
Temps de détection: 5 secondes
```

**Causes** :
- Résolution trop haute
- Trop de processus
- GPU non utilisé

**Solutions** :

1. **Réduire la résolution** :
```python
# config.py
FRAME_WIDTH = 320    # Au lieu de 640
FRAME_HEIGHT = 240   # Au lieu de 480
```

2. **Désactiver l'affichage** :
```python
SHOW_DISPLAY = False
```

3. **Désactiver l'apprentissage** :
```python
LEARNING_MODE = False
SAVE_IMAGES = False
```

4. **Utiliser GPU si disponible** :
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

5. **Fermer les autres applications** :
   - Navigateur web
   - IDEs (VS Code, PyCharm)
   - Antivirus

---

### ❌ Beaucoup de lag / vidéo saccadée

**Symptôme** :
```
FPS très bas (< 5 FPS)
```

**Cause** : Performances insuffisantes

**Solutions** :

1. **Réduire drastiquement la résolution** :
```python
FRAME_WIDTH = 160
FRAME_HEIGHT = 120
```

2. **Augmenter auto_sort_delay** :
```python
AUTO_SORT_DELAY = 10.0  # Laisser plus de temps
```

3. **Réduire MIN_DETECTIONS** :
```python
MIN_DETECTIONS = 1
```

4. **Utiliser une meilleure machine** :
   - Upgrader à Jetson Nano
   - Ou GPU NVIDIA

---

## ❓ FAQ Générale

### Q : Combien de temps pour l'installation ?
**R** : 20-30 minutes si tout va bien. Plus long si problèmes de drivers.

### Q : Comment réentraîner le modèle ?
**R** : Voir [docs/ENTRAINEMENT_IA.md](ENTRAINEMENT_IA.md)

### Q : Peut-on utiliser sur Raspberry Pi ?
**R** : Oui, mais lent. Mieux sur Jetson Nano ou ordinateur classique.

### Q : Les images d'apprentissage prennent trop de place ?
**R** : Archiver régulièrement : `mv data/training_images/*.jpg archive/`

### Q : Comment ajouter une nouvelle couleur de bac ?
**R** : Éditer `config.py` et ajouter dans `VALID_BINS` et `WASTE_TO_BIN_MAPPING`

### Q : Le tri ne marche qu'en mode manuel, pas automatique ?
**R** : Vérifier la confiance YOLO. Réduire `CONFIDENCE_THRESHOLD` à 0.5.

### Q : Comment relancer l'application si elle crash ?
**R** : 
```bash
# Voir le dernier message d'erreur
# Consulter logs : data/logs/
# Redémarrer : python src/yolo_detector.py
```

---

## 🆘 Besoin d'Aide Supplémentaire ?

Si votre problème n'est pas répertorié :

1. **Consulter les logs** :
```bash
cat data/logs/system.log
tail -f data/logs/system.log
```

2. **Ouvrir une issue GitHub** :
   https://github.com/sayfox8/SmartBin_SI/issues

3. **Vérifier la documentation** :
   - [docs/ARCHITECTURE.md](ARCHITECTURE.md)
   - [docs/CONFIGURATION.md](CONFIGURATION.md)
   - [docs/INSTALLATION.md](INSTALLATION.md)

---

**Dernière ressource** : Lire les messages d'erreur attentivement !  
Ils contiennent généralement la solution exacte. 🔍

