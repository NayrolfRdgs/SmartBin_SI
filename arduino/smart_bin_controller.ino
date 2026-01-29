/**
 * ============================================
 * SMART BIN SI - Contrôleur Arduino
 * ============================================
 * 
 * DESCRIPTION :
 * Contrôleur de plateforme double-axe pour le tri automatique des déchets
 * 
 * CONFIGURATION DES BACS :
 * - Brown  : 30°  | Bascule HAUT   (vers 0°)
 * - Yellow : 150° | Bascule HAUT   (vers 0°)
 * - Green  : 90°  | Bascule BAS    (vers 180°)
 * 
 * MATÉRIEL :
 * - 2x Servomoteurs MG996R
 * - NVIDIA Jetson Nano (via USB Série)
 * 
 * AUTEUR : FlowCreativeStudio
 * DATE : 2026
 * ============================================
 */

#include <Servo.h>

// ============================================
// OBJETS SERVO
// ============================================
Servo orientationServo;  // Rotation de la plateforme gauche/droite
Servo tiltServo;         // Inclinaison de la plateforme haut/bas

// ============================================
// CONFIGURATION DES BROCHES
// ============================================
const int ORIENTATION_PIN = 10;
const int TILT_PIN = 9;

// ============================================
// CONSTANTES DE POSITION (degrés)
// ============================================

// Angles d'orientation (rotation)
const int POSITION_REST = 90;      // Position centrale/neutre
const int ANGLE_BROWN = 30;        // Position bac marron
const int ANGLE_YELLOW = 150;      // Position bac jaune
const int ANGLE_GREEN = 90;        // Position bac vert (centre)

// Angles d'inclinaison (vidage)
const int TILT_UP = 20;            // Vidage vers le haut (proche de 0°)
const int TILT_DOWN = 160;         // Vidage vers le bas (proche de 180°)

// ============================================
// CONSTANTES DE TIMING (millisecondes)
// ============================================
const int DELAY_ORIENTATION = 1000;    // Temps pour tourner vers la position
const int DELAY_DUMP = 600;            // Temps pour basculer pour le vidage
const int DELAY_VIBRATION = 150;       // Durée de chaque secousse
const int VIBRATION_COUNT = 4;         // Nombre de secousses
const int DELAY_RETURN = 400;          // Pause avant retour
const int DELAY_RESET = 500;           // Temps pour retour au repos

// Amplitude de vibration
const int VIBRATION_AMPLITUDE = 20;    // Degrés de mouvement pendant la secousse


// ============================================
// SETUP - EXÉCUTÉ UNE FOIS
// ============================================
void setup() {
  // Initialiser la communication série
  Serial.begin(9600);
  
  // Attacher les servos aux broches
  orientationServo.attach(ORIENTATION_PIN);
  tiltServo.attach(TILT_PIN);
  
  // Initialiser en position de repos (à plat et centré)
  orientationServo.write(POSITION_REST);
  tiltServo.write(POSITION_REST);
  
  // Message de démarrage
  Serial.println("Smart Bin SI - Controleur Arduino Pret");
  Serial.println("En attente de commandes : yellow, green, brown");
}


// ============================================
// BOUCLE PRINCIPALE
// ============================================
void loop() {
  // Vérifier si des données sont disponibles sur le port série
  if (Serial.available() > 0) {
    // Lire la commande jusqu'au retour à la ligne
    String command = Serial.readStringUntil('\n');
    command.trim();  // Supprimer les espaces
    
    // Exécuter la séquence de tri selon la commande
    if (command == "brown") {
      executeSortingSequence(ANGLE_BROWN, "BROWN", 0);  // 0 = bascule HAUT
    } 
    else if (command == "yellow") {
      executeSortingSequence(ANGLE_YELLOW, "YELLOW", 0);  // 0 = bascule HAUT
    }
    else if (command == "green") {
      executeSortingSequence(ANGLE_GREEN, "GREEN", 1);  // 1 = bascule BAS
    }
    else {
      // Commande inconnue
      Serial.print("Erreur : Commande inconnue '");
      Serial.print(command);
      Serial.println("'");
    }
  }
}


