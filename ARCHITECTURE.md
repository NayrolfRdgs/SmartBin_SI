# 🏗️ Architecture Smart Bin SI - Explications Détaillées

## 📊 Vue d'Ensemble du Système

```
┌─────────────────────────────────────────────────────────────────┐
│                      SMART BIN SI                               │
│                                                                 │
│  [Caméra USB] ──▶ [YOLO] ──▶ [DB Manager] ──▶ [Arduino]       │
│                     │            │                │             │
│                Detection    Base de         Contrôle           │
│                Objet        Données          Servos            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎬 LES 3 CODES PRINCIPAUX

### 1️⃣ **yolo_detector.py** - Détection par Caméra
**Rôle :** Capture les images et détecte les objets

```
┌──────────────────────────────────────┐
│     YOLO DETECTOR                    │
├──────────────────────────────────────┤
│                                      │
│  📷 Caméra                           │
│   │                                  │
│   ▼                                  │
│  🖼️ Capture Frame                    │
│   │                                  │
│   ▼                                  │
│  🧠 YOLO Inference                   │
│   │                                  │
│   ▼                                  │
│  🎯 Détection                        │
│     ├─ Classe: "plastic_bottle"     │
│     ├─ Confiance: 0.92              │
│     └─ BBox: [x, y, w, h]           │
│   │                                  │
│   ▼                                  │
│  ✅ Si confiance > seuil             │
│   │                                  │
│   ▼                                  │
│  📤 Envoie "plastic_bottle"          │
│      vers DB Manager                 │
│                                      │
└──────────────────────────────────────┘
```

**Commandes :**
```bash
# Lancer la détection
python3 yolo_detector.py

# Contrôles pendant l'exécution
# q - Quitter
# s - Forcer le tri immédiat
# r - Réinitialiser le compteur
```

**Ce qu'il fait :**
1. Ouvre la caméra (USB ou CSI)
2. Capture les images en boucle
3. Passe chaque image au modèle YOLO
4. Détecte les objets avec leur classe et confiance
5. Filtre les détections (minimum 3 fois le même objet)
6. Envoie le nom de l'objet au DB Manager

---

### 2️⃣ **waste_classifier.py** - Gestionnaire de Base de Données + Logique
**Rôle :** Gère la DB et décide quelle couleur envoyer à l'Arduino

```
┌────────────────────────────────────────────┐
│     DB MANAGER (waste_classifier.py)       │
├────────────────────────────────────────────┤
│                                            │
│  📥 Reçoit: "plastic_bottle"               │
│   │                                        │
│   ▼                                        │
│  🔍 Cherche en Base de Données             │
│   │                                        │
│   ├─ ✅ Trouvé ?                           │
│   │   │                                    │
│   │   ▼                                    │
│   │  📊 waste_items.db                     │
│   │   ┌─────────────────────────────┐     │
│   │   │ plastic_bottle | yellow     │     │
│   │   │ cardboard      | yellow     │     │
│   │   │ banana_peel    | green      │     │
│   │   └─────────────────────────────┘     │
│   │   │                                    │
│   │   ▼                                    │
│   │  ✅ Retourne "yellow"                  │
│   │                                        │
│   └─ ❌ Pas trouvé ?                       │
│       │                                    │
│       ▼                                    │
│      🙋 Demande à l'utilisateur            │
│         "Dans quel bac ?"                  │
│       │                                    │
│       ▼                                    │
│      💾 Sauvegarde en DB                   │
│         plastic_bottle → yellow            │
│   │                                        │
│   ▼                                        │
│  📤 Envoie "yellow" à Arduino              │
│                                            │
└────────────────────────────────────────────┘
```

**Commandes :**
```bash
# Mode manuel (sans YOLO)
python3 waste_classifier.py

