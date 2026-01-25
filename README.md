# 🤖 Smart Bin SI | Control Center

> **Système de tri robotisé piloté par NVIDIA Jetson Nano & Arduino.**

---

## 🛠 Architecture du Système

Le projet transforme la **Jetson Nano** en unité centrale de traitement (IA & Logique) communiquant en série avec un **Arduino** chargé de l'exécution mécanique.

### 1. Initialisation de l'OS

* **Système :** [NVIDIA JetPack SDK](https://developer.nvidia.com/embedded/jetpack)
* **Procédure :** 1. Télécharger l'image SD adaptée.
2. Flasher via `BalenaEtcher`.
3. Allouer au moins **32 Go** (Classe 10) pour éviter les goulots d'étranglement.

### 2. Stack Logicielle

Exécutez ce bloc pour configurer l'environnement Python et les accès matériels :

```bash
# Update System
sudo apt-get update && sudo apt-get upgrade -y

# Core Dependencies
sudo apt-get install -y python3-pip python3-tk

# Hardware Communication
pip3 install pyserial

```

---

## 📂 Organisation du Workspace

Il est recommandé de respecter la structure suivante pour le déploiement :

```text
Projet_Poubelle_SI/
├── 📄 tri_control_center.py   # Logique principale & GUI
├── 🗃️ inventaire_tri.db       # DB SQLite (Générée automatiquement)
└── 📜 README.md               # Documentation

```

---

## ⚡ Schéma de Connexion

| Composant | Interface | Description |
| --- | --- | --- |
| **Jetson Nano** | USB Type A | Maître (Calcul & Interface) |
| **Arduino Uno** | USB Type B | Esclave (Contrôle Servos) |
| **Servos MG996R** | PWM D9 / D10 | Actionneurs de tri |

> [!CAUTION]
> **ALIMENTATION EXTERNE REQUISE** : Les servomoteurs MG996R tirent un courant de crête important. Utilisez une alimentation 5V/3A dédiée pour éviter de griller les ports USB de la Jetson.

---

## 🕹️ Workflow de Tri

```python
# Lancement de l'unité de contrôle
python3 tri_control_center.py

```

### Logique de Décision :

1. **Input** ➔ Saisie utilisateur (Nom de l'objet).
2. **Lookup** ➔ Requête SQL dans `inventaire_tri.db`.
3. **Conditionnelle** :
* `IF EXISTS` ➔ Envoi du code `Serial` vers Arduino.
* `ELSE` ➔ Appel de l'UI (User Input) pour assignation de couleur.


4. **Learning** ➔ Si `Verrouiller (*)` est actif, insertion de la nouvelle règle en base.

---

## 🔭 Roadmap : Vision par Ordinateur

Le passage à **YOLOv6** est la prochaine étape majeure.

* **Pré-requis :** PyTorch & Drivers CUDA (inclus dans JetPack).
* **Objectif :** Suppression de la saisie manuelle pour un tri 100% autonome par caméra.

Souhaitez-vous que je rédige le **code Arduino (C++)** correspondant pour gérer les signaux envoyés par la Jetson ?
