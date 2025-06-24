import datetime
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
from database_manager import DatabaseManager


class MainWindow(QMainWindow):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Doctor App")
        self.resize(400, 200)

        # Track inserted test patient ID
        self.inserted_patient_id = 0

        # Set up UI
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add test patient button
        btn_add = QPushButton("Add Test Patient")
        btn_add.clicked.connect(self.add_test_patient)
        layout.addWidget(btn_add)

        # Get test patient button
        btn_get = QPushButton("Get Test Patient")
        btn_get.clicked.connect(self.get_test_patient)
        layout.addWidget(btn_get)

        # Get all patients button
        btn_get_all = QPushButton("Get All Patients")
        btn_get_all.clicked.connect(self.get_all_patients)
        layout.addWidget(btn_get_all)

        # Delete all patients button
        btn_delete_all = QPushButton("Delete All Patients")
        btn_delete_all.clicked.connect(self.delete_all_patients)
        layout.addWidget(btn_delete_all)

        # Delete one patient button
        self.btn_delete_one = QPushButton("Delete One Patient (ID: 0)")
        self.btn_delete_one.clicked.connect(self.delete_one_patient)
        layout.addWidget(self.btn_delete_one)

        # Update test patient button
        btn_update = QPushButton("Update Test Patient")
        btn_update.clicked.connect(self.update_test_patient)
        layout.addWidget(btn_update)

    def update_delete_one_button_label(self):
        self.btn_delete_one.setText(f"Delete One Patient (ID: {self.inserted_patient_id})")

    def add_test_patient(self):
        birthday = datetime.datetime.strptime("2.4.1996", "%d.%m.%Y").strftime("%Y-%m-%d %H:%M:%S")
        patient_id = self.db_manager.add_patient(
            name="Pantelija",
            last_name="Stosic",
            birthday=birthday,
            phone_number="+123123123",
            email="pantelijastosic@gmail.com",
            gender="Male",
            address="Grocka",
            note="Bez beleški"
        )
        if patient_id:
            self.inserted_patient_id = patient_id
            self.update_delete_one_button_label()
            QMessageBox.information(self, "Success", f"Test patient added with ID: {patient_id}")
        else:
            QMessageBox.critical(self, "Error", "Failed to add test patient. Check logs for details.")

    def get_test_patient(self):
        if self.inserted_patient_id == 0:
            QMessageBox.critical(self, "Error", "First add test patient.")
            return
        patient = self.db_manager.get_patient(patient_id=self.inserted_patient_id)
        if patient:
            QMessageBox.information(self, "Success", f"Found patient with ID: {patient[0]}")
        else:
            QMessageBox.critical(self, "Error", "Failed to find patient. Check logs for details.")

    def get_all_patients(self):
        patients = self.db_manager.get_all_patients()
        QMessageBox.information(self, "Success", f"Found {len(patients)} patients.")

    def delete_all_patients(self):
        patients = self.db_manager.get_all_patients()
        for patient in patients:
            self.db_manager.delete_patient(patient_id=patient[0])
        self.inserted_patient_id = 0
        self.update_delete_one_button_label()
        QMessageBox.information(self, "Success", "Deleted all patients.")

    def delete_one_patient(self):
        if self.inserted_patient_id == 0:
            QMessageBox.critical(self, "Error", "First add test patient.")
            return
        self.db_manager.delete_patient(patient_id=self.inserted_patient_id)
        QMessageBox.information(self, "Success", f"Deleted patient with ID: {self.inserted_patient_id}")
        self.inserted_patient_id = 0
        self.update_delete_one_button_label()

    def update_test_patient(self):
        if self.inserted_patient_id == 0:
            QMessageBox.critical(self, "Error", "First add test patient.")
            return
        birthday = datetime.datetime.strptime("2.4.1996", "%d.%m.%Y").strftime("%Y-%m-%d %H:%M:%S")
        self.db_manager.update_patient(
            patient_id=self.inserted_patient_id,
            name="Pantelija Update",
            last_name="Stosic Update",
            birthday=birthday,
            phone_number="+123123123",
            email="pantelijastosic@gmail.com",
            gender="Male",
            address="Grocka",
            note="Bez beleški"
        )
        QMessageBox.information(self, "Success", f"Updated patient with ID: {self.inserted_patient_id}")
