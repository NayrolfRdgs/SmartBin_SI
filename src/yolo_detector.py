"""
Smart Bin SI - Module de Détection YOLO
Intègre YOLOv5/YOLOv8 pour la détection temps-réel via caméra
Remplace la saisie manuelle par la détection automatique
"""

import cv2
import torch
import time
import numpy as np
from pathlib import Path
import sys

# Ajouter le script principal au path pour utiliser les fonctions de base de données
sys.path.append(str(Path(__file__).parent))

try:
    from waste_classifier import (
        init_database, 
        get_or_assign_bin_color, 
        send_sorting_command,
        init_serial_connection
    )
    MAIN_SCRIPT_AVAILABLE = True
except ImportError:
    print("⚠ Attention : Script principal non trouvé")
    MAIN_SCRIPT_AVAILABLE = False


# ============================================
# CONFIGURATION
# ============================================

# Configuration du modèle
MODEL_PATH = "models/best.pt"  # Chemin vers ton modèle YOLO entraîné
CONFIDENCE_THRESHOLD = 0.6     # Confiance minimum pour accepter une détection
IOU_THRESHOLD = 0.45           # Seuil IoU pour la suppression non-maximale

# Configuration caméra
CAMERA_SOURCE = 0  # 0 pour caméra USB, ou "rtsp://..." pour caméra IP
# Pour caméra CSI Jetson, utiliser le pipeline gstreamer (voir ci-dessous)
USE_CSI_CAMERA = False

# Configuration affichage
SHOW_DISPLAY = True
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Comportement de détection
AUTO_SORT_DELAY = 2.0  # Secondes d'attente avant le tri auto d'un objet détecté
MIN_DETECTIONS = 3     # Nombre minimum de détections consécutives avant tri


# Mapping catégorie de déchet → couleur de bac
# Personnaliser selon les classes de ton modèle entraîné
WASTE_TO_BIN_MAPPING = {
    # Recyclable (Bac jaune)
    "plastic_bottle": "yellow",
    "cardboard": "yellow",
    "paper": "yellow",
    "metal_can": "yellow",
    "glass": "yellow",
    
    # Organique (Bac vert)
    "food_waste": "green",
    "organic": "green",
    "biodegradable": "green",
    
    # Déchets généraux (Bac marron)
    "general_waste": "brown",
    "non_recyclable": "brown",
    "mixed": "brown",
}


# ============================================
# SUPPORT CAMÉRA CSI JETSON
# ============================================

def get_csi_pipeline(camera_id=0, width=640, height=480, fps=30):
    """
    Créer un pipeline GStreamer pour caméra CSI Jetson
    
    Args:
        camera_id: ID du capteur caméra (0 ou 1)
        width: Largeur de l'image
        height: Hauteur de l'image
        fps: Fréquence d'images
    
    Retourne:
        str: Chaîne de pipeline GStreamer
    """
    return (
        f"nvarguscamerasrc sensor-id={camera_id} ! "
        f"video/x-raw(memory:NVMM), width={width}, height={height}, "
        f"format=NV12, framerate={fps}/1 ! "
        f"nvvidconv flip-method=0 ! "
        f"video/x-raw, width={width}, height={height}, format=BGRx ! "
        f"videoconvert ! "
        f"video/x-raw, format=BGR ! appsink"
    )


# ============================================
# CLASSE DÉTECTEUR DE DÉCHETS
# ============================================

