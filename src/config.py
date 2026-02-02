"""
Smart Bin SI - Configuration Centrale
Configuration centralisée pour le système de tri intelligent des déchets.
"""

from pathlib import Path

# ============================================
# CHEMINS DE BASE
# ============================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TRAINING_DIR = DATA_DIR / "training_images"
DB_PATH = DATA_DIR / "waste_items.db"
MODELS_DIR = BASE_DIR / "models"

# Création automatique des dossiers nécessaires
DATA_DIR.mkdir(exist_ok=True)
TRAINING_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# ============================================
# CONFIGURATION DU MODÈLE YOLO
# ============================================
MODEL_PATH = str(MODELS_DIR / "best.pt")  # Chemin vers le modèle YOLO entraîné
CONFIDENCE_THRESHOLD = 0.6                # Seuil de confiance pour les détections
IOU_THRESHOLD = 0.45                      # Seuil d'intersection sur union pour NMS

# ============================================
# CONFIGURATION DE LA CAMÉRA
# ============================================
CAMERA_SOURCE = 0        # Index de la caméra (0 = caméra par défaut)
USE_CSI_CAMERA = False   # Utiliser la caméra CSI sur Raspberry Pi
FRAME_WIDTH = 640        # Largeur de l'image capturée
FRAME_HEIGHT = 480       # Hauteur de l'image capturée
SHOW_DISPLAY = True      # Afficher la fenêtre de visualisation OpenCV

# ============================================
# CONFIGURATION ARDUINO
# ============================================
ARDUINO_PORT = '/dev/ttyACM0'  # Port série pour la communication Arduino
BAUD_RATE = 9600               # Vitesse de communication en bauds
SORTING_DURATION = 10          # Durée d'attente pour le tri en secondes

# ============================================
# CONFIGURATION DE L'APPRENTISSAGE
# ============================================
LEARNING_MODE = True      # Mode apprentissage : validation manuelle des détections
SAVE_IMAGES = True        # Sauvegarder les images de détection
MIN_DETECTIONS = 3        # Nombre minimum de détections consécutives avant tri
AUTO_SORT_DELAY = 2.0     # Délai entre deux opérations de tri en secondes

# ============================================
# CONFIGURATION DES BACS DE TRI
# ============================================
VALID_BINS = ["yellow", "green", "brown"]  # Bacs de tri valides

# Mapping par défaut des objets détectés vers les bacs
# jaune=recyclable, vert=organique, marron=déchets généraux
# Les nouveaux objets appris sont stockés en base de données
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

# Couleurs pour l'affichage OpenCV (format BGR)
BIN_COLORS = {
    "yellow": (0, 255, 255),  # Jaune
    "green": (0, 255, 0),     # Vert
    "brown": (50, 100, 165),  # Marron
    "unknown": (128, 128, 128)  # Gris pour inconnu
}