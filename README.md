# SIpoubelle

Guide d'Installation : Poubelle Intelligente SICe document détaille les étapes pour transformer votre NVIDIA Jetson Nano en centre de contrôle pour le tri robotisé.1. Choix et Installation de l'OSOS : Utilisez JetPack SDK (basé sur Ubuntu 18.04 ou 20.04 selon votre version de Jetson).Flashage : Utilisez BalenaEtcher pour graver l'image ISO sur une carte microSD (minimum 32 Go, classe 10).Premier démarrage : Suivez les étapes de configuration (langue, clavier, WiFi).2. Préparation de l'Environnement PythonOuvrez un terminal sur la Jetson et installez les dépendances nécessaires :# Mise à jour du système
sudo apt-get update
sudo apt-get upgrade

# Installation de pip et des outils python
sudo apt-get install python3-pip
sudo apt-get install python3-tk

# Installation des bibliothèques de communication et d'interface
pip3 install pyserial
3. Mise en place de la Base de DonnéesLe script Python gère la création automatique de la base de données SQLite (inventaire_tri.db). Vous n'avez pas besoin d'installer de serveur SQL lourd, SQLite est un simple fichier local idéal pour la Jetson.4. Organisation des FichiersCréez un dossier dédié pour le projet :mkdir ~/Projet_Poubelle_SI
cd ~/Projet_Poubelle_SI
Placez-y votre fichier principal :tri_control_center.py (Le code de l'interface et de la logique).5. Connexion PhysiqueArduino : Branchez-le via USB à l'un des ports de la Jetson.Moteurs : Connectez vos servomoteurs MG996R à l'Arduino (Pins 9 et 10).Alimentation : IMPORTANT Utilisez une alimentation externe pour les moteurs. Ne les alimentez pas via l'Arduino seul, la Jetson risquerait de s'éteindre à cause de la chute de tension.6. Lancement du SystèmePour démarrer votre centre de contrôle :python3 tri_control_center.py
7. Fonctionnement du Cycle de TriSaisie : Tapez le nom de l'objet dans le terminal.Vérification : Le script cherche dans inventaire_tri.db.Décision :Si connu : L'ordre est envoyé à l'Arduino.Si inconnu : L'interface graphique s'illumine et vous demande de cliquer sur une couleur.Verrouillage : Cochez la case "Verrouiller (*)" pour que l'objet soit traité automatiquement la prochaine fois.Note : Pour le futur passage à YOLOv6, il faudra installer PyTorch et les drivers NVIDIA spécifiques au Deep Learning (inclus dans JetPack).