# Entrées pendant l'exécution
# [nom objet] - Trier un objet
# stats - Voir les statistiques
# quit - Quitter
```

**Ce qu'il fait :**
1. **Reçoit** le nom d'un objet (de YOLO ou saisie manuelle)
2. **Cherche** dans la base de données SQLite
   - Si trouvé → récupère la couleur
   - Si pas trouvé → demande à l'utilisateur
3. **Sauvegarde** les nouveaux objets en DB
4. **Envoie** la couleur à l'Arduino via série

**Structure de la Base de Données :**
```sql
CREATE TABLE waste_classification (
    item_name TEXT PRIMARY KEY,      -- "plastic_bottle"
    bin_color TEXT NOT NULL,         -- "yellow"
    created_at TIMESTAMP,            -- "2026-01-28 14:30:00"
    usage_count INTEGER DEFAULT 1   -- 42 (nombre de fois trié)
);
```

---

### 3️⃣ **smart_bin_controller.ino** - Contrôle des Servomoteurs
**Rôle :** Contrôle les mouvements physiques de la plateforme

```
┌─────────────────────────────────────────────┐
│     ARDUINO CONTROLLER                      │
├─────────────────────────────────────────────┤
│                                             │
│  📥 Reçoit: "yellow\n"                      │
│   │                                         │
│   ▼                                         │
│  🎯 Décode la commande                      │
│   │                                         │
│   ├─ yellow → 150° rotation, bascule HAUT  │
│   ├─ green  → 90°  rotation, bascule BAS   │
│   └─ brown  → 30°  rotation, bascule HAUT  │
│   │                                         │
│   ▼                                         │
│  ⚙️ SÉQUENCE DE TRI                         │
│   │                                         │
│   ├─ PHASE 1: ROTATION                     │
│   │   Servo orientation → 150°             │
│   │   Délai 1000ms                         │
│   │                                         │
│   ├─ PHASE 2: VIDAGE                       │
│   │   Servo bascule → 20° (HAUT)           │
│   │   Délai 600ms                          │
│   │                                         │
│   ├─ PHASE 3: VIBRATION (4x)               │
│   │   Bascule 20° → 40° → 20°              │
│   │   Délai 150ms entre chaque             │
│   │                                         │
│   └─ PHASE 4: RETOUR                       │
│       Servo bascule → 90°                  │
│       Servo rotation → 90°                 │
│   │                                         │
│   ▼                                         │
│  ✅ Envoie "✓ Termine"                      │
│                                             │
└─────────────────────────────────────────────┘
```

**Upload sur Arduino :**
```bash
# Dans Arduino IDE
1. Ouvrir smart_bin_controller.ino
2. Sélectionner : Outils > Carte > Arduino Uno
3. Sélectionner : Outils > Port > /dev/ttyACM0
4. Cliquer sur : Téléverser (→)
```

**Ce qu'il fait :**
1. **Écoute** le port série USB
2. **Reçoit** une commande couleur ("yellow", "green", "brown")
3. **Exécute** la séquence de mouvements :
   - Rotation vers le bon bac
   - Basculement pour vider
   - Secousses pour bien vider
   - Retour en position neutre
4. **Confirme** la fin du tri

**Configuration Hardware :**
```
Arduino Uno
├─ Pin 10 → Servo Orientation (rotation gauche/droite)
├─ Pin 9  → Servo Bascule (inclinaison haut/bas)
└─ USB    → Jetson Nano (/dev/ttyACM0)

Servos MG996R
├─ VCC → Alimentation externe 5V/3A
├─ GND → Masse commune Arduino + Alim
└─ Signal → Pins PWM Arduino
```

---

## 🔄 FLUX COMPLET DE DONNÉES

### Scénario : Détection d'une bouteille en plastique

```
┌─────────────┐
│   ÉTAPE 1   │  Caméra capture l'image
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  yolo_detector.py                                   │
│  -------------------------------------------------- │
│  📷 Frame capturée                                  │
│  🧠 YOLO inference                                  │
│  🎯 Détection: plastic_bottle (conf: 0.92)          │
│  ✅ 3 détections consécutives → valide              │
│  📤 Envoie "plastic_bottle" au DB Manager           │
└──────┬──────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│   ÉTAPE 2   │  Vérification en base de données
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  waste_classifier.py                                │
│  -------------------------------------------------- │
│  📥 Reçoit: "plastic_bottle"                        │
│  🔍 SELECT bin_color FROM waste_classification      │
│      WHERE item_name = 'plastic_bottle'             │
│  ✅ Résultat: "yellow"                              │
│  📤 Envoie "yellow\n" via port série                │
└──────┬──────────────────────────────────────────────┘
       │
       │ USB Serial (/dev/ttyACM0, 9600 bauds)
       │
       ▼
┌─────────────┐
│   ÉTAPE 3   │  Exécution physique du tri
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  smart_bin_controller.ino (Arduino)                 │
│  -------------------------------------------------- │
│  📥 Serial.read(): "yellow\n"                       │
│  🎯 if (command == "yellow")                        │
│  ⚙️  executeSortingSequence(150°, "YELLOW", 0)      │
│                                                     │
│  Phase 1: orientationServo.write(150°)             │
│           delay(1000ms)                            │
│                                                     │
│  Phase 2: tiltServo.write(20°) // Bascule HAUT    │
│           delay(600ms)                             │
│                                                     │
│  Phase 3: Vibrations 4x                            │
│           tiltServo: 20° → 40° → 20°               │
│                                                     │
│  Phase 4: tiltServo.write(90°)                     │
│           orientationServo.write(90°)              │
│                                                     │
│  📤 Serial.println("✓ Termine")                     │
└─────────────────────────────────────────────────────┘
```

---

## 📁 STRUCTURE DES FICHIERS ESSENTIELS

```
SmartBin_SI/
│
├── 🐍 yolo_detector.py          ← CODE 1: Détection YOLO
│   └─ Fonction: Détecter objets via caméra
│
├── 🐍 waste_classifier.py       ← CODE 2: Gestion DB + Logique
│   └─ Fonction: Mapper objet → couleur
│
├── 🤖 smart_bin_controller.ino  ← CODE 3: Contrôle Arduino
│   └─ Fonction: Mouvements servos
│
├── ⚙️ config.py                 ← Configuration centrale
│   └─ Fonction: Paramètres (seuils, ports, mapping)
│
├── 💾 waste_items.db            ← Base de données SQLite
│   └─ Fonction: Stockage objet → couleur
│
└── 🧠 models/
    └── best.pt                  ← Modèle YOLO entraîné
        └─ Fonction: Poids du réseau de neurones