class WasteDetector:
    """
    Système de détection de déchets basé sur YOLO
    S'intègre avec la base de données et le contrôleur Arduino existants
    """
    
    def __init__(self, model_path=MODEL_PATH):
        """
        Initialiser le détecteur YOLO
        
        Args:
            model_path: Chemin vers les poids YOLO entraînés (fichier .pt)
        """
        print("\n" + "="*50)
        print("🤖 SMART BIN SI - DÉTECTEUR YOLO")
        print("="*50)
        
        # Charger le modèle YOLO
        self.model = self.load_model(model_path)
        
        # Suivi des détections
        self.last_detection = None
        self.detection_count = 0
        self.last_sort_time = 0
        
        # Initialiser la base de données et le port série si disponibles
        if MAIN_SCRIPT_AVAILABLE:
            self.serial_conn = init_serial_connection()
            self.db_conn, self.db_cursor = init_database()
        else:
            print("⚠ Mode autonome (pas de DB/Arduino)")
            self.serial_conn = None
            self.db_conn = None
            self.db_cursor = None
        
        print("✓ Détecteur initialisé\n")
    
    def load_model(self, model_path):
        """
        Charger le modèle YOLO depuis un fichier
        Supporte YOLOv5 et YOLOv8 via torch.hub ou ultralytics
        """
        print(f"📦 Chargement du modèle depuis : {model_path}")
        
        if not Path(model_path).exists():
            print(f"⚠ Fichier du modèle introuvable : {model_path}")
            print("   Utilisation du YOLOv5s par défaut (pré-entraîné sur COCO)")
            print("   Pour utiliser un modèle custom, entraîne-le d'abord !")
            
            # Charger YOLOv5s pré-entraîné comme solution de secours
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        else:
            # Charger le modèle custom entraîné
            try:
                model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
                print("✓ Modèle custom chargé avec succès")
            except Exception as e:
                print(f"✗ Erreur lors du chargement du modèle custom : {e}")
                print("   Retour au YOLOv5s pré-entraîné")
                model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        
        # Définir les paramètres du modèle
        model.conf = CONFIDENCE_THRESHOLD
        model.iou = IOU_THRESHOLD
        
        # Utiliser le GPU si disponible (important pour Jetson)
        if torch.cuda.is_available():
            model = model.cuda()
            print("✓ Accélération GPU activée")
        else:
            print("⚠ Exécution sur CPU (plus lent)")
        
        return model
    
    def detect_waste(self, frame):
        """
        Exécuter la détection YOLO sur une image
        
        Args:
            frame: Image OpenCV (format BGR)
        
        Retourne:
            results: Résultats de détection YOLO
        """
        # Exécuter l'inférence
        results = self.model(frame)
        return results
    
    def process_detections(self, results):
        """
        Traiter les résultats YOLO et extraire les déchets
        
        Args:
            results: Résultats de détection YOLO
        
        Retourne:
            list: Déchets détectés avec [nom_classe, confiance, bbox]
        """
        detections = []
        
        # Extraire les résultats (format dépend de YOLOv5 vs YOLOv8)
        try:
            # Format YOLOv5
            predictions = results.pandas().xyxy[0]
            
            for idx, row in predictions.iterrows():
                class_name = row['name']
                confidence = row['confidence']
                bbox = [row['xmin'], row['ymin'], row['xmax'], row['ymax']]
                
                detections.append({
                    'class': class_name,
                    'confidence': confidence,
                    'bbox': bbox
                })
        except:
            # Analyse alternative si pandas non disponible
            pred = results.xyxy[0].cpu().numpy()
            for detection in pred:
                x1, y1, x2, y2, conf, cls = detection
                class_name = self.model.names[int(cls)]
                
                detections.append({
                    'class': class_name,
                    'confidence': float(conf),
                    'bbox': [float(x1), float(y1), float(x2), float(y2)]
                })
        
        return detections
    
    def map_to_bin(self, waste_class):
        """
        Mapper une classe de déchet détectée vers la couleur du bac
        
        Args:
            waste_class: Nom de la classe de déchet détectée
        
        Retourne:
            str: Couleur du bac (yellow/green/brown) ou None si inconnu
        """
        # Mapping direct depuis la configuration
        if waste_class in WASTE_TO_BIN_MAPPING:
            return WASTE_TO_BIN_MAPPING[waste_class]
        
        # Solution de secours : vérifier la base de données si disponible
        if MAIN_SCRIPT_AVAILABLE and self.db_cursor:
            bin_color = get_or_assign_bin_color(
                self.db_cursor, 
                self.db_conn, 
                waste_class
            )
            return bin_color
        
        return None
    
    def should_trigger_sort(self, detection):
        """
        Décider si on doit déclencher l'action de tri
        Utilise un filtrage temporel pour éviter les faux positifs
        
        Args:
            detection: Dictionnaire de détection actuel
        
        Retourne:
            bool: True si on doit trier maintenant
        """
        current_time = time.time()
        
        # Vérifier si assez de temps s'est écoulé depuis le dernier tri
        if current_time - self.last_sort_time < AUTO_SORT_DELAY:
            return False
        
        # Vérifier si le même objet est détecté plusieurs fois
        if detection and self.last_detection:
            if detection['class'] == self.last_detection['class']:
                self.detection_count += 1
            else:
                self.detection_count = 1
                self.last_detection = detection
        else:
            self.detection_count = 1
            self.last_detection = detection
        
        # Déclencher si le minimum de détections consécutives est atteint
        if self.detection_count >= MIN_DETECTIONS:
            self.detection_count = 0
            self.last_sort_time = current_time
            return True
        
        return False
    
    def draw_detections(self, frame, detections):
        """
        Dessiner les boîtes de détection et labels sur l'image
        
        Args:
            frame: Image OpenCV
            detections: Liste des dictionnaires de détection
        
        Retourne:
            frame: Image annotée
        """
        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det['bbox']]
            class_name = det['class']
            confidence = det['confidence']
            
            # Obtenir la couleur du bac pour ce déchet
            bin_color = self.map_to_bin(class_name)
            
            # Choisir la couleur d'affichage selon le bac
            if bin_color == "yellow":
                color = (0, 255, 255)  # Jaune en BGR
            elif bin_color == "green":
                color = (0, 255, 0)    # Vert
            elif bin_color == "brown":
                color = (0, 100, 200)  # Marron
            else:
                color = (128, 128, 128)  # Gris pour inconnu
            
            # Dessiner la boîte
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Dessiner le label
            label = f"{class_name} ({confidence:.2f})"
            if bin_color:
                label += f" -> {bin_color}"
            
            cv2.putText(frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame
    
    def run_camera_detection(self):
        """
        Boucle principale : capturer images, détecter déchets, déclencher tri
        """
        # Initialiser la caméra
        if USE_CSI_CAMERA:
            print("📷 Ouverture caméra CSI...")
            pipeline = get_csi_pipeline(width=FRAME_WIDTH, height=FRAME_HEIGHT)
            cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        else:
            print(f"📷 Ouverture caméra : {CAMERA_SOURCE}")
            cap = cv2.VideoCapture(CAMERA_SOURCE)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        
        if not cap.isOpened():
            print("✗ Échec d'ouverture de la caméra")
            return
        
        print("✓ Caméra prête")
        print("\n" + "="*50)
        print("CONTRÔLES :")
        print("  'q' - Quitter")
        print("  's' - Forcer le tri de la détection actuelle")
        print("  'r' - Réinitialiser le compteur de détections")
        print("="*50 + "\n")
        
        fps_time = time.time()
        fps_counter = 0
        fps_display = 0
        
        try:
            while True:
                # Capturer l'image
                ret, frame = cap.read()
                if not ret:
                    print("✗ Échec de lecture de l'image")
                    break
                
                # Exécuter la détection YOLO
                results = self.detect_waste(frame)
                detections = self.process_detections(results)
                
                # Dessiner les détections
                if SHOW_DISPLAY:
                    frame = self.draw_detections(frame, detections)
                
                # Vérifier si on doit déclencher le tri
                if detections:
                    best_detection = max(detections, key=lambda x: x['confidence'])
                    
                    if self.should_trigger_sort(best_detection):
                        waste_class = best_detection['class']
                        bin_color = self.map_to_bin(waste_class)
                        
                        if bin_color:
                            print(f"\n🎯 TRI AUTO DÉCLENCHÉ : {waste_class} → bac {bin_color}")
                            
                            if MAIN_SCRIPT_AVAILABLE and self.serial_conn:
                                send_sorting_command(self.serial_conn, bin_color)
                            else:
                                print(f"   [SIMULATION] Trierait vers {bin_color}")
                        else:
                            print(f"\n⚠ Type de déchet inconnu : {waste_class}")
                
                # Calculer les FPS
                fps_counter += 1
                if time.time() - fps_time > 1.0:
                    fps_display = fps_counter
                    fps_counter = 0
                    fps_time = time.time()
                
                # Afficher les infos sur l'image
                if SHOW_DISPLAY:
                    info_text = f"FPS: {fps_display} | Detections: {len(detections)}"
                    cv2.putText(frame, info_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    if self.last_detection:
                        status_text = f"Suivi: {self.last_detection['class']} ({self.detection_count}/{MIN_DETECTIONS})"
                        cv2.putText(frame, status_text, (10, 60), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    
                    cv2.imshow('Smart Bin - Detection', frame)
                
                # Gérer les entrées clavier
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n👋 Arrêt de la détection...")
                    break
                elif key == ord('s'):
                    if detections and MAIN_SCRIPT_AVAILABLE:
                        best = max(detections, key=lambda x: x['confidence'])
                        bin_color = self.map_to_bin(best['class'])
                        if bin_color:
                            print(f"\n⚡ TRI MANUEL : {best['class']} → {bin_color}")
                            send_sorting_command(self.serial_conn, bin_color)
                elif key == ord('r'):
                    self.detection_count = 0
                    self.last_detection = None
                    print("\n↻ Compteur de détections réinitialisé")
        
        except KeyboardInterrupt:
            print("\n\n⚠ Interrompu par l'utilisateur")
        
        finally:
            # Nettoyage
            cap.release()
            if SHOW_DISPLAY:
                cv2.destroyAllWindows()
            
            if MAIN_SCRIPT_AVAILABLE:
                if self.serial_conn:
                    self.serial_conn.close()
                if self.db_conn:
                    self.db_conn.close()
            
            print("\n✓ Système de détection arrêté\n")


# ============================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================

def main():
    """Exécuter la détection YOLO"""
    detector = WasteDetector()
    detector.run_camera_detection()


if __name__ == "__main__":
    main()