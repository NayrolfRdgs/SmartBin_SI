# 💻 Guide d'Utilisation - Smart Bin SI

> Guide complet pour utiliser Smart Bin SI dans ses différents modes.

**Dernière mise à jour** : Février 2026

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Mode Manuel](#mode-manuel)
3. [Mode Automatique (YOLO)](#mode-automatique-yolo)
4. [Interface Web](#interface-web)
5. [Commandes CLI](#commandes-cli)
6. [Astuces et Bonnes Pratiques](#astuces-et-bonnes-pratiques)

---

## 🎯 Vue d'Ensemble

Smart Bin SI propose **3 modes d'utilisation** :

| Mode | Description | Caméra | Usage |
|------|-------------|--------|-------|
| **Manuel** | Saisie texte des objets | ❌ Non | Test, apprentissage manuel |
| **Automatique** | Détection YOLO en temps réel | ✅ Oui | Production, utilisation réelle |
| **Web** | Tableau de bord + monitoring | ❌ Non | Supervision, statistiques |

---

## 🎮 Mode Manuel

### Démarrage

Le mode le plus simple, parfait pour tester sans caméra.

```bash
# Activer l'environnement
# Windows :
.venv\Scripts\activate
# Linux/macOS :
source .venv/bin/activate

# Lancer le mode manuel
python src/waste_classifier.py
```

### Affichage

```
🤖 SMART BIN SI - MODE MANUEL (sans caméra)
Tape le nom d'un objet pour lancer le tri. 'stats' = statistiques, 'quit' = quitter.

Objet >
```

### Commandes Disponibles

#### 1. Entrer un Nom d'Objet

```
Objet > plastic_bottle
✓ Tri vers bac yellow

Objet > banana
✓ Tri vers bac green

Objet > paper_towel
✓ Tri vers bac brown

Objet > unknown_item
📦 Objet inconnu : 'unknown_item'
Dans quel bac le mettre ?
  1 - yellow
  2 - green
  3 - brown
  0 - Annuler
Choix : 1
✓ Nouvel objet enregistré : unknown_item → yellow
```

#### 2. Voir les Statistiques

```
Objet > stats

📊 Base de données :
  plastic_bottle       → yellow (7 utilisations)
  banana               → green (3 utilisations)
  paper_towel          → brown (5 utilisations)
  metal_can            → yellow (2 utilisations)
```

#### 3. Quitter

```
Objet > quit
Fermeture...
Base de données fermée ✓
Arduino fermé ✓
```

### Cas d'Usage

**Ajouter de nouveaux objets** :
1. Entrer le nom : `glass_bottle`
2. Répondre à la question du bac : `1` (yellow)
3. L'objet est enregistré et sera reconnu la prochaine fois

**Corriger une classification** :
1. Entrer l'objet : `plastic_bag` → demande bac
2. Choisir le bon bac
3. La BD est mise à jour

---

## 👁️ Mode Automatique (YOLO)

### Démarrage

Le mode complet avec détection par caméra et apprentissage.

```bash
# Activer l'environnement
.venv\Scripts\activate

# Lancer le mode automatique
cd src
python yolo_detector.py
```

### Affichage

```
🎬 DÉTECTION YOLO ACTIVE
Appuyez sur les touches :
  y = confirmer (apprendre)
  n = rejeter
  q = quitter

Détection: plastic_bottle (confiance: 0.92)
Action >
```

### Workflow Complet

#### Étape 1 : Placer un Objet
```
1. Placer un déchet devant la caméra
2. YOLO détecte l'objet automatiquement
```

#### Étape 2 : Confirmation de l'Utilisateur

```
Détection: banana (confiance: 0.87)
Action > y          ← Confirmer
✓ Apprentissage : image sauvegardée
✓ Tri vers bac green
```

Ou rejeter :
```
Détection: something (confiance: 0.45)
Action > n          ← Rejeter
⊘ Fausse détection ignorée
```

#### Étape 3 : Tri Automatique

Après confirmation :
```
1. YOLO détecte "banana"
2. DB cherche : trouve "green"
3. Arduino reçoit : "green"
4. Servos actionnés
5. Objet tombe dans le bac vert
6. Image sauvegardée pour apprentissage
```

### Commandes Pendant la Détection

| Touche | Action | Résultat |
|--------|--------|----------|
| `y` | Confirmer | Trie + enregistre l'image |
| `n` | Rejeter | Ignore cette détection |
| `q` | Quitter | Ferme l'application |
| (aucune) | Attendre | Continue la détection |

### Apprentissage Continu

À chaque confirmation (`y`) :

```
✓ Tri vers bac yellow
✓ Image sauvegardée dans :
  data/training_images/yellow/plastic_bottle_0234.jpg

[Cette image servira à réentraîner le modèle]
```

Les images s'accumulent dans :
- `data/training_images/yellow/` - images recyclables
- `data/training_images/green/` - images organiques
- `data/training_images/brown/` - images reste

### Optimiser la Détection

**Si manque de détections :**
```python
# Dans config.py
CONFIDENCE_THRESHOLD = 0.5    # Réduire (au lieu de 0.6)
MIN_DETECTIONS = 1            # Accepter une détection
```

**Si trop de faux positifs :**
```python
CONFIDENCE_THRESHOLD = 0.75   # Augmenter
MIN_DETECTIONS = 3            # Attendre 3 confirmations
```

---

## 🌐 Interface Web

### Démarrage

```bash
# Naviguer au dossier admin
cd admin_interface

# Installer si besoin
pip install Flask psutil

# Lancer l'application
python app.py
```

### Accès

Ouvrir le navigateur :
- **Local** : http://localhost:5000
- **Réseau** : http://192.168.1.XXX:5000 (remplacer XXX par votre IP)

### Fonctionnalités du Tableau de Bord

#### 1. Vue d'Ensemble Système
- CPU, RAM, Disque (temps réel)
- GPU NVIDIA (si disponible)
- État Arduino et Caméra
- Uptime du système

#### 2. Gestion des Bacs
```
Bac Jaune (Recyclage)
  Remplissage : 65%
  Items : 145
  Dernière vidange : 2026-02-01 10:30

Bac Vert (Compost)
  Remplissage : 32%
  Items : 87
  Dernière vidange : 2026-01-30 14:15

Bac Marron (Reste)
  Remplissage : 78%
  Items : 203
  Dernière vidange : 2026-01-28 09:00
```

#### 3. Historique Détections
```
Timestamp           | Objet          | Bac    | Confiance
2026-02-01 11:42   | plastic_bottle | yellow | 0.92
2026-02-01 11:40   | banana         | green  | 0.88
2026-02-01 11:38   | cardboard      | yellow | 0.85
```

#### 4. Paramètres
- Éditer config.py en direct
- Mode maintenance
- Activation/désactivation fonctionnalités

### Actions Possibles

**Vider un Bac** :
1. Cliquer "Gérer les Bacs"
2. Cliquer "Vider" sur le bac choisi
3. Redémarrage du compteur

**Consulter les Statistiques** :
1. Accueil → voir les graphiques
2. Section "Détections" → historique complet

**Télécharger les Logs** :
1. Menu → "Logs"
2. Sélectionner la plage de dates
3. Télécharger en CSV/JSON

---

## 🖥️ Commandes CLI

### Scripts Disponibles

```bash
# Mode manuel
python src/waste_classifier.py

# Mode automatique
python src/yolo_detector.py

# Interface web
cd admin_interface && python app.py

# Tests
python scripts/test_app.py
python scripts/test_complete.py
python scripts/test_hardware.py
```

### Arguments de Ligne de Commande

```bash
# Mode manuel avec fichier de log
python src/waste_classifier.py --log

# Mode automatique sans affichage
python src/yolo_detector.py --no-display

# Mode automatique avec confiance personnalisée
python src/yolo_detector.py --confidence 0.7

# Mode automatique enregistrer toutes les images
python src/yolo_detector.py --save-all
```

### Fichiers de Log

Les logs se trouvent dans : `data/logs/`

```bash
# Voir les logs récents
tail -f data/logs/system.log

# Filtrer les erreurs
grep "ERROR" data/logs/system.log

# Exporter les statistiques
python scripts/export_stats.py > rapport.txt
```

---

## 💡 Astuces et Bonnes Pratiques

### 1. Organiser les Objets

**Bonne pratique** :
- ✅ Utiliser des noms uniformes : `plastic_bottle` (pas `PET bottle`)
- ✅ Être spécifique : `glass_jar` (pas `glass`)
- ✅ Minuscules + underscores : `metal_can` (pas `Metal Can`)

**Éviter** :
- ❌ Noms différents pour même objet
- ❌ Espaces : utiliser `_`
- ❌ Caractères spéciaux

### 2. Améliorer la Détection

**Meilleure situation** :
```
✓ Bonne lumière
✓ Objet bien visible
✓ Caméra à distance appropriée (30-50cm)
✓ Fond simple
```

**À éviter** :
```
✗ Lumière trop faible
✗ Objet flou ou partiellement caché
✗ Trop prêt ou trop loin
✗ Fond complexe/chargé
```

### 3. Gérer la Base de Données

**Consultez régulièrement** :
```bash
# Voir les objets enregistrés
python src/waste_classifier.py
→ stats

# Vérifier la DB directement
sqlite3 data/waste_items.db
SELECT COUNT(*) FROM waste_classification;
```

**Nettoyer si besoin** :
```bash
# Sauvegarder d'abord
cp data/waste_items.db data/waste_items.db.backup

# Supprimer la DB (sera recréée vierge)
rm data/waste_items.db
```

### 4. Performance et Optimisation

**Pour plus de rapidité** :
```python
# config.py
FRAME_WIDTH = 320           # Au lieu de 640
FRAME_HEIGHT = 240          # Au lieu de 480
MIN_DETECTIONS = 1          # Au lieu de 3
AUTO_SORT_DELAY = 0.5       # Au lieu de 2.0
LEARNING_MODE = False       # Pas d'apprentissage
```

**Pour plus de précision** :
```python
CONFIDENCE_THRESHOLD = 0.75 # Au lieu de 0.6
MIN_DETECTIONS = 5
AUTO_SORT_DELAY = 3.0
LEARNING_MODE = True
```

### 5. Mode Production

**Configuration recommandée** :
```python
# config.py
LEARNING_MODE = False           # Pas d'interruption
SAVE_IMAGES = False             # Économise disque
SHOW_DISPLAY = False            # Économise CPU
CONFIDENCE_THRESHOLD = 0.75     # Fiable
AUTO_SORT_DELAY = 2.0          # Rythme équilibré
SORTING_DURATION = 15           # Temps pour trier
```

**Lancer en arrière-plan** (Linux) :
```bash
nohup python src/yolo_detector.py > data/logs/production.log 2>&1 &
```

### 6. Maintenance Régulière

**Tous les jours** :
- Vider les bacs physiques
- Vérifier les logs

**Toutes les semaines** :
- Nettoyer la caméra
- Vérifier la DB : `sqlite3 data/waste_items.db ".schema"`
- Consulter les statistiques

**Tous les mois** :
- Archiver les images d'apprentissage
- Réentraîner le modèle YOLO
- Backup de la base de données

---

## 📊 Exemple Workflow Complet

### Jour 1 : Mise en Place

```bash
1. Démarrer en mode manuel :
   python src/waste_classifier.py

2. Enregistrer les 10 objets courants :
   - plastic_bottle → yellow
   - glass_bottle → yellow
   - banana → green
   - etc.

3. Tester : 'stats' pour voir la DB
```

### Jour 2-5 : Apprentissage

```bash
1. Activer mode automatique :
   python src/yolo_detector.py

2. Placer régulièrement des objets
3. Confirmer chaque détection : 'y'
4. Les images s'accumulent dans data/training_images/

5. Après 100+ images confirmées :
   python docs/ENTRAINEMENT_IA.md
```

### Semaine 2+ : Production

```bash
1. Mode automatique stable
2. Presque pas de faux positifs
3. Tri automatisé
4. Monitoring web

python src/yolo_detector.py  # Fonctionnement autonome
```

---

## 🔧 Dépannage Rapide Utilisation

| Problème | Solution |
|----------|----------|
| Rien ne trie | Vérifier Arduino connecté : `python scripts/test_hardware.py` |
| Caméra ne démarre pas | Changer `CAMERA_SOURCE` dans config.py |
| BD trop grande | Archiver les images : `mv data/training_images/* archive/` |
| Performance lente | Réduire résolution caméra dans config.py |
| Trop de faux positifs | Augmenter `CONFIDENCE_THRESHOLD` à 0.7-0.8 |

---

**Besoin d'aide ?** Voir [docs/DEPANNAGE.md](DEPANNAGE.md)