```

---

## 🎮 MODES D'UTILISATION

### Mode 1️⃣ : Manuel (Sans Caméra)
**Pour tester sans YOLO**

```bash
python3 waste_classifier.py
```

**Flux :**
```
Utilisateur tape "plastic_bottle"
    ↓
waste_classifier.py cherche en DB
    ↓
Si trouvé: envoie "yellow" à Arduino
Si pas trouvé: demande couleur, sauvegarde, envoie
    ↓
Arduino exécute le tri
```

### Mode 2️⃣ : Automatique (Avec Caméra)
**Détection YOLO temps réel**

```bash
python3 yolo_detector.py
```

**Flux :**
```
Caméra capture frame
    ↓
YOLO détecte "plastic_bottle"
    ↓
3 détections consécutives validées
    ↓
Appelle waste_classifier.get_bin_color()
    ↓
waste_classifier cherche en DB → "yellow"
    ↓
Envoie "yellow" à Arduino
    ↓
Arduino exécute le tri
```

---

## 🔧 LES FICHIERS AUXILIAIRES

### config.py
**Rôle :** Centraliser TOUS les paramètres

```python
# Au lieu de changer dans chaque fichier
# Tu changes UNE FOIS ici

MODEL_NAME = "yolov8n_waste.pt"  # Quel modèle
CONFIDENCE_THRESHOLD = 0.6        # Seuil de confiance
ARDUINO_PORT = "/dev/ttyACM0"     # Port série
CAMERA_SOURCE = 0                 # Quelle caméra

WASTE_TO_BIN_MAPPING = {
    "plastic": "yellow",
    "cardboard": "yellow",
    # ...
}
```

### setup.sh
**Rôle :** Installer automatiquement TOUT

```bash
# Au lieu de faire 20 commandes manuelles
# Tu lances UNE FOIS :
bash setup.sh

# Ça installe :
# - Python + dépendances
# - PyTorch pour Jetson
# - YOLOv5/v8
# - Configure les permissions série
# - Crée la structure de dossiers
```

### download_model.py
**Rôle :** Télécharger un modèle YOLO pré-entraîné

```bash
python3 download_model.py

# Propose 3 modèles :
# [1] Nano (rapide, 20 FPS)
# [2] Small (moyen, 12 FPS)
# [3] Medium (précis, 5 FPS)

# Télécharge depuis Roboflow
# Copie dans models/
```

---

## 💡 POURQUOI SÉPARER LES CODES ?

### ❌ Sans séparation (tout dans 1 fichier)
```python
# Un énorme fichier de 2000 lignes
# Difficile à maintenir
# Difficile à débugger
# Impossible de tester séparément
```

### ✅ Avec séparation (3 fichiers distincts)
```python
# yolo_detector.py - 300 lignes
# waste_classifier.py - 200 lignes
# smart_bin_controller.ino - 150 lignes

# Avantages :
# - Chaque fichier a UNE responsabilité
# - Tu peux tester chaque partie séparément
# - Facile à comprendre
# - Facile à modifier
# - Réutilisable
```

---

## 🧪 COMMENT TESTER CHAQUE PARTIE

### Test 1 : Arduino seul
```bash
# Ouvre Arduino IDE
# Upload smart_bin_controller.ino
# Ouvre le Moniteur Série
# Tape : yellow
# → Les servos doivent bouger
```

### Test 2 : DB Manager seul
```bash
python3 waste_classifier.py

# Entre : plastic_bottle
# Si nouveau : demande couleur
# Si connu : tri direct
```

### Test 3 : YOLO seul
```bash
python3 yolo_detector.py

# Montre un objet à la caméra
# Vérifie la détection à l'écran
# (Sans Arduino = pas de mouvement)
```

### Test 4 : Système complet
```bash
# 1. Arduino uploadé
# 2. Lance YOLO
python3 yolo_detector.py

# 3. Montre un déchet
# → Détection + Tri automatique
```

---

## 🎯 RÉSUMÉ ULTRA-SIMPLE

| Fichier | Rôle | Entrée | Sortie |
|---------|------|--------|--------|
| **yolo_detector.py** | 👁️ Voir | Image caméra | Nom objet |
| **waste_classifier.py** | 🧠 Décider | Nom objet | Couleur bac |
| **smart_bin_controller.ino** | 🤖 Agir | Couleur bac | Mouvement servos |

**Chaîne complète :**
```
Caméra → YOLO → DB → Arduino → Servos → Tri !
```

C'est tout ! 🎉