"""
Smart Bin SI - Configuration Centrale
"""

from pathlib import Path

# ============================================
# CHEMINS
# ============================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TRAINING_DIR = DATA_DIR / "training_images"
DB_PATH = DATA_DIR / "waste_items.db"
MODELS_DIR = BASE_DIR / "models"

# Créer les dossiers
DATA_DIR.mkdir(exist_ok=True)
TRAINING_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# ============================================
# MODÈLE YOLO
# ============================================
MODEL_PATH = str(MODELS_DIR / "best.pt")  # Ton modèle entraîné
CONFIDENCE_THRESHOLD = 0.6                # Seuil de confiance
IOU_THRESHOLD = 0.45                      # Seuil NMS

# ============================================
# CAMÉRA
# ============================================
CAMERA_SOURCE = 0        # 0 = USB, 1 = deuxième caméra
USE_CSI_CAMERA = False   # True pour Raspberry Pi Camera
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
SHOW_DISPLAY = True      # Afficher la fenêtre OpenCV

# ============================================
# ARDUINO
# ============================================
ARDUINO_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600
SORTING_DURATION = 10    # Secondes d'attente pour le tri

# ============================================
# APPRENTISSAGE
# ============================================
LEARNING_MODE = True      # Demander validation pour chaque détection
SAVE_IMAGES = True        # Sauvegarder les images
MIN_DETECTIONS = 3        # Détections consécutives avant tri
AUTO_SORT_DELAY = 2.0     # Délai entre deux tris (secondes)

# ============================================
# BACS DE TRI
# ============================================
VALID_BINS = ["yellow", "green", "brown"]

# Mapping par défaut : objet détecté → bac (jaune=recyclable, vert=organique, marron=reste)
# Tu peux l'étendre ; les nouveaux objets appris en usage sont stockés en DB
WASTE_TO_BIN_MAPPING = {
    "plastic": "yellow",
    "plastic_bottle": "yellow",
    "bottle": "yellow",
    "cardboard": "yellow",
    "paper": "yellow",
    "metal": "yellow",
    "glass": "yellow",
    "can": "yellow",
    "banana_peel": "green",
    "food": "green",
    "organic": "green",
    "tissue": "brown",
    "trash": "brown",
}

# Couleurs pour l'affichage OpenCV (BGR)
BIN_COLORS = {
    "yellow": (0, 255, 255),
    "green": (0, 255, 0),
    "brown": (50, 100, 165),
    "unknown": (128, 128, 128)
}