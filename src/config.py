"""
Smart Bin SI - Configuration Centrale
Tous les paramètres système au même endroit
"""

from pathlib import Path

# ============================================
# CHEMINS
# ============================================
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"

# Créer les dossiers s'ils n'existent pas
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# ============================================
# CONFIGURATION DU MODÈLE YOLO
# ============================================

# Modèle à utiliser (change ici pour changer de modèle)
# Options : "yolov8n_waste.pt", "yolov8s_waste.pt", "yolov8m_waste.pt", "best.pt"
MODEL_NAME = "yolov8n_waste.pt"
MODEL_PATH = str(MODELS_DIR / MODEL_NAME)

# Paramètres de détection
CONFIDENCE_THRESHOLD = 0.6  # Confiance minimum pour accepter une détection (0-1)
IOU_THRESHOLD = 0.45        # Seuil IoU pour la suppression non-maximale
MIN_DETECTIONS = 3          # Nombre minimum de détections consécutives avant tri
AUTO_SORT_DELAY = 2.0       # Secondes d'attente avant le tri automatique

# ============================================
# MAPPING DES CLASSES DE DÉCHETS
# ============================================
# Associe les noms de classes détectées aux couleurs de bacs
# Personnaliser selon les classes de TON modèle

# Pour le modèle YOLOv8n Waste (6 classes)
WASTE_MAPPING_YOLOV8N = {
    "cardboard": "yellow",      # Recyclable
    "glass": "yellow",          # Recyclable
    "metal": "yellow",          # Recyclable
    "paper": "yellow",          # Recyclable
    "plastic": "yellow",        # Recyclable
    "trash": "brown",           # Déchets généraux
}

# Pour le modèle YOLOv8s Waste (Classes étendues)
WASTE_MAPPING_YOLOV8S = {
    "cardboard": "yellow",
    "glass": "yellow",
    "metal": "yellow",
    "paper": "yellow",
    "plastic": "yellow",
    "biodegradable": "green",   # Organique
    "hazardous": "brown",       # Traitement spécial
    "trash": "brown",
}

# Pour un modèle personnalisé (Définis le tien)
WASTE_MAPPING_CUSTOM = {
    "plastic_bottle": "yellow",
    "aluminum_can": "yellow",
    "newspaper": "yellow",
    "food_waste": "green",
    "banana_peel": "green",
    "coffee_grounds": "green",
    "general_waste": "brown",
    "styrofoam": "brown",
}

# Sélectionner le mapping actif selon le modèle
if "yolov8n" in MODEL_NAME:
    WASTE_TO_BIN_MAPPING = WASTE_MAPPING_YOLOV8N
elif "yolov8s" in MODEL_NAME:
    WASTE_TO_BIN_MAPPING = WASTE_MAPPING_YOLOV8S
elif "best" in MODEL_NAME:
    WASTE_TO_BIN_MAPPING = WASTE_MAPPING_CUSTOM
else:
    WASTE_TO_BIN_MAPPING = WASTE_MAPPING_YOLOV8N  # Par défaut

# ============================================
# CONFIGURATION CAMÉRA
# ============================================

# Source de la caméra
CAMERA_SOURCE = 0  # 0 pour caméra USB, 1 pour deuxième caméra, etc.

# Utiliser une caméra CSI (Module Raspberry Pi Camera sur Jetson)
USE_CSI_CAMERA = False

# Paramètres caméra CSI
CSI_CAMERA_ID = 0
CSI_CAMERA_WIDTH = 640
CSI_CAMERA_HEIGHT = 480
CSI_CAMERA_FPS = 30
CSI_FLIP_METHOD = 0  # 0=pas de rotation, 2=rotation 180°

# Résolution des images
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Paramètres d'affichage
SHOW_DISPLAY = True  # Afficher la fenêtre OpenCV avec détections
SHOW_FPS = True      # Afficher le compteur de FPS

# ============================================
# CONFIGURATION ARDUINO
# ============================================

