# 🧠 Entraîner ton IA (YOLO) – Étape par étape

Ce guide t’explique **comment entraîner ton modèle de détection** pour Smart Bin : logiciels (dont applications web), où mettre les fichiers, et quoi faire après l’entraînement.

---

## Vue d’ensemble

Pour que ton IA reconnaisse tes déchets, il faut :

1. **Collecter des images** de tes déchets (photos ou captures caméra).
2. **Annoter** : dessiner une boîte autour de chaque objet et lui donner un nom (ex. `plastic_bottle`, `can`).
3. **Exporter** le jeu de données au format YOLO (images + fichiers `.txt` de labels).
4. **Entraîner** un modèle YOLO (sur ton PC ou en ligne).
5. **Mettre le modèle dans le projet** : copier le fichier `best.pt` au bon endroit.

À la fin, ton projet doit utiliser **`src/models/best.pt`** (ou le chemin indiqué dans `config.py`).

---

## Où mettre quoi dans le projet

```
SIpoubelle/
├── src/
│   ├── models/           ← ICI : tu mets ton modèle entraîné (best.pt)
│   │   └── best.pt       ← Fichier généré après l’entraînement
│   ├── data/
│   │   └── training_images/   ← Images collectées par l’app (optionnel pour réentraînement)
│   │       ├── plastic_bottle/
│   │       ├── can/
│   │       └── ...
│   ├── config.py
│   ├── yolo_detector.py
│   └── waste_classifier.py
```

- **Avant l’entraînement** : tu prépares ton dataset **ailleurs** (sur Roboflow, ou dans un dossier `dataset/` sur ton PC).
- **Après l’entraînement** : tu copies **`best.pt`** dans **`src/models/best.pt`** (ou tu changes `MODEL_PATH` dans `src/config.py`).

---

# Méthode 1 : Application web (Roboflow) – Recommandé pour débuter

Tout se fait dans le navigateur : annotation + entraînement dans le cloud. Pas besoin d’installer de logiciel lourd.

## Étape 1 : Créer un compte et un projet

1. Va sur **https://roboflow.com**
2. Crée un compte (gratuit).
3. Clique sur **Create New Project**.
4. Donne un nom au projet (ex. `SmartBin-Dechets`).
5. Choisis **Object Detection**.
6. Valide.

## Étape 2 : Ajouter tes images

1. Dans le projet, onglet **Upload** (ou **Add Images**).
2. Tu peux :
   - **Glisser-déposer** des images depuis ton PC.
   - Ou utiliser des **images déjà collectées** par Smart Bin dans `src/data/training_images/<classe>/` (copie-les dans un dossier puis uploade ce dossier).
3. Idéal : au moins **50–100 images par classe** (ex. 50 bouteilles, 50 canettes, 50 cartons). Plus tu en mets, mieux c’est.

**Où prendre les images ?**

- Photos de déchets avec ton téléphone.
- Captures faites avec `yolo_detector.py` (tu valides « y » et les images sont dans `src/data/training_images/`).
- Datasets publics (Roboflow Universe, etc.) que tu importes dans le même projet.

## Étape 3 : Annoter (dessiner les boîtes)

1. Onglet **Annotate** (ou **Label**).
2. Ouvre une image.
3. Choisis une **classe** (ex. `plastic_bottle`, `can`, `cardboard`) ou crée-la.
4. Dessine un **rectangle** autour de chaque objet à détecter.
5. Associe le rectangle à la classe.
6. Passe à l’image suivante. Répète pour toutes les images.

Conseil : garde des **noms de classes courts, en anglais, sans espace** (ex. `plastic_bottle`, `can`, `paper`, `organic`). Tu pourras les faire correspondre aux bacs dans `config.py` après.

## Étape 4 : Générer le dataset et choisir le format YOLO

1. Quand tu as fini d’annoter, clique sur **Generate** (ou **Create Dataset Version**).
2. Tu peux appliquer des **augmentations** (rotation, luminosité, etc.) pour avoir plus de variété – optionnel.
3. Clique sur **Generate**.
4. Une fois la version créée, clique sur **Export**.
5. Choisis le format **YOLOv8** (ou YOLOv5).
6. Télécharge le **ZIP** du dataset.

Tu obtiens un ZIP avec une structure du type :

```
dataset/
├── data.yaml      ← Fichier de config (chemins + noms de classes)
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
```

## Étape 5 : Entraîner le modèle (sur Roboflow ou sur ton PC)

### Option A : Entraînement dans Roboflow (nécessite un abonnement payant)

- Dans Roboflow, onglet **Train** → choisis un modèle (ex. YOLOv8) et lance l’entraînement.
- À la fin, télécharge le fichier **weights** (souvent `best.pt`).

### Option B : Entraînement sur ton PC (gratuit)

