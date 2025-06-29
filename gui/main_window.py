import datetime
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
from database_manager import DatabaseManager

class MainWindow(QMainWindow):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Doctor App")
        self.resize(400, 400)

        # Track inserted test patient and appointment IDs
        self.inserted_patient_id = 0
        self.inserted_appointment_id = 0

        # Set up UI
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Patient CRUD buttons
        btn_add = QPushButton("Add Test Patient")
        btn_add.clicked.connect(self.add_test_patient)
        layout.addWidget(btn_add)

        btn_get = QPushButton("Get Test Patient")
        btn_get.clicked.connect(self.get_test_patient)
        layout.addWidget(btn_get)

        btn_get_all = QPushButton("Get All Patients")
        btn_get_all.clicked.connect(self.get_all_patients)
        layout.addWidget(btn_get_all)

        btn_delete_all = QPushButton("Delete All Patients")
        btn_delete_all.clicked.connect(self.delete_all_patients)
        layout.addWidget(btn_delete_all)

        self.btn_delete_one = QPushButton("Delete One Patient (ID: 0)")
        self.btn_delete_one.clicked.connect(self.delete_one_patient)
        layout.addWidget(self.btn_delete_one)

        btn_update = QPushButton("Update Test Patient")
        btn_update.clicked.connect(self.update_test_patient)
        layout.addWidget(btn_update)

        # Appointment CRUD buttons
        btn_add_appt = QPushButton("Add Test Appointment")
        btn_add_appt.clicked.connect(self.add_test_appointment)
        layout.addWidget(btn_add_appt)

        btn_get_appt = QPushButton("Get Test Appointment")
        btn_get_appt.clicked.connect(self.get_test_appointment)
        layout.addWidget(btn_get_appt)

        btn_get_all_appts = QPushButton("Get All Appointments")
        btn_get_all_appts.clicked.connect(self.get_all_appointments)
        layout.addWidget(btn_get_all_appts)

        btn_delete_all_appts = QPushButton("Delete All Appointments")
        btn_delete_all_appts.clicked.connect(self.delete_all_appointments)
        layout.addWidget(btn_delete_all_appts)

        self.btn_delete_one_appt = QPushButton("Delete One Appointment (ID: 0)")
        self.btn_delete_one_appt.clicked.connect(self.delete_one_appointment)
        layout.addWidget(self.btn_delete_one_appt)

        btn_update_appt = QPushButton("Update Test Appointment")
        btn_update_appt.clicked.connect(self.update_test_appointment)
        layout.addWidget(btn_update_appt)

    def update_delete_one_button_label(self):
        self.btn_delete_one.setText(f"Delete One Patient (ID: {self.inserted_patient_id})")
        self.btn_delete_one_appt.setText(f"Delete One Appointment (ID: {self.inserted_appointment_id})")

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
        self.inserted_appointment_id = 0
        self.update_delete_one_button_label()
        QMessageBox.information(self, "Success", "Deleted all patients and appointments.")

    def delete_one_patient(self):
        if self.inserted_patient_id == 0:
            QMessageBox.critical(self, "Error", "First add test patient.")
            return
        self.db_manager.delete_patient(patient_id=self.inserted_patient_id)
        QMessageBox.information(self, "Success", f"Deleted patient with ID: {self.inserted_patient_id}")
        self.inserted_patient_id = 0
        self.inserted_appointment_id = 0
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

    def add_test_appointment(self):
        if self.inserted_patient_id == 0:
            QMessageBox.critical(self, "Error", "First add test patient.")
            return
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        appointment_id = self.db_manager.add_appointment(
            id_patient=self.inserted_patient_id,
            date=date,
            diagnose_text="Routine checkup",
            diagnose_sound=None
        )
        if appointment_id:
            self.inserted_appointment_id = appointment_id
            self.update_delete_one_button_label()
            QMessageBox.information(self, "Success", f"Test appointment added with ID: {appointment_id}")
        else:
            QMessageBox.critical(self, "Error", "Failed to add test appointment. Check logs for details.")

    def get_test_appointment(self):
        if self.inserted_appointment_id == 0:
            QMessageBox.critical(self, "Error", "First add test appointment.")
            return
        appointment = self.db_manager.get_appointment(appointment_id=self.inserted_appointment_id)
        if appointment:
            QMessageBox.information(self, "Success", f"Found appointment with ID: {appointment[0]}")
        else:
            QMessageBox.critical(self, "Error", "Failed to find appointment. Check logs for details.")

    def get_all_appointments(self):
        appointments = self.db_manager.get_all_appointments()
        QMessageBox.information(self, "Success", f"Found {len(appointments)} appointments.")

    def delete_all_appointments(self):
        appointments = self.db_manager.get_all_appointments()
        for appointment in appointments:
            self.db_manager.delete_appointment(appointment_id=appointment[0])
        self.inserted_appointment_id = 0
        self.update_delete_one_button_label()
        QMessageBox.information(self, "Success", "Deleted all appointments.")

    def delete_one_appointment(self):
        if self.inserted_appointment_id == 0:
            QMessageBox.critical(self, "Error", "First add test appointment.")
            return
        self.db_manager.delete_appointment(appointment_id=self.inserted_appointment_id)
        QMessageBox.information(self, "Success", f"Deleted appointment with ID: {self.inserted_appointment_id}")
        self.inserted_appointment_id = 0
        self.update_delete_one_button_label()

    def update_test_appointment(self):
        if self.inserted_appointment_id == 0:
            QMessageBox.critical(self, "Error", "First add test appointment.")
            return
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db_manager.update_appointment(
            appointment_id=self.inserted_appointment_id,
            id_patient=self.inserted_patient_id,
            date=date,
            diagnose_text="Updated routine checkup",
            diagnose_sound=None
        )
        QMessageBox.information(self, "Success", f"Updated appointment with ID: {self.inserted_appointment_id}")