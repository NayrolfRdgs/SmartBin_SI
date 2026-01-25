🗑️ Projet Poubelle Intelligente SIBienvenue dans le dépôt du Centre de Contrôle pour le Tri Robotisé. Ce projet utilise une NVIDIA Jetson Nano couplée à un Arduino pour automatiser le tri des déchets via une interface intelligente et une base de données locale.🚀 Guide d'Installation1. Préparation du Système (OS)OS recommandé : JetPack SDK (basé sur Ubuntu 18.04 ou 20.04).Flashage : Utilisez BalenaEtcher pour graver l'image sur une carte microSD (Min. 32 Go, Classe 10).Initialisation : Suivez l'assistant de configuration au premier démarrage (clavier, WiFi, utilisateur).2. Environnement Python & DépendancesOuvrez un terminal sur votre Jetson et exécutez les commandes suivantes pour préparer l'environnement :Bash# Mise à jour du système
sudo apt-get update && sudo apt-get upgrade -y

# Installation de pip et des outils graphiques
sudo apt-get install python3-pip python3-tk -y

# Installation des bibliothèques nécessaires
pip3 install pyserial
3. Base de DonnéesLe système utilise SQLite, une solution légère idéale pour l'embarqué.Le fichier inventaire_tri.db est créé automatiquement lors du premier lancement du script.Aucune installation de serveur SQL tiers n'est requise.4. Structure du ProjetOrganisez vos fichiers pour garantir le bon fonctionnement des chemins relatifs :Bashmkdir ~/Projet_Poubelle_SI
cd ~/Projet_Poubelle_SI
# Placez ici votre fichier tri_control_center.py
🔌 Connexion Physique (Hardware)ComposantConnexionNote ImportanteArduinoPort USB JetsonCommunication série via /dev/ttyUSB0 ou /dev/ttyACM0ServomoteursPins 9 et 10 (Arduino)Modèle MG996R recommandéAlimentationExterne (5V/6V)NE PAS alimenter les moteurs via l'Arduino (risque de crash Jetson).🛠️ UtilisationLancement du systèmeBashpython3 tri_control_center.py
Cycle de fonctionnementSaisie : Entrez le nom de l'objet dans le terminal.Vérification : Le script interroge la base de données.Décision :Objet connu : L'ordre de tri est envoyé instantanément à l'Arduino.Objet inconnu : L'interface vous invite à sélectionner une catégorie (couleur).Apprentissage : Cochez "Verrouiller (*)" pour mémoriser ce choix et automatiser le tri futur de cet objet.📈 Évolutions futuresIntégration Vision : Migration vers YOLOv6 pour la détection en temps réel.Deep Learning : Nécessite l'installation de PyTorch (inclus dans les bibliothèques CUDA de JetPack).
