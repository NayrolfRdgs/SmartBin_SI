"""
Smart Bin SI - Base de données (objet → bac) + Arduino (tri)
Utilisé par yolo_detector.py pour le tri et l'apprentissage des associations.
"""

import sqlite3
import serial
import serial.tools.list_ports
from pathlib import Path
from datetime import datetime

# Import config (depuis src/ ou en package)
try:
    from config import (
        DB_PATH, ARDUINO_PORT, BAUD_RATE, SORTING_DURATION,
        VALID_BINS, WASTE_TO_BIN_MAPPING,
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from config import (
        DB_PATH, ARDUINO_PORT, BAUD_RATE, SORTING_DURATION,
        VALID_BINS, WASTE_TO_BIN_MAPPING,
    )

# Connexions globales
_conn = None
_serial = None


def init_database():
    """Crée la base SQLite et la table si besoin."""
    global _conn
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    _conn = sqlite3.connect(str(DB_PATH))
    _conn.execute("""
        CREATE TABLE IF NOT EXISTS waste_classification (
            item_name TEXT PRIMARY KEY,
            bin_color TEXT NOT NULL,
            created_at TEXT,
            usage_count INTEGER DEFAULT 1
        )
    """)
    _conn.commit()


def init_serial_connection():
    """Ouvre la connexion série vers l'Arduino. En mode simulation si pas d'Arduino."""
    global _serial
    if _serial is not None:
        return
    try:
        _serial = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        # Laisser le temps à l'Arduino de reset
        import time
        time.sleep(2)
        print("✓ Arduino connecté")
    except Exception as e:
        print(f"⚠ Arduino non détecté ({e}) - mode simulation")
        _serial = None


def init_serial():
    """Alias pour compatibilité."""
    init_serial_connection()


def cleanup():
    """Ferme la DB et la série."""
    global _conn, _serial
    if _conn:
        _conn.close()
        _conn = None
    if _serial and _serial.is_open:
        _serial.close()
        _serial = None


def get_bin_color(item_name):
    """
    Retourne la couleur du bac pour un objet (sans sauvegarder).
    Cherche en DB, sinon mapping par défaut dans config.
    """
    if not item_name:
        return None
    item_name = item_name.strip().lower()
    # 1. Base de données
    if _conn:
        try:
            row = _conn.execute(
                "SELECT bin_color FROM waste_classification WHERE item_name = ?",
                (item_name,)
            ).fetchone()
            if row:
                return row[0]
        except sqlite3.OperationalError:
            pass
    # 2. Mapping par défaut (config)
    return WASTE_TO_BIN_MAPPING.get(item_name)


def save_to_database(item_name, bin_color):
    """Enregistre ou met à jour l'association objet → bac."""
    if not _conn or bin_color not in VALID_BINS:
        return False
    item_name = item_name.strip().lower()
    now = datetime.now().isoformat()
    try:
        _conn.execute("""
            INSERT INTO waste_classification (item_name, bin_color, created_at, usage_count)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(item_name) DO UPDATE SET
                bin_color = excluded.bin_color,
                usage_count = usage_count + 1
        """, (item_name, bin_color, now))
        _conn.commit()
        return True
    except Exception:
        return False


def ask_user_for_bin(item_name):
    """
    Demande à l'utilisateur dans quel bac mettre cet objet.
    Retourne la couleur du bac ou None si annulé.
    """
    print(f"\n📦 Objet inconnu : '{item_name}'")
    print("Dans quel bac le mettre ?")
    for i, b in enumerate(VALID_BINS, 1):
        print(f"  {i} - {b}")
    print("  0 - Annuler")
    try:
        choice = input("Choix : ").strip()
        if choice == "0":
            return None
        idx = int(choice)
        if 1 <= idx <= len(VALID_BINS):
            return VALID_BINS[idx - 1]
    except (ValueError, IndexError):
        pass
    return None


def send_sort_command(bin_color):
    """Envoie la commande de tri à l'Arduino."""
    if _serial and _serial.is_open:
        try:
            _serial.write(f"{bin_color}\n".encode())
            _serial.flush()
        except Exception as e:
            print(f"⚠ Erreur envoi Arduino : {e}")
            return False
    else:
        print(f"[Simulation] → Tri vers bac {bin_color}")
    return True


def classify_and_sort(item_name, ask_if_unknown=True, auto_mode=False):
    """
    Détermine le bac pour l'objet, enregistre si nouveau, envoie la commande de tri.
    - ask_if_unknown: si True, demande à l'utilisateur pour un objet inconnu
    - auto_mode: si True, utilise uniquement le mapping sans demander
    Retourne la couleur du bac utilisée, ou None.
    """
    if not item_name:
        return None
    item_name = item_name.strip().lower()
    bin_color = get_bin_color(item_name)

    if bin_color is None:
        if ask_if_unknown and not auto_mode:
            bin_color = ask_user_for_bin(item_name)
            if bin_color:
                save_to_database(item_name, bin_color)
        else:
            return None
    else:
        # Incrémenter usage_count
        if _conn:
            try:
                _conn.execute(
                    "UPDATE waste_classification SET usage_count = usage_count + 1 WHERE item_name = ?",
                    (item_name,)
                )
                _conn.commit()
            except Exception:
                pass

    if bin_color:
        send_sort_command(bin_color)
        if _serial and _serial.is_open:
            import time
            time.sleep(SORTING_DURATION)
    return bin_color


def get_stats():
    """Retourne les stats de la base (pour affichage)."""
    if not _conn:
        return []
    try:
        return _conn.execute("""
            SELECT item_name, bin_color, usage_count
            FROM waste_classification
            ORDER BY usage_count DESC
        """).fetchall()
    except Exception:
        return []


# ============================================
# MODE MANUEL (sans caméra) : saisie du nom d'objet
# ============================================

def run_manual_mode():
    """Boucle interactive : tu tapes le nom de l'objet, le système trie (DB + Arduino)."""
    init_database()
    init_serial_connection()
    print("\n🤖 SMART BIN SI - MODE MANUEL (sans caméra)")
    print("Tape le nom d'un objet pour lancer le tri. 'stats' = statistiques, 'quit' = quitter.\n")
    try:
        while True:
            name = input("Objet > ").strip()
            if not name:
                continue
            if name.lower() == "quit":
                break
            if name.lower() == "stats":
                rows = get_stats()
                print("\n📊 Base de données :")
                for r in rows:
                    print(f"  {r[0]:20} → {r[1]} ({r[2]} utilisations)")
                print()
                continue
            bin_color = classify_and_sort(name, ask_if_unknown=True, auto_mode=False)
            if bin_color:
                print(f"✓ Tri vers bac {bin_color}\n")
            else:
                print("⊘ Annulé ou objet inconnu.\n")
    finally:
        cleanup()


if __name__ == "__main__":
    run_manual_mode()
