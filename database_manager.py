import sqlite3
import os
import shutil
import datetime
from utils import log_error

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.base_dir = os.path.dirname(db_path)
        self.audio_dir = os.path.join(self.base_dir, "audio")
        self.backup_dir = os.path.join(self.base_dir, "backup")
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        self.init_db()

    def init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS patient (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        full_name TEXT NOT NULL,
                        phone_number TEXT,
                        email TEXT,
                        gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
                        birthday DATE NOT NULL,
                        address TEXT,
                        note TEXT
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS appointment (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_patient INTEGER NOT NULL,
                        date DATETIME NOT NULL,
                        diagnose_text TEXT,
                        diagnose_sound TEXT,
                        FOREIGN KEY (id_patient) REFERENCES patient(id)
                    )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_full_name ON patient(full_name)")
                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS update_full_name
                    AFTER INSERT OR UPDATE OF name, last_name ON patient
                    FOR EACH ROW
                    BEGIN
                        UPDATE patient SET full_name = NEW.name || ' ' || NEW.last_name WHERE id = NEW.id;
                    END;
                """)
                conn.commit()
        except sqlite3.Error as e:
            log_error(f"Database initialization failed: {e}")

    def backup_db(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"database_{timestamp}.bak")
            shutil.copy(self.db_path, backup_path)
            # Keep last 5 backups
            backups = sorted(os.listdir(self.backup_dir), reverse=True)
            for old_backup in backups[5:]:
                os.remove(os.path.join(self.backup_dir, old_backup))
        except Exception as e:
            log_error(f"Database backup failed: {e}")

    def add_patient(self, name, last_name, birthday, phone_number=None, email=None, gender=None, address=None, note=None):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO patient (name, last_name, full_name, phone_number, email, gender, birthday, address, note) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (name, last_name, f"{name} {last_name}", phone_number, email, gender, birthday, address, note)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            log_error(f"Add patient failed: {e}")
            return None

    def update_patient(self, patient_id, name, last_name, birthday, phone_number=None, email=None, gender=None, address=None, note=None):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE patient SET name = ?, last_name = ?, full_name = ?, phone_number = ?, email = ?, "
                    "gender = ?, birthday = ?, address = ?, note = ? WHERE id = ?",
                    (name, last_name, f"{name} {last_name}", phone_number, email, gender, birthday, address, note, patient_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            log_error(f"Update patient failed: {e}")
            return False

    def delete_patient(self, patient_id):
        try:
            self.backup_db()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Delete associated appointments and audio files
                cursor.execute("SELECT diagnose_sound FROM appointment WHERE id_patient = ?", (patient_id,))
                for row in cursor.fetchall():
                    if row[0]:
                        try:
                            os.remove(row[0])
                        except OSError:
                            pass
                cursor.execute("DELETE FROM appointment WHERE id_patient = ?", (patient_id,))
                cursor.execute("DELETE FROM patient WHERE id = ?", (patient_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            log_error(f"Delete patient failed: {e}")
            return False

    def get_patient(self, patient_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patient WHERE id = ?", (patient_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            log_error(f"Get patient failed: {e}")
            return None

    def get_all_patients(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, full_name, phone_number, email FROM patient")
                return cursor.fetchall()
        except sqlite3.Error as e:
            log_error(f"Get all patients failed: {e}")
            return []

    def search_patients(self, query):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, full_name, phone_number, email FROM patient WHERE full_name LIKE ? LIMIT 100",
                    (f"%{query}%",)
                )
                return cursor.fetchall()
        except sqlite3.Error as e:
            log_error(f"Search patients failed: {e}")
            return []

    def add_appointment(self, id_patient, date, diagnose_text=None, diagnose_sound=None):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO appointment (id_patient, date, diagnose_text, diagnose_sound) VALUES (?, ?, ?, ?)",
                    (id_patient, date, diagnose_text, diagnose_sound)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            log_error(f"Add appointment failed: {e}")
            return None

    def delete_appointment(self, appointment_id):
        try:
            self.backup_db()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT diagnose_sound FROM appointment WHERE id = ?", (appointment_id,))
                sound_path = cursor.fetchone()[0]
                if sound_path:
                    try:
                        os.remove(sound_path)
                    except OSError:
                        pass
                cursor.execute("DELETE FROM appointment WHERE id = ?", (appointment_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            log_error(f"Delete appointment failed: {e}")
            return False

    def get_appointments_by_patient(self, patient_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, date, diagnose_text FROM appointment WHERE id_patient = ?", (patient_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            log_error(f"Get appointments failed: {e}")
            return []