# Apprentissage au fur et à mesure – Smart Bin SI

Ce guide explique comment utiliser YOLO avec une **base que tu entraînes toi-même** et un **apprentissage continu** : dès qu’une détection est validée (« oui c’est correct »), le système enregistre l’image pour améliorer le modèle plus tard.

---

## 1. Quel script utiliser ?

| À faire | Script |
|--------|--------|
| **Lancer la détection + apprentissage** | `yolo_detector.py` |
| Ne plus lancer comme programme principal | ~~`waste_classifier.py`~~ (il ne contient plus que la logique DB + Arduino, pas d’entrée caméra) |

**En pratique :**

```bash
cd SIpoubelle
# Depuis la racine du projet (avec src dans le PYTHONPATH ou depuis src/)
python -m src.yolo_detector
# OU depuis src/
cd src && python yolo_detector.py
```

---

## 2. Flux en mode apprentissage

1. Tu lances **`yolo_detector.py`**.
2. YOLO détecte un objet (ex. `plastic_bottle`).
3. Après **3 détections consécutives** (évite les faux positifs), le script te demande :
   - **y** : Oui, c’est correct → l’image (et un fichier label YOLO si dispo) est sauvegardée dans `data/training_images/<classe>/`, puis le tri est envoyé à l’Arduino.
   - **n** : Non → tu indiques le vrai nom → l’image est sauvegardée sous la classe corrigée (et en erreur pour l’ancienne), puis le tri se fait avec la classe corrigée.
   - **skip** : Ignorer → rien n’est sauvegardé, pas de tri.

4. Les images validées sont stockées dans **`data/training_images/<nom_classe>/`** (ex. `data/training_images/plastic_bottle/`).  
   Si une bbox est disponible, un fichier **`.txt`** au format YOLO (une ligne : `class_id x_center y_center width height` normalisés) est créé à côté de l’image pour le réentraînement.

---

## 3. Base de données que tu entraînes toi-même

- **Modèle initial** : tu entraînes un modèle YOLO sur **tes** classes (déchets que tu veux reconnaître). Tu mets le fichier de poids dans **`models/best.pt`** (ou tu adaptes `MODEL_PATH` dans `config.py`).
- **Mapping objet → bac** : dans **`config.py`**, la variable **`WASTE_TO_BIN_MAPPING`** donne le bac par défaut pour chaque classe. Les objets que l’utilisateur associe à un bac en usage sont en plus enregistrés en base SQLite (`data/waste_items.db`) et réutilisés ensuite.

Tu peux :
- Étendre **`WASTE_TO_BIN_MAPPING`** pour de nouvelles classes.
- Laisser l’utilisateur choisir le bac la première fois qu’un objet inconnu est détecté (géré par `waste_classifier`).

---

## 4. Entraîner ta base (modèle initial)

1. **Préparer un jeu de données**  
   - Images de tes déchets, avec annotations au format YOLO (fichiers `.txt` par image : `class_id x_center y_center width height` normalisés).
   - Tu peux utiliser [Roboflow](https://roboflow.com/), [LabelImg](https://github.com/HumanSignal/labelImg), etc.

2. **Entraîner YOLO (ex. Ultralytics YOLOv8)**  
   - Exemple avec `ultralytics` :
     ```bash
     pip install ultralytics
     yolo train model=yolov8n.pt data=chemin/vers/data.yaml epochs=100 imgsz=640
     ```
   - Le `data.yaml` décrit les dossiers d’images/labels et les noms de classes.

3. **Copier le meilleur poids**  
   - Remplacer (ou pointer) **`models/best.pt`** par ton `best.pt` issu de l’entraînement.

---

## 5. Réentraîner avec les images collectées

Les images validées (« y ») sont dans **`data/training_images/<classe>/`** avec, quand c’est possible, un **`.txt`** au format YOLO.

Pour **réentraîner** (fine-tuning ou nouvel entraînement) :

1. **Option A – Réutiliser la structure actuelle**  
   - Construire un `data.yaml` qui pointe vers :
     - Images : sous-dossiers de `data/training_images/` (en excluant `_errors` si tu veux).
     - Labels : les `.txt` à côté de chaque image.
   - Les noms de classes doivent correspondre à ceux de ton modèle (ou à un nouveau `names` dans le `data.yaml`).

2. **Option B – Script de conversion**  
   - Tu peux ajouter un script (ex. `scripts/build_training_dataset.py`) qui :
     - Parcourt `data/training_images/`,
     - Copie les images + labels dans une arborescence type `dataset/images/train/` et `dataset/labels/train/`,
     - Génère un `data.yaml` avec les bons chemins et noms de classes.

Ensuite, lancer un entraînement Ultralytics comme au §4, avec ce nouveau `data.yaml`, puis remplacer **`models/best.pt`** par le nouveau `best.pt`.

---

## 6. Récap des dossiers importants

| Dossier / Fichier | Rôle |
|-------------------|------|
| **`models/best.pt`** | Modèle YOLO utilisé à l’exécution (celui que tu entraînes / réentraînes). |
| **`data/training_images/<classe>/`** | Images validées (« correct ») pour chaque classe, + `.txt` YOLO si bbox disponible. |
| **`data/training_images/_errors/`** | Images sauvegardées quand tu corriges une détection (classe incorrecte). |
| **`data/waste_items.db`** | Base SQLite : association objet → bac (jaune/vert/marron). |
| **`src/config.py`** | Configuration : `MODEL_PATH`, `TRAINING_DIR`, `WASTE_TO_BIN_MAPPING`, seuils, etc. |

---

## 7. Ce qu’on a supprimé / simplifié

- **`waste_classifier.py`** en tant que script principal avec caméra + YOLO a été retiré. Il ne contient plus que la logique **DB + Arduino** (init DB, série, `get_bin_color`, `classify_and_sort`, `save_to_database`, `ask_user_for_bin`, etc.), utilisée par **`yolo_detector.py`**.
- Un seul point d’entrée pour la détection et l’apprentissage : **`yolo_detector.py`**.  
  Dès qu’une détection est validée (« oui c’est correct »), l’image (et le label YOLO si possible) est enregistrée pour que tu puisses réentraîner le modèle et l’améliorer au fur et à mesure.
