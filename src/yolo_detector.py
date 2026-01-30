"""
Smart Bin SI - Détecteur YOLO avec apprentissage au fur et à mesure
- Détecte les objets via caméra
- Demande ta validation : si tu dis "oui c'est correct", l'image est sauvegardée pour réentraîner le modèle
- Utilise waste_classifier pour le tri (DB + Arduino)
"""

import cv2
import torch
import time
import numpy as np
from pathlib import Path
from datetime import datetime

import waste_classifier
from config import (
    MODEL_PATH, CONFIDENCE_THRESHOLD, IOU_THRESHOLD,
    CAMERA_SOURCE, USE_CSI_CAMERA, FRAME_WIDTH, FRAME_HEIGHT, SHOW_DISPLAY,
    AUTO_SORT_DELAY, MIN_DETECTIONS, LEARNING_MODE, SAVE_IMAGES,
    TRAINING_DIR, BIN_COLORS,
)


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
    Utilise waste_classifier pour la logique de tri
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
        self.last_frame = None  # Pour sauvegarder l'image lors de corrections
        
        # Initialiser les connexions via waste_classifier
        waste_classifier.init_serial_connection()
        waste_classifier.init_database()
        
        # Dossier pour les images d'apprentissage (quand tu confirmes "correct")
        if SAVE_IMAGES:
            TRAINING_DIR.mkdir(parents=True, exist_ok=True)
        
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
    
    def get_bin_color_for_display(self, waste_class):
        """
        Obtenir la couleur du bac pour l'affichage (sans trier)
        
        Args:
            waste_class: Nom de la classe de déchet
        
        Retourne:
            str: Couleur du bac ou None
        """
        # Chercher en base de données sans sauvegarder
        bin_color = waste_classifier.get_bin_color(waste_class)
        return bin_color
    
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
            
            # Obtenir la couleur du bac pour ce déchet (juste pour affichage)
            bin_color = self.get_bin_color_for_display(class_name)
            
            color = BIN_COLORS.get(bin_color, BIN_COLORS["unknown"])
            
            # Dessiner la boîte
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Dessiner le label
            label = f"{class_name} ({confidence:.2f})"
            if bin_color:
                label += f" -> {bin_color}"
            else:
                label += " -> ?"
            
            # Fond pour le texte
            (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame, (x1, y1-text_height-10), (x1+text_width, y1), color, -1)
            
            # Texte
            cv2.putText(frame, label, (x1, y1-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return frame
    
    def save_image_for_training(self, frame, class_name, bbox=None, class_id=None, correct=True):
        """
        Sauvegarde une image pour le réentraînement YOLO.
        Quand tu confirmes que la détection est correcte, l'image est stockée
        dans data/training_images/<class_name>/ (+ fichier .txt YOLO si bbox fourni).
        
        Args:
            frame: Image à sauvegarder
            class_name: Nom de la classe (ex: plastic_bottle)
            bbox: [x1, y1, x2, y2] optionnel → génère un .txt au format YOLO
            class_id: index de la classe (pour le .txt YOLO)
            correct: True = bonne détection, False = erreur (sauvegardé dans _errors/)
        """
        if not SAVE_IMAGES:
            return
        class_name = class_name.strip().lower().replace(" ", "_")
        if correct:
            folder = TRAINING_DIR / class_name
        else:
            folder = TRAINING_DIR / "_errors" / class_name
        folder.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = "ok" if correct else "err"
        base = f"{prefix}_{timestamp}"
        filename = folder / f"{base}.jpg"
        cv2.imwrite(str(filename), frame)
        # Fichier label YOLO (une ligne : class_id x_center y_center width height, normalisé 0-1)
        if bbox is not None and class_id is not None and len(bbox) == 4:
            h, w = frame.shape[:2]
            x1, y1, x2, y2 = [float(x) for x in bbox]
            x_center = ((x1 + x2) / 2) / w
            y_center = ((y1 + y2) / 2) / h
            width = (x2 - x1) / w
            height = (y2 - y1) / h
            label_path = folder / f"{base}.txt"
            with open(label_path, "w") as f:
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
        print(f"💾 Image sauvegardée pour apprentissage : {filename.name} ({class_name})")
    
    def _class_name_to_id(self, class_name):
        """Retourne l'index de la classe dans le modèle (pour le label YOLO)."""
        if not hasattr(self.model, "names"):
            return None
        names = self.model.names  # dict int -> str
        for idx, name in names.items():
            if name == class_name:
                return idx
        return None

    def handle_correction(self, frame, best_detection):
        """
        Demande si la détection est correcte ; si oui, sauvegarde l'image (+ label YOLO) pour réentraînement.
        
        Args:
            frame: Image actuelle
            best_detection: dict avec 'class', 'confidence', 'bbox'
        """
        detected_class = best_detection["class"]
        bbox = best_detection.get("bbox")
        class_id = self._class_name_to_id(detected_class)
        
        print(f"\n⚠ YOLO a détecté : '{detected_class}'")
        print("Est-ce correct ?")
        print("  y - Oui, c'est correct → image sauvegardée pour améliorer le modèle")
        print("  n - Non, corriger le nom")
        print("  skip - Ignorer")
        
        choice = input("Votre choix : ").strip().lower()
        
        if choice == 'y':
            print("✓ Détection confirmée → image sauvegardée pour réentraînement")
            self.save_image_for_training(
                frame, detected_class, bbox=bbox, class_id=class_id, correct=True
            )
            return detected_class
        
        elif choice == 'n':
            print("\nQuel est le vrai nom de cet objet ?")
            correct_name = input("Nom correct : ").strip()
            
            if correct_name:
                correct_name = correct_name.strip().lower().replace(" ", "_")
                self.save_image_for_training(frame, correct_name, correct=True)
                self.save_image_for_training(frame, detected_class, correct=False)
                print(f"✓ Correction enregistrée : {detected_class} → {correct_name}")
                return correct_name
        
        print("⊘ Détection ignorée")
        return None
    
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
        if LEARNING_MODE:
            print("  'c' - Corriger la dernière détection")
        print("  'stats' - Voir les statistiques")
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
                
                # Sauvegarder la dernière frame pour corrections
                self.last_frame = frame.copy()
                
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
                        
                        # En mode apprentissage, demander confirmation
                        if LEARNING_MODE:
                            corrected_class = self.handle_correction(self.last_frame, best_detection)
                            if corrected_class is None:
                                continue  # Ignoré par l'utilisateur
                            waste_class = corrected_class
                        
                        print(f"\n🎯 TRI AUTO DÉCLENCHÉ : {waste_class}")
                        
                        # Utiliser waste_classifier pour le tri
                        # ask_if_unknown=True pour permettre d'apprendre
                        bin_color = waste_classifier.classify_and_sort(
                            waste_class,
                            ask_if_unknown=True,
                            auto_mode=False
                        )
                        
                        if bin_color:
                            print(f"✓ Trié vers le bac {bin_color}")
                
                # Calculer les FPS
                fps_counter += 1
                if time.time() - fps_time > 1.0:
                    fps_display = fps_counter
                    fps_counter = 0
                    fps_time = time.time()
                
                # Afficher les infos sur l'image
                if SHOW_DISPLAY:
                    # Info FPS et détections
                    info_text = f"FPS: {fps_display} | Detections: {len(detections)}"
                    cv2.putText(frame, info_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Suivi de détection
                    if self.last_detection:
                        status_text = f"Suivi: {self.last_detection['class']} ({self.detection_count}/{MIN_DETECTIONS})"
                        cv2.putText(frame, status_text, (10, 60), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    
                    # Mode
                    mode_text = "Mode: Apprentissage" if LEARNING_MODE else "Mode: Auto"
                    cv2.putText(frame, mode_text, (10, FRAME_HEIGHT - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
                    
                    cv2.imshow('Smart Bin - Detection', frame)
                
                # Gérer les entrées clavier
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\n👋 Arrêt de la détection...")
                    break
                
                elif key == ord('s'):
                    # Tri manuel forcé
                    if detections:
                        best = max(detections, key=lambda x: x['confidence'])
                        waste_class = best['class']
                        print(f"\n⚡ TRI MANUEL FORCÉ : {waste_class}")
                        waste_classifier.classify_and_sort(
                            waste_class,
                            ask_if_unknown=True,
                            auto_mode=False
                        )
                
                elif key == ord('r'):
                    # Réinitialiser le compteur
                    self.detection_count = 0
                    self.last_detection = None
                    print("\n↻ Compteur de détections réinitialisé")
                
                elif key == ord('c') and LEARNING_MODE:
                    # Corriger la dernière détection
                    if self.last_detection:
                        corrected = self.handle_correction(
                            self.last_frame,
                            self.last_detection
                        )
                        if corrected:
                            bin_color = waste_classifier.ask_user_for_bin(corrected)
                            if bin_color:
                                waste_classifier.save_to_database(corrected, bin_color)
                
                # Commande textuelle pour stats
                # (Note: ne fonctionne que si on redirige stdin, sinon utiliser 's' dans le menu)
        
        except KeyboardInterrupt:
            print("\n\n⚠ Interrompu par l'utilisateur")
        
        finally:
            # Nettoyage
            cap.release()
            if SHOW_DISPLAY:
                cv2.destroyAllWindows()
            
            waste_classifier.cleanup()
            
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