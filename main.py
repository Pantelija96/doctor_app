import sys
import os
from PyQt6.QtWidgets import QApplication
from database_manager import DatabaseManager
from gui.main_window import MainWindow

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)

def main():
    # Set app data directory
    app_data_dir = os.path.join(os.path.expandvars(r"%APPDATA%\DoctorApp"), "data")
    os.makedirs(app_data_dir, exist_ok=True)
    db_path = os.path.join(app_data_dir, "database.db")

    # Initialize database
    db_manager = DatabaseManager(db_path)
    print("Database initialized successfully.")

    app = QApplication(sys.argv)

    window = MainWindow(db_manager)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()