# Paramètres du port série
ARDUINO_PORT = "/dev/ttyACM0"  # Essayer /dev/ttyACM1, /dev/ttyUSB0 si pas trouvé
BAUD_RATE = 9600
SERIAL_TIMEOUT = 1

# Ports possibles à tester (dans l'ordre)
POSSIBLE_PORTS = [
    "/dev/ttyACM0",
    "/dev/ttyACM1",
    "/dev/ttyUSB0",
    "/dev/ttyUSB1",
]

# Timing du tri
SORTING_DURATION = 10  # Secondes d'attente pour que l'Arduino finisse le tri

# ============================================
# CONFIGURATION BASE DE DONNÉES
# ============================================

# Fichier de la base de données
DB_NAME = "waste_items.db"
DB_PATH = str(DATA_DIR / DB_NAME)

# Tables
TABLE_CLASSIFICATION = "waste_classification"
TABLE_HISTORY = "detection_history"

# ============================================
# COULEURS DES BACS
# ============================================

# Couleurs valides des bacs (ne pas changer)
VALID_BINS = ["yellow", "green", "brown"]

# Informations sur les bacs
BIN_INFO = {
    "yellow": {
        "name": "Recyclable",
        "description": "Plastique, carton, métal, verre, papier",
        "color_rgb": (255, 255, 0),
        "color_bgr": (0, 255, 255),  # Pour OpenCV
    },
    "green": {
        "name": "Organique",
        "description": "Déchets alimentaires, matériaux biodégradables",
        "color_rgb": (0, 255, 0),
        "color_bgr": (0, 255, 0),
    },
    "brown": {
        "name": "Déchets Généraux",
        "description": "Déchets non recyclables, non organiques",
        "color_rgb": (165, 100, 50),
        "color_bgr": (50, 100, 165),
    },
}

# ============================================
# CONFIGURATION DES LOGS
# ============================================

# Fichiers de logs
SYSTEM_LOG = str(LOGS_DIR / "system.log")
DETECTION_LOG = str(LOGS_DIR / "detections.log")
ERROR_LOG = str(LOGS_DIR / "errors.log")

# Niveau de logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Format des logs
LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================
# OPTIMISATION PERFORMANCES (JETSON)
# ============================================

# Utiliser l'accélération GPU si disponible
USE_GPU = True

# Nombre de threads pour l'inférence CPU
NUM_THREADS = 4

# Prétraitement des images
RESIZE_FOR_INFERENCE = True  # Redimensionner les images avant inférence pour la vitesse
TARGET_INFERENCE_SIZE = 416  # Plus petit = plus rapide, moins précis

# ============================================
# PARAMÈTRES DE COMPORTEMENT
# ============================================

# Demander confirmation manuelle avant le tri
REQUIRE_CONFIRMATION = False

# Apprentissage automatique des nouveaux objets
AUTO_LEARN = True

# Nombre maximum d'erreurs consécutives avant arrêt
MAX_CONSECUTIVE_ERRORS = 5

# Activer le mode debug (sortie verbeuse)
DEBUG_MODE = False

# ============================================
# COULEURS UI (Pour la sortie Terminal)
# ============================================

COLORS = {
    "success": "\033[92m",  # Vert
    "error": "\033[91m",    # Rouge
    "warning": "\033[93m",  # Jaune
    "info": "\033[94m",     # Bleu
    "reset": "\033[0m",     # Reset
}

# ============================================
# PARAMÈTRES D'EXPORT
# ============================================

# Dossier d'export
EXPORT_DIR = DATA_DIR / "exports"
EXPORT_DIR.mkdir(exist_ok=True)

# Formats d'export
EXPORT_CSV = True
EXPORT_JSON = True

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def get_bin_color_display(bin_color):
    """Obtenir une sortie terminal colorée pour la couleur du bac"""
    if bin_color == "yellow":
        return f"\033[93m{bin_color}\033[0m"
    elif bin_color == "green":
        return f"\033[92m{bin_color}\033[0m"
    elif bin_color == "brown":
        return f"\033[91m{bin_color}\033[0m"
    return bin_color