1. Décompresse le ZIP téléchargé (par ex. dans `C:\Users\Toi\dataset_smartbin\`).
2. Ouvre un terminal dans ce dossier (ou note le chemin vers le dossier qui contient `data.yaml`).
3. Installe Ultralytics et lance l’entraînement :

```bash
pip install ultralytics
cd C:\Users\Toi\dataset_smartbin
yolo train model=yolov8n.pt data=data.yaml epochs=100 imgsz=640
```

- `yolov8n.pt` = modèle petit et rapide (nano). Tu peux mettre `yolov8s.pt` pour plus de précision et plus lent.
- À la fin, le fichier **`best.pt`** est dans un sous-dossier du type `runs/detect/train/weights/best.pt`.

## Étape 6 : Mettre le modèle dans Smart Bin

1. Copie le fichier **`best.pt`** (depuis Roboflow ou depuis `runs/detect/train/weights/best.pt`).
2. Colle-le dans ton projet :

```
SIpoubelle\src\models\best.pt
```

3. Si ton projet est dans `Z:\SI\SIpoubelle`, le chemin complet est :  
   **`Z:\SI\SIpoubelle\src\models\best.pt`**

4. Vérifie dans **`src/config.py`** que c’est bien ce fichier qui est utilisé :

```python
MODEL_PATH = str(MODELS_DIR / "best.pt")  # → src/models/best.pt
```

C’est tout : au prochain lancement de `yolo_detector.py`, ton IA utilisera ce modèle.

---

# Méthode 2 : Logiciel local (LabelImg + Ultralytics)

Tu fais l’annotation sur ton PC avec LabelImg, puis tu entraînes avec Ultralytics.

## Étape 1 : Installer LabelImg

```bash
pip install labelImg
```

Ou depuis les sources : https://github.com/HumanSignal/labelImg

## Étape 2 : Préparer les dossiers

Crée un dossier pour ton dataset, par exemple :

```
C:\Users\Toi\dataset_smartbin\
├── images\    ← toutes tes images (.jpg, .png)
└── labels\    ← vide au début ; LabelImg y mettra les .txt
```

Mets tes photos de déchets dans **`images/`**.

## Étape 3 : Définir les classes

1. Lance LabelImg : `labelImg` dans un terminal.
2. **View** → **Auto Save** (optionnel).
3. **Edit** → **Label List** (ou équivalent) : ajoute tes classes une par une, ex. :
   - `plastic_bottle`
   - `can`
   - `cardboard`
   - `paper`
   - etc.

## Étape 4 : Annoter

1. **Open Dir** → choisis le dossier **`images`**.
2. **Change Save Dir** → choisis le dossier **`labels`**.
3. Format : **YOLO** (pas PascalVOC).
4. Pour chaque image : dessine un rectangle autour de chaque objet, choisis la classe, sauvegarde. Passe à l’image suivante.

## Étape 5 : Créer le fichier data.yaml

Dans le dossier du dataset (ex. `C:\Users\Toi\dataset_smartbin\`), crée un fichier **`data.yaml`** :

```yaml
path: .   # ou chemin absolu vers dataset_smartbin
train: images
val: images

names:
  0: plastic_bottle
  1: can
  2: cardboard
  3: paper
  # ... autant que tes classes, dans l’ordre des index 0, 1, 2, ...
```

- `train` et `val` : dossiers d’images (tu peux mettre les mêmes au début, ou séparer 80 % train / 20 % val).
- Les fichiers dans **`labels/`** doivent avoir le **même nom** que les images, en `.txt` (ex. `photo1.jpg` → `photo1.txt`). Chaque ligne du `.txt` : `class_id x_center y_center width height` (valeurs normalisées 0–1).

## Étape 6 : Lancer l’entraînement

```bash
cd C:\Users\Toi\dataset_smartbin
pip install ultralytics
yolo train model=yolov8n.pt data=data.yaml epochs=100 imgsz=640
```

## Étape 7 : Copier best.pt dans le projet

Comme en Méthode 1 :

- Fichier généré : `runs/detect/train/weights/best.pt`
- Copie-le vers : **`Z:\SI\SIpoubelle\src\models\best.pt`** (ou `SIpoubelle\src\models\best.pt` selon ton chemin).

---

# Récapitulatif : où mettre quoi

| Étape | Où | Quoi |
|-------|-----|------|
| Images brutes / dataset | Où tu veux (Roboflow ou dossier PC) | Photos + annotations |
| Après entraînement | **`src/models/best.pt`** | Fichier **best.pt** |
| Config du projet | **`src/config.py`** | `MODEL_PATH` pointe vers `best.pt` |
| Images collectées par l’app | **`src/data/training_images/<classe>/`** | Pour réentraîner plus tard (optionnel) |

---

# Après l’entraînement : faire correspondre les classes aux bacs

Les noms de classes du modèle (ex. `plastic_bottle`, `can`) doivent être reliés aux bacs dans **`src/config.py`** :

```python
WASTE_TO_BIN_MAPPING = {
    "plastic_bottle": "yellow",
    "can": "yellow",
    "cardboard": "yellow",
    "paper": "yellow",
    "organic": "green",
    # ...
}
```

Tu peux ajouter toutes les classes que tu as utilisées lors de l’annotation. Les objets inconnus en usage pourront être assignés à un bac par l’utilisateur (mode manuel / première détection).

---

# En résumé

1. **Logiciel web** : Roboflow (annotation + export YOLO, entraînement possible en ligne ou après export).
2. **Logiciel local** : LabelImg (annotation) + Ultralytics (entraînement).
3. **Où mettre le modèle** : **`src/models/best.pt`**.
4. **Où configurer** : **`src/config.py`** (`MODEL_PATH` et `WASTE_TO_BIN_MAPPING`).

Une fois **`best.pt`** en place dans **`src/models/`**, lance **`yolo_detector.py`** et ton IA utilisera ton modèle personnalisé.