// ============================================
// FONCTION DE SÉQUENCE DE TRI
// ============================================
/**
 * Exécute la séquence complète de tri
 * 
 * @param targetAngle      Angle de rotation cible (30°/90°/150°)
 * @param binName          Nom du bac pour le débogage
 * @param tiltDirection    0 = HAUT (vers 0°), 1 = BAS (vers 180°)
 */
void executeSortingSequence(int targetAngle, String binName, int tiltDirection) {
  Serial.print("Cible : ");
  Serial.print(binName);
  Serial.print(" bac | ");
  
  // Calculer l'angle de vidage selon la direction
  int dumpAngle = (tiltDirection == 0) ? TILT_UP : TILT_DOWN;
  
  // PHASE 1 : ORIENTATION
  // Tourner la plateforme vers le bac cible
  Serial.print("Rotation vers ");
  Serial.print(targetAngle);
  Serial.print("°... ");
  
  orientationServo.write(targetAngle);
  delay(DELAY_ORIENTATION);
  
  // PHASE 2 : VIDAGE
  // Incliner la plateforme pour libérer les déchets
  Serial.print("Basculement ");
  Serial.print(tiltDirection == 0 ? "HAUT" : "BAS");
  Serial.print("... ");
  
  tiltServo.write(dumpAngle);
  delay(DELAY_DUMP);
  
  // PHASE 3 : VIBRATION
  // Secouer la plateforme pour assurer la libération complète
  Serial.print("Secouage... ");
  
  for (int i = 0; i < VIBRATION_COUNT; i++) {
    // Secouer en se déplaçant légèrement vers la position de repos
    if (tiltDirection == 0) {
      tiltServo.write(dumpAngle + VIBRATION_AMPLITUDE);  // Bouger vers 90°
    } else {
      tiltServo.write(dumpAngle - VIBRATION_AMPLITUDE);  // Bouger vers 90°
    }
    delay(DELAY_VIBRATION);
    
    // Retourner à la position de vidage
    tiltServo.write(dumpAngle);
    delay(DELAY_VIBRATION);
  }
  
  // PHASE 4 : RETOUR AU REPOS
  // Retourner en position neutre pour l'objet suivant
  Serial.print("Retour... ");
  
  delay(DELAY_RETURN);
  
  // D'abord niveler l'inclinaison
  tiltServo.write(POSITION_REST);
  delay(DELAY_RESET);
  
  // Puis centrer la rotation
  orientationServo.write(POSITION_REST);
  
  Serial.println("✓ Termine");
}


// ============================================
// FONCTIONS UTILITAIRES
// ============================================

/**
 * Arrêt d'urgence - retour immédiat en position de repos
 * Peut être appelé via la commande série "STOP"
 */
void emergencyStop() {
  orientationServo.write(POSITION_REST);
  tiltServo.write(POSITION_REST);
  Serial.println("ARRET D'URGENCE - Retour en position de repos");
}

/**
 * Mode calibration - balaye lentement toutes les positions
 */
void calibrationMode() {
  Serial.println("Demarrage de la calibration...");
  
  // Test servo d'orientation
  Serial.println("Test orientation (30° -> 150°)");
  for (int angle = 30; angle <= 150; angle += 10) {
    orientationServo.write(angle);
    Serial.print(angle);
    Serial.print("° ");
    delay(500);
  }
  Serial.println();
  
  // Retour au centre
  orientationServo.write(POSITION_REST);
  delay(1000);
  
  // Test servo d'inclinaison
  Serial.println("Test inclinaison (20° -> 160°)");
  for (int angle = 20; angle <= 160; angle += 10) {
    tiltServo.write(angle);
    Serial.print(angle);
    Serial.print("° ");
    delay(500);
  }
  Serial.println();
  
  // Retour au repos
  tiltServo.write(POSITION_REST);
  Serial.println("Calibration terminee");
}