def get_opencv_color(bin_color):
    """Obtenir le tuple de couleur BGR OpenCV pour la couleur du bac"""
    return BIN_INFO.get(bin_color, {}).get("color_bgr", (128, 128, 128))


def print_config():
    """Afficher la configuration actuelle"""
    print("\n" + "="*60)
    print("📋 SMART BIN SI - CONFIGURATION")
    print("="*60)
    print(f"Modèle : {MODEL_NAME}")
    print(f"Seuil de confiance : {CONFIDENCE_THRESHOLD}")
    print(f"Source caméra : {CAMERA_SOURCE}")
    print(f"Port Arduino : {ARDUINO_PORT}")
    print(f"Base de données : {DB_PATH}")
    print(f"Classes : {len(WASTE_TO_BIN_MAPPING)}")
    print("\nMapping des déchets :")
    for waste_class, bin_color in WASTE_TO_BIN_MAPPING.items():
        print(f"  - {waste_class:20} → {get_bin_color_display(bin_color)}")
    print("="*60 + "\n")


# ============================================
# VALIDATION
# ============================================

def validate_config():
    """Vérifier si la configuration est valide"""
    errors = []
    
    # Vérifier si le fichier du modèle existe
    if not Path(MODEL_PATH).exists():
        errors.append(f"Fichier du modèle introuvable : {MODEL_PATH}")
    
    # Vérifier si le dossier de la base de données existe
    if not DATA_DIR.exists():
        errors.append(f"Dossier data introuvable : {DATA_DIR}")
    
    # Vérifier si le mapping est valide
    for waste_class, bin_color in WASTE_TO_BIN_MAPPING.items():
        if bin_color not in VALID_BINS:
            errors.append(f"Couleur de bac invalide '{bin_color}' pour la classe '{waste_class}'")
    
    if errors:
        print(f"{COLORS['error']}Erreurs de configuration :{COLORS['reset']}")
        for error in errors:
            print(f"  ✗ {error}")
        return False
    
    return True


# ============================================
# EXPORT TOUT
# ============================================

__all__ = [
    # Chemins
    "BASE_DIR", "SRC_DIR", "DATA_DIR", "LOGS_DIR", "MODELS_DIR",
    
    # Modèle
    "MODEL_NAME", "MODEL_PATH", "CONFIDENCE_THRESHOLD", "IOU_THRESHOLD",
    "MIN_DETECTIONS", "AUTO_SORT_DELAY",
    
    # Mapping
    "WASTE_TO_BIN_MAPPING", "VALID_BINS", "BIN_INFO",
    
    # Caméra
    "CAMERA_SOURCE", "USE_CSI_CAMERA", "FRAME_WIDTH", "FRAME_HEIGHT",
    "SHOW_DISPLAY", "SHOW_FPS",
    
    # Arduino
    "ARDUINO_PORT", "BAUD_RATE", "SERIAL_TIMEOUT", "POSSIBLE_PORTS",
    "SORTING_DURATION",
    
    # Base de données
    "DB_NAME", "DB_PATH", "TABLE_CLASSIFICATION", "TABLE_HISTORY",
    
    # Logging
    "SYSTEM_LOG", "DETECTION_LOG", "ERROR_LOG", "LOG_LEVEL",
    
    # Comportement
    "REQUIRE_CONFIRMATION", "AUTO_LEARN", "MAX_CONSECUTIVE_ERRORS",
    "DEBUG_MODE",
    
    # Fonctions
    "get_bin_color_display", "get_opencv_color", "print_config",
    "validate_config",
]


# ============================================
# EXÉCUTION DU SCRIPT
# ============================================

if __name__ == "__main__":
    print_config()
    
    if validate_config():
        print(f"{COLORS['success']}✓ Configuration valide{COLORS['reset']}\n")
    else:
        print(f"\n{COLORS['error']}✗ La configuration contient des erreurs{COLORS['reset']}\n")