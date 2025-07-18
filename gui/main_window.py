import os
import sys
from functools import partial
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QLineEdit, QTextEdit, QFrame, QGraphicsDropShadowEffect, QSizePolicy, QGridLayout, QListWidgetItem,
    QDialog, QAbstractItemView
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap, QFontDatabase, QFont, QIcon, QFontMetrics
from database_manager import DatabaseManager
from datetime import datetime
from gui.add_patient_dialog import AddPatientDialog
from gui.add_report_dialog import AddReportDialog
from gui.day_report_dialog import DayReportDialog
from gui.patient_card import PatientCard
from gui.update_report_dialog import UpdateReportDialog
from gui.update_patient_dialog import UpdatePatientDialog, WarningDialog
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

# Prozori za appointmente!

class ConfirmDeleteAppointmentDialog(QDialog):
    def __init__(self, message="Da li zaista želite da obrišete izveštaj?", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setFixedSize(350, 150)

        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #d1d5db;  /* svetlosiva granica */
                border-radius: 12px;
            }
            QLabel {
                color: #111827;
                font-size: 14px;
                font-family: 'Inter';
            }
            QPushButton {
                padding: 8px 24px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton#yes_btn {
                background-color: #EF4444;
                color: white;
            }
            QPushButton#yes_btn:hover {
                background-color: #dc2626;
            }
            QPushButton#no_btn {
                background-color: #ffffff;
                color: #111827;
            }
            QPushButton#no_btn:hover {
                background-color: #d1d5db;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(16)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        self.yes_btn = QPushButton("Da")
        self.no_btn = QPushButton("Ne")
        self.yes_btn.setObjectName("yes_btn")
        self.no_btn.setObjectName("no_btn")

        btn_layout.addStretch()
        btn_layout.addWidget(self.yes_btn)
        btn_layout.addWidget(self.no_btn)
        btn_layout.addStretch()

        layout.addWidget(self.label)
        layout.addLayout(btn_layout)

        self.apply_shadow(self.yes_btn)
        self.apply_shadow(self.no_btn)

        self.yes_btn.clicked.connect(self.accept)
        self.no_btn.clicked.connect(self.reject)

        self.slide_in_animation()

    def apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 63))
        widget.setGraphicsEffect(shadow)

    def slide_in_animation(self):
        screen = self.screen().availableGeometry()
        end_rect = self.geometry()

        # Pozicioniraj dijalog pre animacije ispod vidljivog dela
        start_x = (screen.width() - end_rect.width()) // 2
        start_y = screen.height()
        end_x = start_x
        end_y = (screen.height() - end_rect.height()) // 2

        self.setGeometry(start_x, start_y, end_rect.width(), end_rect.height())

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(350)
        self.animation.setStartValue(QRect(start_x, start_y, end_rect.width(), end_rect.height()))
        self.animation.setEndValue(QRect(end_x, end_y, end_rect.width(), end_rect.height()))
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

class AppointmentCard(QFrame):
    clicked = pyqtSignal()
    def __init__(self, appointment_id, date: str, diagnose: str):
        super().__init__()
        self.setObjectName("AppointmentCard")
        self.setFixedHeight(80)
        self.selected = False
        self.appointment_id = appointment_id
        self.full_diagnose = diagnose
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)

        self.hovered = False

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(16)
        self.shadow.setOffset(0, 4)
        self.shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(self.shadow)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(4)

        self.date_label = QLabel(f"Datum: {date}")
        self.date_label.setFont(QFont("Inter", 10, QFont.Weight.Bold))

        self.diagnose_label = QLabel(diagnose)
        self.diagnose_label.setFont(QFont("Inter", 10))
        self.diagnose_label.setWordWrap(False)
        self.diagnose_label.setStyleSheet("color: #374151;")
        self.diagnose_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.diagnose_label.setMaximumHeight(24)
        metrics = QFontMetrics(self.diagnose_label.font())
        elided = metrics.elidedText(diagnose, Qt.TextElideMode.ElideRight, 280)  # širina u pikselima
        self.diagnose_label.setText(elided)

        layout.addWidget(self.date_label)
        layout.addWidget(self.diagnose_label)

        self.update_style()

    def enterEvent(self, event):
        self.hovered = True
        self.update_style()

    def leaveEvent(self, event):
        self.hovered = False
        self.update_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()  # obavesti da je kliknuto
            print("Kliknuto na karticu!")
            super().mousePressEvent(event)  # pozovi default ponašanje

    def set_selected(self, selected: bool):
        self.selected = selected
        self.update_style()

    def update_style(self):
        if self.selected or self.hovered:
            bg_color = "#0C81E4"
            text_color = "white"
        else:
            bg_color = "white"
            text_color = "#111827"

        self.setStyleSheet(f"""
            QFrame#AppointmentCard {{
                background-color: {bg_color};
                border-radius: 12px;
                border: none;
            }}
        """)
        self.date_label.setStyleSheet(f"color: {text_color}; background-color: transparent;")
        self.diagnose_label.setStyleSheet(f"color: {text_color}; background-color: transparent;")


