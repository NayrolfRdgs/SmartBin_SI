# 📦 Guide d'Installation Complet - Smart Bin SI

> Guide détaillé pour installer Smart Bin SI avec tous les prérequis et configurations nécessaires.

**Durée estimée** : 20-30 minutes  
**Dernière mise à jour** : Février 2026

---

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Installation Étape par Étape](#installation-étape-par-étape)
3. [Configuration Arduino](#configuration-arduino)
4. [Première Utilisation](#première-utilisation)
5. [Vérification d'Installation](#vérification-dinstallation)
6. [Troubleshooting Installation](#troubleshooting-installation)

---

## ✅ Prérequis

### Système d'Exploitation

- **Windows 10/11**
- **Linux** (Ubuntu 20.04+)
- **macOS** (10.14+)

### Logiciels Nécessaires

| Logiciel | Version Min | Téléchargement |
|----------|-------------|---|
| Python | 3.8 | https://www.python.org |
| Arduino IDE | 2.0+ | https://www.arduino.cc/en/software |
| Git (optionnel) | 2.30+ | https://git-scm.com |

### Matériel Requis

**Obligatoire :**
- 1x Arduino Uno (ou compatible)
- 1x Câble USB Arduino → Ordinateur
- 2x Servomoteurs SG90 (pour les portes des bacs)

**Optionnel (pour mode automatique) :**
- 1x Caméra USB (webcam standard)
- 1x Raspberry Pi ou Jetson Nano (pour embarqué)

### Espace Disque

- **Minimum** : 2 GB
- **Recommandé** : 10 GB (pour modèles YOLO et données)

---

## 🔧 Installation Étape par Étape

### Étape 1 : Télécharger le Projet

#### Option A : Avec Git
```bash
git clone https://github.com/sayfox8/SmartBin_SI.git
cd SmartBin_SI
```

#### Option B : Sans Git
1. Aller sur https://github.com/sayfox8/SmartBin_SI
2. Cliquer sur **Code** → **Download ZIP**
3. Extraire l'archive
4. Ouvrir le terminal dans le dossier extrait

### Étape 2 : Installer Python

#### Vérifier que Python est Installé

```bash
python --version
```

Vous devez voir : `Python 3.8.x` ou plus récent.

**Si Python n'est pas installé :**
1. Aller sur https://www.python.org
2. Télécharger Python 3.10 ou 3.11
3. **Cocher "Add Python to PATH"** pendant l'installation
4. Redémarrer l'ordinateur
5. Vérifier à nouveau : `python --version`

### Étape 3 : Créer un Environnement Virtuel

L'environnement virtuel isole les dépendances du projet.

#### Windows
```bash
# Créer l'environnement
python -m venv .venv

# Activer l'environnement
.venv\Scripts\activate

# Vous devriez voir : (.venv) C:\...>
```

#### Linux / macOS
```bash
# Créer l'environnement
python3 -m venv .venv

# Activer l'environnement
source .venv/bin/activate

# Vous devriez voir : (.venv) user@machine:~$
```

### Étape 4 : Mettre à Jour pip

```bash
python -m pip install --upgrade pip
```

### Étape 5 : Installer les Dépendances

#### Installation Standard

```bash
pip install -r requirements.txt
```

**Packages installés :**
```
pyserial>=3.5              # Communication série Arduino
numpy>=1.19.0              # Calculs matriciels
Pillow>=8.0.0              # Traitement d'images
opencv-python>=4.5.0       # Vision par ordinateur
matplotlib>=3.3.0          # Graphiques
pandas>=1.3.0              # Gestion de données
```

#### Installation pour Interface Web

Si vous voulez utiliser le tableau de bord :

```bash
pip install Flask
pip install psutil          # Monitoring système
```

#### Installation GPU (NVIDIA uniquement)

Si vous avez une **GPU NVIDIA** :

```bash
# Installer CUDA Toolkit 11.8
# Télécharger depuis : https://developer.nvidia.com/cuda-11-8-0-download-archive

# Ensuite installer PyTorch avec CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Étape 6 : Vérifier l'Installation

```bash
# Vérifier que tous les packages sont installés
pip list

# Tester les imports principaux
python -c "import cv2; import numpy; import serial; print('✓ Tous les imports OK')"
```

**Vous devriez voir :**
```
✓ Tous les imports OK
```

---

## ⚙️ Configuration Arduino

### Étape 1 : Installer Arduino IDE

1. Télécharger depuis https://www.arduino.cc/en/software
2. Installer avec les paramètres par défaut
3. Lancer Arduino IDE

### Étape 2 : Téléverser le Code

1. **Ouvrir le fichier** : `arduino/smart_bin_controller.ino`
2. **Dans Arduino IDE** : Fichier → Ouvrir → sélectionner le fichier
3. **Vérifier le port** :
   - Outils → Port → sélectionner **COM3** (Windows) ou **/dev/ttyACM0** (Linux)
   - Si aucun port n'apparaît : installer les drivers CH340
4. **Téléverser** : Cliquer le bouton ➡️ ou Sketch → Téléverser

**Succès quand vous voyez :**
```
Téléversement effectué
Vérification…
✓ Vérification terminée
```

### Étape 3 : Tester Arduino Manuellement

1. Outils → Moniteur série
2. Définir le baud : **9600**
3. Entrer `yellow` ou `green` ou `brown`
4. Appuyer sur Entrée
5. Vérifier que les servos bougent

---

## 🚀 Première Utilisation

### Test 1 : Mode Manuel (Sans Caméra)

Le plus simple pour vérifier que tout fonctionne :

```bash
# Activer l'environnement (si pas déjà activé)
# Windows :
.venv\Scripts\activate
# Linux/macOS :
source .venv/bin/activate

# Lancer le mode manuel
python src/waste_classifier.py
```

**Vous devriez voir :**
```
🤖 SMART BIN SI - MODE MANUEL (sans caméra)
Tape le nom d'un objet pour lancer le tri. 'stats' = statistiques, 'quit' = quitter.

Objet > 
```

**Tester avec :**
```
plastic_bottle
→ ✓ Tri vers bac yellow

banana
→ ✓ Tri vers bac green

tissue
→ ✓ Tri vers bac brown

stats
→ Affiche les statistiques

quit
→ Quitter
```

### Test 2 : Interface Web (Optionnel)

```bash
# Dans le dossier admin_interface
cd admin_interface

# Installer les dépendances
pip install Flask psutil

# Lancer l'application
python app.py
```

Ouvrir le navigateur : **http://localhost:5000**

---

## ✔️ Vérification d'Installation

### Checklist Finale

- [ ] Python 3.8+ installé : `python --version`
- [ ] Environnement virtuel activé : voir `(.venv)` avant le prompt
- [ ] Packages installés : `pip list` affiche tous les packages
- [ ] Arduino IDE installé et fonctionnel
- [ ] Arduino téléversé : code chargé sans erreur
- [ ] Mode manuel fonctionne : `python src/waste_classifier.py` démarrt correctement
- [ ] Caméra reconnue (optionnel) : se connecte sans erreur

### Tests de Diagnostic

```bash
# Test 1 : Python correctement configuré
python -c "import sys; print(f'Python {sys.version}')"

# Test 2 : OpenCV fonctionne
python -c "import cv2; print(f'OpenCV {cv2.__version__}')"

# Test 3 : Connexion série possible
python -c "import serial; print('Série OK')"

# Test 4 : Base de données créée
python -c "from src.waste_classifier import init_database; init_database(); print('DB créée')"
```

---

## 🆘 Troubleshooting Installation

### Problème : "Python not found" ou "command not recognized"

**Cause** : Python n'est pas dans le PATH système.

**Solutions** :
1. Réinstaller Python en cochant **"Add Python to PATH"**
2. Redémarrer l'ordinateur
3. Ou utiliser le chemin complet : `C:\Python310\python.exe --version`

### Problème : "ModuleNotFoundError" pour pyserial ou opencv

**Cause** : Les packages n'ont pas été installés dans le bon environnement.

**Solutions** :
```bash
# Vérifier que l'environnement est bien activé (voir (.venv))
# Sinon l'activer :
.venv\Scripts\activate

# Réinstaller les dépendances
pip install --force-reinstall -r requirements.txt
```

### Problème : Arduino IDE refuse de téléverser

**Cause** : Mauvais port ou drivers manquants.

**Solutions** :
1. Vérifier le port dans Outils → Port (doit voir COM3, COM4 etc ou /dev/ttyACM0)
2. Installer les drivers :
   - **CH340** (Clones Arduino) : https://github.com/nodemcu/ch340g-ch34g-ch34x-mac-linux-driver
   - **Officiel** : installer Arduino IDE qui inclut les drivers
3. Redémarrer Arduino IDE

### Problème : "La caméra ne se connecte pas"

**Cause** : Permissions ou caméra non reconnue.

**Solutions** :
```bash
# Tester les caméras disponibles
python -c "import cv2; cap = cv2.VideoCapture(0); print('Caméra 0:', cap.isOpened())"

# Essayer la caméra 1
python -c "import cv2; cap = cv2.VideoCapture(1); print('Caméra 1:', cap.isOpened())"

# Donner les permissions (Linux)
sudo usermod -a -G video $USER
```

### Problème : Erreur "CUDA not available"

**Cause** : GPU NVIDIA non détecté (normal si vous n'avez pas de GPU).

**Solution** :
```bash
# Vérifier la version GPU installée
python -c "import torch; print(f'CUDA disponible: {torch.cuda.is_available()}')"

# Si False, c'est normal, PyTorch utilisera le CPU
```

### Problème : "pip: command not found"

**Cause** : pip n'est pas dans le PATH.

**Solution** :
```bash
# Utiliser le module Python
python -m pip install -r requirements.txt
```

---

## 📚 Prochaines Étapes

Une fois l'installation terminée :

1. **Lire** [docs/CONFIGURATION.md](CONFIGURATION.md) pour personnaliser votre système
2. **Consulter** [docs/UTILISATION.md](UTILISATION.md) pour apprendre les modes
3. **Suivre** [docs/APPENTISSAGE.md](APPENTISSAGE.md) pour entraîner le modèle
4. **En cas de problème** : voir [docs/DEPANNAGE.md](../DEPANNAGE.md)

---

**Installation réussie ? Bravo ! 🎉**  
Vous êtes prêt à utiliser Smart Bin SI.

