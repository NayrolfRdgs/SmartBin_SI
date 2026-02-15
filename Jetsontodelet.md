📁 SmartBin_SI - Guide d'Installation NVIDIA Jetson

Ce guide explique comment configurer le projet SmartBin_SI sur une plateforme NVIDIA Jetson (Nano, Xavier, ou Orin). Il couvre l'installation de l'IDE, la gestion des droits matériels et l'isolation de l'environnement Python.
📍 Sommaire

    Permissions Matérielles (USB/Arduino)

    Installation de l'IDE (VS Code)

    Configuration de l'Environnement Python

    Installation des Dépendances

    Astuces pour VS Code

1. Permissions Matérielles (USB/Arduino)

Sur Jetson, l'accès aux ports série (USB) est restreint. Si l'IDE Arduino affiche une erreur de type Permission Denied, exécutez ces commandes :
Bash

# Ajoute l'utilisateur actuel au groupe dialout
sudo usermod -a -G dialout $USER

# Force la prise en compte du groupe sans redémarrer (pour la session actuelle)
newgrp dialout

# RECOMMANDÉ : Redémarrer la Jetson pour stabiliser les droits système
sudo reboot

2. Installation de l'IDE (VS Code)

Pour développer directement sur la Jetson, nous installons la version officielle optimisée pour l'architecture ARM64 :
Bash

# Mise à jour des paquets
sudo apt update && sudo apt install -y curl

# Téléchargement du paquet .deb ARM64
curl -L https://go.microsoft.com/fwlink/?LinkID=760868 -o vscode.deb

# Installation
sudo apt install ./vscode.deb

# Nettoyage
rm vscode.deb

Lancement : Tapez code dans le terminal.
3. Configuration de l'Environnement Python

Pour éviter de casser les librairies NVIDIA (JetPack), on utilise un environnement virtuel.
Bash

# Récupération du projet
git clone https://github.com/NayrolfRdgs/SmartBin_SI.git
cd SmartBin_SI

# Installation des outils venv
sudo apt install -y python3-venv python3-pip

# Création de l'environnement virtuel
python3 -m venv smartbin_env

# Activation de l'environnement
source smartbin_env/bin/activate

4. Installation des Dépendances

    [!IMPORTANT]
    Les Jetson utilisent des versions spécifiques de OpenCV et PyTorch optimisées pour CUDA. Si elles sont déjà installées via JetPack, ne les réinstallez pas avec pip.

Bash

# Mise à jour de base
pip install --upgrade pip setuptools wheel

# Installation des dépendances du projet
pip install -r requirements.txt

5. Astuces pour VS Code

Pour transformer VS Code en une station de travail complète pour la Jetson :
Extension	Utilité
Python (Microsoft)	Gestion du virtual env et IntelliSense.
Arduino (Microsoft)	Permet de compiler/téléverser sans ouvrir l'IDE Arduino.
Remote - SSH	(Optionnel) Pour coder sur la Jetson depuis votre PC principal.
🛠 Dépannage rapide

    Port USB non détecté : Vérifiez avec lsusb et assurez-vous que le câble est un câble de données (pas uniquement de charge).

    Erreur CUDA : Vérifiez que vous n'êtes pas dans l'environnement virtuel pour les tests GPU, ou liez les bibliothèques système au venv avec --system-site-packages.