# Prozori za pacijente!


class EditPatientDialog(QDialog):
    def __init__(self, message="Uspešno ste izmenili pacijenta.", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #d1d5db;  /* svetlosiva granica */
                border-radius: 12px;
            }
            QLabel {
                color: #111827;
                font-size: 14px;
                font-family: 'Inter';
            }
            QPushButton {
                background-color: #22C55E;
                color: white;
                font-weight: bold;
                padding: 8px 24px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
        """)
        self.setFixedSize(300, 130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(16)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)

        layout.addWidget(self.label)
        layout.addWidget(self.ok_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # === Primeni shadow efekat na OK dugme ===
        self.apply_shadow(self.ok_btn)
        self.slide_in_animation()

    def apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 63))
        widget.setGraphicsEffect(shadow)

    def slide_in_animation(self):
        screen = self.screen().availableGeometry()
        end_rect = self.geometry()

        # Pozicioniraj dijalog pre animacije ispod vidljivog dela
        start_x = (screen.width() - end_rect.width()) // 2
        start_y = screen.height()
        end_x = start_x
        end_y = (screen.height() - end_rect.height()) // 2

        self.setGeometry(start_x, start_y, end_rect.width(), end_rect.height())

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(350)
        self.animation.setStartValue(QRect(start_x, start_y, end_rect.width(), end_rect.height()))
        self.animation.setEndValue(QRect(end_x, end_y, end_rect.width(), end_rect.height()))
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

class ConfirmDeletePatientDialog(QDialog):
    def __init__(self, message="Da li zaista želite da obrišete pacijenta?", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setFixedSize(350, 150)

        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #d1d5db;  /* svetlosiva granica */
                border-radius: 12px;
            }
            QLabel {
                color: #111827;
                font-size: 14px;
                font-family: 'Inter';
            }
            QPushButton {
                padding: 8px 24px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton#yes_btn {
                background-color: #EF4444;
                color: white;
            }
            QPushButton#yes_btn:hover {
                background-color: #dc2626;
            }
            QPushButton#no_btn {
                background-color: #ffffff;
                color: #111827;
            }
            QPushButton#no_btn:hover {
                background-color: #d1d5db;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(16)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        self.yes_btn = QPushButton("Da")
        self.no_btn = QPushButton("Ne")
        self.yes_btn.setObjectName("yes_btn")
        self.no_btn.setObjectName("no_btn")

        btn_layout.addStretch()
        btn_layout.addWidget(self.yes_btn)
        btn_layout.addWidget(self.no_btn)
        btn_layout.addStretch()

        layout.addWidget(self.label)
        layout.addLayout(btn_layout)

        self.apply_shadow(self.yes_btn)
        self.apply_shadow(self.no_btn)

        self.yes_btn.clicked.connect(self.accept)
        self.no_btn.clicked.connect(self.reject)

        self.slide_in_animation()

    def apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 63))
        widget.setGraphicsEffect(shadow)

    def slide_in_animation(self):
        screen = self.screen().availableGeometry()
        end_rect = self.geometry()

        # Pozicioniraj dijalog pre animacije ispod vidljivog dela
        start_x = (screen.width() - end_rect.width()) // 2
        start_y = screen.height()
        end_x = start_x
        end_y = (screen.height() - end_rect.height()) // 2

        self.setGeometry(start_x, start_y, end_rect.width(), end_rect.height())

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(350)
        self.animation.setStartValue(QRect(start_x, start_y, end_rect.width(), end_rect.height()))
        self.animation.setEndValue(QRect(end_x, end_y, end_rect.width(), end_rect.height()))
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()


class SuccessPatientDialog(QDialog):
    def __init__(self, message="Uspešno ste dodali pacijenta.", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #d1d5db;  /* svetlosiva granica */
                border-radius: 12px;
            }
            QLabel {
                color: #111827;
                font-size: 14px;
                font-family: 'Inter';
            }
            QPushButton {
                background-color: #22C55E;
                color: white;
                font-weight: bold;
                padding: 8px 24px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
        """)
        self.setFixedSize(300, 130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(16)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)

        layout.addWidget(self.label)
        layout.addWidget(self.ok_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # === Primeni shadow efekat na OK dugme ===
        self.apply_shadow(self.ok_btn)
        self.slide_in_animation()

    def apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 63))
        widget.setGraphicsEffect(shadow)

    def slide_in_animation(self):
        screen = self.screen().availableGeometry()
        end_rect = self.geometry()

        # Pozicioniraj dijalog pre animacije ispod vidljivog dela
        start_x = (screen.width() - end_rect.width()) // 2
        start_y = screen.height()
        end_x = start_x
        end_y = (screen.height() - end_rect.height()) // 2

        self.setGeometry(start_x, start_y, end_rect.width(), end_rect.height())

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(350)
        self.animation.setStartValue(QRect(start_x, start_y, end_rect.width(), end_rect.height()))
        self.animation.setEndValue(QRect(end_x, end_y, end_rect.width(), end_rect.height()))
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()

