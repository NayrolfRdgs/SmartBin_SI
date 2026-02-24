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

# Option d'interface utilisateur web
try:
    from config import USER_INTERFACE_ENABLED, USER_INTERFACE_PORT
except Exception:
    USER_INTERFACE_ENABLED = False
    USER_INTERFACE_PORT = 5001

if USER_INTERFACE_ENABLED:
    import requests
    import time

# Connexions globales
_conn = None
_serial = None


def init_database():
    """Crée la base SQLite et toutes les tables si besoin."""
    global _conn
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    _conn = sqlite3.connect(str(DB_PATH))
    
    # Table 1 : Classification (objet → bac)
    _conn.execute("""
        CREATE TABLE IF NOT EXISTS waste_classification (
            item_name TEXT PRIMARY KEY,
            bin_color TEXT NOT NULL,
            created_at TEXT,
            usage_count INTEGER DEFAULT 1
        )
    """)
    
    # Table 2 : Historique de tri (pour tracking remplissage)
    _conn.execute("""
        CREATE TABLE IF NOT EXISTS sorting_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bin_color TEXT NOT NULL,
            item_name TEXT,
            timestamp TEXT NOT NULL,
            confidence REAL DEFAULT 1.0
        )
    """)
    
    # Table 3 : État des bacs (remplissage, dernière vidange)
    _conn.execute("""
        CREATE TABLE IF NOT EXISTS bin_status (
            bin_color TEXT PRIMARY KEY,
            fill_level REAL DEFAULT 0.0,
            item_count INTEGER DEFAULT 0,
            last_emptied TEXT,
            capacity_liters REAL DEFAULT 10.0
        )
    """)
    
    # Initialiser les bacs s'ils n'existent pas
    from config import VALID_BINS
    for bin_color in VALID_BINS:
        _conn.execute("""
            INSERT OR IGNORE INTO bin_status (bin_color, last_emptied)
            VALUES (?, ?)
        """, (bin_color, datetime.now().isoformat()))
    
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
    # Si l'interface utilisateur web est activée, tenter d'envoyer la question
    if USER_INTERFACE_ENABLED:
        try:
            url = f"http://127.0.0.1:{USER_INTERFACE_PORT}/api/ask"
            resp = requests.post(url, json={'item_name': item_name}, timeout=2)
            if resp.ok:
                data = resp.json()
                task_id = data.get('task_id')
                # Poller la réponse (timeout total ~20s)
                answer_url = f"http://127.0.0.1:{USER_INTERFACE_PORT}/api/answer/{task_id}"
                start = time.time()
                while time.time() - start < 20:
                    r = requests.get(answer_url, timeout=2)
                    if r.ok:
                        ans = r.json()
                        if ans.get('answered'):
                            bin_color = ans.get('bin_color')
                            if bin_color in VALID_BINS:
                                return bin_color
                            else:
                                return None
                    time.sleep(0.5)
        except Exception:
            pass

    # Fallback console
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


def classify_and_sort(item_name, ask_if_unknown=True, auto_mode=False, confidence=1.0):
    """
    Détermine le bac pour l'objet, enregistre si nouveau, envoie la commande de tri.
    - ask_if_unknown: si True, demande à l'utilisateur pour un objet inconnu
    - auto_mode: si True, utilise uniquement le mapping sans demander
    - confidence: confiance de la détection (0-1)
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
        # LOG LA DÉTECTION
        log_detection(bin_color, item_name, confidence)
        
        # Envoyer commande Arduino
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


def log_detection(bin_color, item_name, confidence=1.0):
    """Enregistre une détection dans l'historique."""
    if not _conn:
        return False
    try:
        _conn.execute("""
            INSERT INTO sorting_history (bin_color, item_name, timestamp, confidence)
            VALUES (?, ?, ?, ?)
        """, (bin_color, item_name, datetime.now().isoformat(), confidence))
        
        # Mise à jour du bac : +1 item
        _conn.execute("""
            UPDATE bin_status 
            SET item_count = item_count + 1,
                fill_level = fill_level + 0.5
            WHERE bin_color = ?
        """, (bin_color,))
        
        _conn.commit()
        return True
    except Exception as e:
        print(f"⚠ Erreur log_detection : {e}")
        return False


def get_bin_status():
    """Retourne l'état des 3 bacs (remplissage, items, dernière vidange)."""
    if not _conn:
        return []
    try:
        return _conn.execute("""
            SELECT bin_color, fill_level, item_count, last_emptied, capacity_liters
            FROM bin_status
            ORDER BY bin_color ASC
        """).fetchall()
    except Exception as e:
        print(f"⚠ Erreur get_bin_status : {e}")
        return []


def empty_bin(bin_color):
    """Vide un bac (reset remplissage et compteur)."""
    if not _conn:
        return False
    try:
        _conn.execute("""
            UPDATE bin_status
            SET fill_level = 0, item_count = 0, last_emptied = ?
            WHERE bin_color = ?
        """, (datetime.now().isoformat(), bin_color))
        _conn.commit()
        return True
    except Exception:
        return False


def get_detection_history(limit=50):
    """Retourne l'historique des détections."""
    if not _conn:
        return []
    try:
        return _conn.execute("""
            SELECT bin_color, item_name, timestamp, confidence
            FROM sorting_history
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,)).fetchall()
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