# Kraj prozora za pacijente!

class MainWindow(QMainWindow):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Doktorska evidencija")
        self.resize(1000, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # Skini sistemski title bar

        # Učitaj font
        font_path = resource_path("assets/Inter-VariableFont_opsz,wght.ttf")
        #font_path = os.path.join("assets", "Inter-VariableFont_opsz,wght.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print("Greška: Font nije učitan!")
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.setFont(QFont(font_family))

        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QWidget {
                font-family: 'Inter';
                font-size: 14px;
            }
            QLabel {
                color: #111827;
            }
            QLabel.bold {
                font-weight: bold;
                font-size: 16px;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ccc;
                border-radius: 12px;
                padding: 6px;
                background-color: #ffffff;
            }
            QListWidget {
                border: none;
                background-color: #f9f9f9;
            }
            QPushButton {
                height: 36px;
                padding: 6px 16px;
                border-radius: 18px;
                border: none;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """)

        self.setup_ui()

    def apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 63))
        widget.setGraphicsEffect(shadow)

    def setup_ui(self):
        wrapper = QVBoxLayout()
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.setSpacing(0)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setLayout(wrapper)

        # Custom title bar
        wrapper.addWidget(self.create_title_bar())

        # Glavni sadržaj
        content = QHBoxLayout()
        wrapper.addLayout(content)

        content.addWidget(self.create_left_panel())
        content.addWidget(self.create_right_panel())
        self.load_patients()

    # Funkcije vezane za pacijente!

    def load_patients(self):
        self.patient_list.clear()
        self.cards = []

        patients = self.db_manager.get_all_patients()
        for i, patient in enumerate(patients):
            full_name = patient[1]
            birthday = patient[2]
            if birthday:
                birth_year = str(birthday).split("-")[0]
            else:
                birth_year = "N/A"

            card = PatientCard(full_name, birth_year)
            item = QListWidgetItem()
            item.setSizeHint(card.sizeHint())
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)

            self.patient_list.addItem(item)
            self.patient_list.setItemWidget(item, card)
            self.cards.append(card)

        #if self.cards:
        #    self.select_patient(0)

        self.patient_list.currentRowChanged.connect(self.select_patient)

    def select_patient(self, index):
        for i, card in enumerate(self.cards):
            card.set_selected(i == index)

        if 0 <= index < len(self.cards):
            patient = self.db_manager.get_all_patients()[index]
            self.selected_patient_id = patient[0]
            self.update_patient_info(patient)
            self.load_appointment_history(patient[0])  # Dodaj ovo

    def update_patient_info(self, patient):
        full_name = patient[1] or "-"
        birth_date = patient[2] or "-"
        address = patient[3] or "-"
        gender = patient[4] or "-"
        note = patient[5] or ""

        birth_date_str = "-"
        try:
            if isinstance(birth_date, str):
                dt = datetime.fromisoformat(birth_date)
                birth_date_str = dt.strftime("%d.%m.%Y.")
            elif hasattr(birth_date, 'strftime'):
                birth_date_str = birth_date.strftime("%d.%m.%Y.")
            else:
                birth_date_str = str(birth_date)
        except:
            birth_date_str = str(birth_date)

        self.label_name.setText(f"Pacijent: {full_name}")
        self.label_birthday.setText(f"Datum rođenja: {birth_date_str}")
        self.label_address.setText(f"Adresa: {address}")
        self.label_gender.setText(f"Pol: {gender}")
        self.note_edit.setPlainText(note)

        self.history_list.clear()  # zasad prazno

    def on_add_patient(self):

        dialog = AddPatientDialog(self)
        if dialog.exec():  # ako je kliknuto "Sačuvaj"
            data = dialog.get_data()

            # Razdvajamo ime i prezime
            name_parts = data["full_name"].strip().split(" ", 1)
            name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            # Čuvamo u bazu
            self.db_manager.add_patient(
                name=name,
                last_name=last_name,
                birthday=data["birthday"],
                gender=data["gender"],
                address=data["address"],
                phone_number=None,
                email=None,
                note=data["note"]
            )

            self.load_patients()  # osvežimo prikaz

            dialog = SuccessPatientDialog(parent=self)
            dialog.exec()

    def on_edit_patient(self):
        current_row = self.patient_list.currentRow()
        if current_row < 0:
            warning = WarningDialog("Molimo Vas da prvo selektujete pacijenta.", self)
            warning.exec()
            return

        all_patients = self.db_manager.get_all_patients()
        selected_patient = all_patients[current_row]
        patient_id = selected_patient[0]

        patient_data = self.db_manager.get_patient(patient_id)
        if not patient_data:
            print("Greška: Pacijent nije pronađen.")
            return

        dialog = UpdatePatientDialog(self)
        try:
            dialog.set_data({
                "full_name": patient_data[3],  # full_name
                "birthday": patient_data[7],  # birthday
                "gender": patient_data[6],  # gender
                "address": patient_data[8],  # address
                "note": patient_data[9],  # note
            })
        except IndexError as e:
            print("Greška pri učitavanju podataka:", e)
            return

        if dialog.exec():
            updated = dialog.get_data()
            name_parts = updated["full_name"].strip().split(" ", 1)
            name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            self.db_manager.update_patient(
                patient_id=patient_id,
                name=name,
                last_name=last_name,
                birthday=updated["birthday"],
                gender=updated["gender"],
                address=updated["address"],
                note=updated["note"]
            )
            self.load_patients()

            dialog = EditPatientDialog(parent=self)
            dialog.exec()

    def on_delete_patient(self):
        current_row = self.patient_list.currentRow()
        if current_row < 0:
            return  # ništa nije selektovano

        dialog = ConfirmDeletePatientDialog(parent=self)
        if dialog.exec():  # korisnik kliknuo "Da"
            selected_patient = self.db_manager.get_all_patients()[current_row]
            self.db_manager.delete_patient(selected_patient[0])
            self.load_patients()

    def filter_patients(self, text):
        text = text.lower()
        for i in range(self.patient_list.count()):
            item = self.patient_list.item(i)
            widget = self.patient_list.itemWidget(item)
            if isinstance(widget, PatientCard):  # Dodaj sigurnosnu proveru
                full_name = widget.name_label.text().lower()
                item.setHidden(text not in full_name)

    # Funkcije vezane za appointmente!

    def on_edit_appointment(self):
        selected_index = self.history_list.currentRow()
        if selected_index < 0:
            warning = WarningDialog("Molimo Vas da prvo selektujete izveštaj.", self)
            warning.exec()
            return

        item = self.history_list.item(selected_index)
        widget = self.history_list.itemWidget(item)

        if not isinstance(widget, AppointmentCard) or not hasattr(widget, "appointment_id"):
            warning = WarningDialog("Ne mogu da pronađem izabrani izveštaj.", self)
            warning.exec()
            return

        appointment_id = widget.appointment_id
        date_str = widget.date_label.text().replace("Datum: ", "").strip()
        diagnose_text = widget.full_diagnose

        dialog = UpdateReportDialog(
            appointment_id=appointment_id,
            patient_id=self.selected_patient_id,
            db_manager=self.db_manager,
            refresh_callback=self.load_appointment_history,
            parent=self
        )

        dialog.set_data({
            "date": date_str,
            "diagnose_text": diagnose_text
        })

        dialog.exec()

    def on_delete_appointment(self):
        selected_row = self.history_list.currentRow()
        if selected_row < 0:
            warning = WarningDialog("Molimo Vas da prvo selektujete izveštaj.", self)
            warning.exec()
            return

        item = self.history_list.item(selected_row)
        widget = self.history_list.itemWidget(item)

        if not isinstance(widget, AppointmentCard):
            warning = WarningDialog("Ne mogu da pronađem izabrani izveštaj.", self)
            warning.exec()
            return

        appointment_id = widget.appointment_id

        dialog = ConfirmDeleteAppointmentDialog(
            "Da li ste sigurni da želite da obrišete izveštaj?", parent=self
        )
        if dialog.exec():
            success = self.db_manager.delete_appointment(appointment_id)
            if success:
                self.load_appointment_history(self.selected_patient_id)

    def on_add_report(self):
        current_row = self.patient_list.currentRow()
        if current_row < 0:
            warning = WarningDialog("Molimo Vas da prvo selektujete pacijenta.", self)
            warning.exec()
            return  # nijedan pacijent nije selektovan

        patient = self.db_manager.get_all_patients()[current_row]
        patient_id = patient[0]

        dialog = AddReportDialog(
            patient_id=patient_id,
            db_manager=self.db_manager,
            refresh_callback=self.load_appointment_history,  # 🟢 povezujemo osvežavanje
            parent=self
        )
        dialog.exec()

    def select_appointment_card(self, selected_card):
        for card in self.appointment_cards:
            card.set_selected(card == selected_card)

    def load_appointment_history(self, patient_id):
        self.history_list.clear()
        self.appointment_cards = []

        self.appointment_ids = []  # čuvamo ID-jeve redom

        appointments = self.db_manager.get_appointments_by_patient_id(patient_id)
        for appointment in appointments:
            appointment_id, date, diagnose = appointment
            self.appointment_ids.append(appointment_id)
            card = AppointmentCard(appointment_id, date, diagnose)
            card.full_diagnose = diagnose

            # poveži klik
            card.clicked.connect(partial(self.select_appointment_card, card))
            self.appointment_cards.append(card)

            item = QListWidgetItem()
            item.setSizeHint(card.sizeHint())
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.history_list.addItem(item)
            self.history_list.setItemWidget(item, card)

    # Dugme za day report!

    def on_day_report(self):
        dialog = DayReportDialog(self.db_manager, self)
        dialog.exec()


    # Custom title bar!

    def create_title_bar(self):
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: #0C81E4;")

        layout = QGridLayout(title_bar)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(0)

        # === LOGO ===
        logo = QLabel()
        logo.setPixmap(QPixmap(resource_path("assets/icons/logo.png")).scaled(74, 68, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(logo, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # === NASLOV ===
        title = QLabel("Doktorska evidencija")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        # === IKONICE ===
        icon_container = QWidget()
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(4)

        btn_min = QPushButton()
        btn_min.setIcon(QIcon(resource_path("assets/icons/minimize.png")))
        btn_min.setFixedSize(24, 24)
        btn_min.setStyleSheet("border: none;")
        btn_min.clicked.connect(self.showMinimized)

        btn_max = QPushButton()
        btn_max.setIcon(QIcon(resource_path("assets/icons/maximize.png")))
        btn_max.setFixedSize(24, 24)
        btn_max.setStyleSheet("border: none;")
        btn_max.clicked.connect(self.toggle_maximize_restore)

        btn_close = QPushButton()
        btn_close.setIcon(QIcon(resource_path("assets/icons/close.png")))
        btn_close.setFixedSize(24, 24)
        btn_close.setStyleSheet("border: none;")
        btn_close.clicked.connect(self.close)

        icon_layout.addWidget(btn_min)
        icon_layout.addWidget(btn_max)
        icon_layout.addWidget(btn_close)

        layout.addWidget(icon_container, 0, 2, alignment=Qt.AlignmentFlag.AlignRight  | Qt.AlignmentFlag.AlignVCenter)

        layout.setColumnStretch(0, 1)  # logo
        layout.setColumnStretch(1, 2)  # title
        layout.setColumnStretch(2, 1)  # icons

        return title_bar

    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_pos = event.globalPosition().toPoint()
            if self.isMaximized():
                self.showNormal()
                self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, "_is_dragging") and self._is_dragging:
            self.move(self.pos() + event.globalPosition().toPoint() - self._drag_pos)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False

    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)

        #=== Pretraga ===
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(12, 4, 12, 4)
        search_layout.setSpacing(8)
        search_container.setStyleSheet("background-color: #f3f4f6; border-radius: 18px;")

        icon_label = QLabel()
        icon_label.setFixedSize(16, 16)
        icon_label.setPixmap(QPixmap(resource_path("assets/icons/search.png")).scaled(16, 16))
        icon_label.setStyleSheet("background-color: transparent;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pretraži pacijente")
        self.search_input.setFont(QFont("Montserrat", 11, QFont.Weight.Medium))
        self.search_input.setStyleSheet("border: none; background-color: transparent; font-size: 14px;")
        self.search_input.textChanged.connect(self.filter_patients)

        search_layout.addWidget(icon_label)
        search_layout.addWidget(self.search_input)
        self.apply_shadow(search_container)
        layout.addWidget(search_container)

        # === Lista pacijenata ===
        self.patient_list = QListWidget()
        self.patient_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.patient_list.verticalScrollBar().setSingleStep(10)
        self.patient_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: none;
                border-radius: 12px;
                padding: 6px;
            }
            QListWidget::item {
                background: transparent;
                border: none;
            }
            QListWidget::item:selected {
                background: transparent;
            }
            QListWidget::item:hover {
                background: transparent;
            }
            
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 2px 0 2px 0;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #D1D5DB;
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9CA3AF;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        self.patient_list.setSpacing(8)
        self.patient_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.apply_shadow(self.patient_list)

        layout.addWidget(self.patient_list)

        # === Dugmad za pacijente ===
        button_layout = QHBoxLayout()

        # Dodaj pacijenta
        btn_add_patient = QPushButton("Dodaj pacijenta")
        btn_add_patient.setFont(QFont("Montserrat", 11, QFont.Weight.Medium))
        btn_add_patient.setStyleSheet("""
            QPushButton {
                background-color: #22C55E;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 24px;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
        """)
        self.apply_shadow(btn_add_patient)
        btn_add_patient.clicked.connect(self.on_add_patient)
        button_layout.addWidget(btn_add_patient)

        # Izmeni pacijenta
        btn_edit_patient = QPushButton("Izmeni pacijenta")
        btn_edit_patient.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #111827;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 24px;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)
        self.apply_shadow(btn_edit_patient)
        btn_edit_patient.clicked.connect(self.on_edit_patient)  # Definiši metodu
        button_layout.addWidget(btn_edit_patient)

        # Obriši pacijenta
        btn_delete_patient = QPushButton("Obriši pacijenta")
        btn_delete_patient.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 24px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        self.apply_shadow(btn_delete_patient)
        btn_delete_patient.clicked.connect(self.on_delete_patient)  # Definiši metodu
        button_layout.addWidget(btn_delete_patient)

        # Dodaj layout u glavni layout
        layout.addLayout(button_layout)

        return panel

    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # === Informacije o pacijentu ===
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(4)
        info_layout.setContentsMargins(12, 12, 12, 12)  # Umesto paddinga u stilu
        info_frame.setStyleSheet("background-color: #ffffff; border-radius: 12px;")
        self.apply_shadow(info_frame)

        # Podaci o pacijentu sa manjim razmakom
        grid = QGridLayout()
        grid.setHorizontalSpacing(0)
        grid.setVerticalSpacing(2)
        grid.setContentsMargins(0, 0, 0, 0)

        self.label_name = QLabel()
        self.label_name.setStyleSheet("font-weight: bold;")

        self.label_birthday = QLabel()
        self.label_address = QLabel()
        self.label_gender = QLabel()

        grid.addWidget(self.label_name, 0, 0)
        grid.addWidget(self.label_birthday, 1, 0)
        grid.addWidget(self.label_address, 2, 0)
        grid.addWidget(self.label_gender, 3, 0)

        info_layout.addLayout(grid)

        # Napomena
        note_label = QLabel("Napomena:")
        note_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        info_layout.addWidget(note_label)

        self.note_edit = QTextEdit()
        self.note_edit.setReadOnly(True)
        self.note_edit.setFixedHeight(200)
        self.note_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        #self.apply_shadow(self.note_edit)

        self.note_edit.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 12px;
                padding: 10px;
                font-family: 'Inter';
                font-size: 14px;
                color: #111827;
            }
            QTextEdit:focus {
                border: 1px solid #0C81E4;
                outline: none;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 2px 0 2px 0;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #D1D5DB;
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9CA3AF;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        info_layout.addWidget(self.note_edit)

        layout.addWidget(info_frame)

        # === Istorija pregleda ===
        history_frame = QFrame()
        history_layout = QVBoxLayout(history_frame)
        history_layout.setContentsMargins(4, 12, 4, 12)
        history_frame.setStyleSheet("background-color: #ffffff; border-radius: 12px;")
        self.apply_shadow(history_frame)

        history_label = QLabel("Istorija pregleda")
        history_label.setStyleSheet("font-weight: bold;"
                                    "padding-left: 12px")

        self.history_list = QListWidget()
        self.history_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.history_list.verticalScrollBar().setSingleStep(10)
        self.history_list.setSpacing(14)
        self.history_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
            }
            QListWidget::item {
                background: transparent;
                margin-bottom: 12px;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 2px 0 2px 0;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #D1D5DB;
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9CA3AF;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

        history_layout.addWidget(history_label)
        history_layout.addWidget(self.history_list)
        layout.addWidget(history_frame)

        # === Dugmad ===
        button_layout = QHBoxLayout()

        btn_add_report = QPushButton("Dodaj izveštaj")
        btn_add_report.clicked.connect(self.on_add_report)
        btn_add_report.setStyleSheet("""
            QPushButton {
                background-color: #22C55E;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 24px;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
        """)
        self.apply_shadow(btn_add_report)

        btn_edit_report = QPushButton("Izmeni izveštaj")
        btn_edit_report.clicked.connect(self.on_edit_appointment)
        btn_edit_report.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #111827;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 24px;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)
        self.apply_shadow(btn_edit_report)

        btn_delete_report = QPushButton("Obriši izveštaj")
        btn_delete_report.clicked.connect(self.on_delete_appointment)
        btn_delete_report.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 24px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        self.apply_shadow(btn_delete_report)

        btn_day_report = QPushButton("Pregled dana")
        btn_day_report.clicked.connect(self.on_day_report)
        btn_day_report.setStyleSheet("""
                    QPushButton {
                        background-color: #0C81E4;
                        color: #ffffff;
                        font-weight: bold;
                        padding: 8px 16px;
                        border-radius: 24px;
                    }
                    QPushButton:hover {
                        background-color: #3696ea;
                    }
                """)
        self.apply_shadow(btn_day_report)

        button_layout.addWidget(btn_add_report)
        button_layout.addWidget(btn_edit_report)
        button_layout.addWidget(btn_delete_report)
        button_layout.addWidget(btn_day_report)


        layout.addLayout(button_layout)
        return panel
