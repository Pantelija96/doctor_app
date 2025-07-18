import base64
import sys
import tempfile
import webbrowser

from PyQt6.QtCore import Qt, QDate, QSize, QPropertyAnimation, QRect, QEasingCurve, QUrl
from PyQt6.QtGui import QColor, QIcon, QPixmap, QDesktopServices
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QPushButton, QHBoxLayout, QTextEdit, QLabel, QDateEdit, \
    QVBoxLayout, QDialog, QWidget
import os

from report_generator import generate_appointment_pdf
from speech_processor import SpeechProcessor

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

class WarningDialog(QDialog):
    def __init__(self, message="Niste popunili sva potrebna polja!", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #d1d5db;  /* svetlosiva granica */
                border-radius: 12px;
            }
            QLabel {
                color: #DC2626;
                font-size: 14px;
                font-family: 'Inter';
            }
            QPushButton {
                background-color: #DC2626;
                color: white;
                font-weight: bold;
                padding: 8px 24px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        self.setFixedSize(500, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(16)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)

        layout.addWidget(self.label)
        layout.addWidget(self.ok_btn, alignment=Qt.AlignmentFlag.AlignCenter)

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

class SuccessDialog(QDialog):
    def __init__(self, message="Uspešno ste dodali izveštaj!", parent=None):
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

class AddReportDialog(QDialog):
    def __init__(self, patient_id, db_manager, refresh_callback=None, parent=None):
        super().__init__(parent)
        print("AddReportDialog initialized")  # Debug
        self.patient_id = patient_id
        self.db_manager = db_manager
        self.refresh_callback = refresh_callback
        self.setWindowTitle("Dodaj izveštaj")
        self.resize(500, 550)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: white;")
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #d1d5db;  /* svetlosiva granica */
                border-radius: 12px;
            }
        """)

        # Initialize SpeechProcessor with updated audio directory
        appdata_path = os.getenv('APPDATA') or os.path.expanduser('~/AppData/Roaming')
        audio_dir = os.path.join(appdata_path, 'DoctorApp', 'data', 'audio')
        try:
            self.speech_processor = SpeechProcessor(audio_dir)
        except Exception as e:
            warning = WarningDialog(f"Greška pri inicijalizaciji snimanja: {str(e)}", self)
            warning.exec()
            self.speech_processor = None
        self.is_recording = False
        self.audio_path = None

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.create_title_bar())

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(16)

        # Date input
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd.MM.yyyy.")
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setFixedHeight(36)
        self.date_input.setStyleSheet(""" QDateEdit { border: 1px solid #ccc; background-color: white; padding: 6px; border-radius: 10px; } QDateEdit::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 24px; border-left: 1px solid #ccc; } QDateEdit::down-arrow { image: url(assets/icons/down-arrow.png); width: 12px; height: 12px; } """)
        self.apply_shadow(self.date_input)

        calendar = self.date_input.calendarWidget()
        calendar.setStyleSheet(
            """ QCalendarWidget QToolButton#qt_calendar_prevmonth, QCalendarWidget QToolButton#qt_calendar_nextmonth { qproperty-icon: url(assets/icons/left-arrow.png); width: 24px; height: 24px; icon-size: 12px; border-radius: 12px; } QCalendarWidget QToolButton#qt_calendar_nextmonth { qproperty-icon: url(assets/icons/right-arrow.png); } QCalendarWidget QToolButton { color: black; } """)

        content_layout.addWidget(QLabel("Datum pregleda"))
        content_layout.addWidget(self.date_input)

        # Diagnosis input
        self.diagnose_input = QTextEdit()
        self.diagnose_input.setPlaceholderText("Unesite dijagnozu...")
        self.diagnose_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 12px;
                padding: 8px;
                background-color: white;
            }
        """)
        self.diagnose_input.setMinimumHeight(200)
        self.apply_shadow(self.diagnose_input)

        content_layout.addWidget(QLabel("Dijagnoza / Simptomi"))
        content_layout.addWidget(self.diagnose_input)

        # Record button
        self.record_btn = QPushButton("Započni snimanje")
        record_icon_path = resource_path("assets/icons/zapocni_snimanje_ikonica.png")
        self.record_btn.setIcon(QIcon(record_icon_path if os.path.exists(record_icon_path) else ""))
        self.record_btn.setIconSize(QSize(18, 18))
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #0C81E4;
                color: white;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #0967b2;
            }
        """)
        self.record_btn.setFixedHeight(40)
        self.record_btn.clicked.connect(self.toggle_recording)
        self.apply_shadow(self.record_btn)
        content_layout.addWidget(self.record_btn)

        # Connect transcription signal
        if self.speech_processor:
            self.speech_processor.transcription_completed.connect(self.handle_transcription)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Sačuvaj")
        self.save_btn.clicked.connect(self.save_report)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #22C55E;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 24px;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
        """)
        self.apply_shadow(self.save_btn)

        self.print_btn = QPushButton("Štampaj")
        self.print_btn.clicked.connect(self.print_pdf)
        self.print_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 24px;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)
        self.apply_shadow(self.print_btn)

        self.cancel_btn = QPushButton("Otkaži")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 24px;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        self.apply_shadow(self.cancel_btn)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.print_btn)
        btn_layout.addWidget(self.cancel_btn)

        content_layout.addLayout(btn_layout)
        main_layout.addLayout(content_layout)

    def showEvent(self, event):
        super().showEvent(event)
        screen = self.screen().availableGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def toggle_recording(self):
        if not self.speech_processor:
            warning = WarningDialog("Snimanje nije dostupno.", self)
            warning.exec()
            return
        if not self.is_recording:
            if self.speech_processor.start_recording():
                self.is_recording = True
                self.record_btn.setText("Zaustavi snimanje")
                stop_icon_path = resource_path("assets/icons/zapocni_snimanje_ikonica.png")
                self.record_btn.setIcon(QIcon(stop_icon_path if os.path.exists(stop_icon_path) else ""))
        else:
            audio_path, text = self.speech_processor.stop_recording()
            self.is_recording = False
            self.record_btn.setText("Započni snimanje")
            record_icon_path = resource_path("assets/icons/zapocni_snimanje_ikonica.png")
            self.record_btn.setIcon(QIcon(record_icon_path if os.path.exists(record_icon_path) else ""))
            if audio_path:
                self.audio_path = audio_path

    def handle_transcription(self, audio_path, text):
        if audio_path:
            self.audio_path = audio_path
            current_text = self.diagnose_input.toPlainText().strip()
            if current_text:
                self.diagnose_input.setPlainText(current_text + "\n" + text)
            else:
                self.diagnose_input.setPlainText(text)
        else:
            warning = WarningDialog(text, self)
            warning.exec()

    def save_report(self):
        diagnose_text = self.diagnose_input.toPlainText().strip()
        date_str = self.date_input.date().toString("yyyy-MM-dd")

        if not diagnose_text:
            warning = WarningDialog("Polje za dijagnozu ne sme biti prazno.", self)
            warning.exec()
            return

        try:
            appointment_id = self.db_manager.add_appointment(
                id_patient=self.patient_id,
                date=date_str,
                diagnose_text=diagnose_text,
                diagnose_sound=self.audio_path
            )
            if appointment_id:
                if hasattr(self, "refresh_callback") and self.refresh_callback:
                    self.refresh_callback(self.patient_id)
                dialog = SuccessDialog("Uspešno ste dodali izveštaj!", self)
                dialog.exec()
                self.accept()
            else:
                warning = WarningDialog("Došlo je do greške pri dodavanju izveštaja.", self)
                warning.exec()
        except Exception as e:
            warning = WarningDialog(f"Greška pri čuvanju izveštaja: {str(e)}", self)
            warning.exec()

    def create_title_bar(self):
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: #0C81E4;"
                                "border-top-left-radius: 12px;"
                                "border-top-right-radius: 12px;")
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(10, 0, 10, 0)

        logo = QLabel()
        logo_path = resource_path("assets/icons/logo.png")
        logo.setPixmap(QPixmap(logo_path if os.path.exists(logo_path) else "").scaled(68, 62))
        layout.addWidget(logo)

        title = QLabel("Dodaj izveštaj")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        close_btn = QPushButton()
        close_icon_path = resource_path("assets/icons/close.png")
        close_btn.setIcon(QIcon(close_icon_path if os.path.exists(close_icon_path) else ""))
        close_btn.setStyleSheet("border: none;")
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        return title_bar

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, "_is_dragging") and self._is_dragging:
            self.move(self.pos() + event.globalPosition().toPoint() - self._drag_pos)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False

    def apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 63))
        widget.setGraphicsEffect(shadow)

    def print_pdf(self):
        try:
            # Get current inputs
            diagnose_text = self.diagnose_input.toPlainText( ).strip( )
            if not diagnose_text:
                warning = WarningDialog("Unesite dijagnozu pre štampe.", self)
                warning.exec( )
                return

            patient = self.db_manager.get_patient(self.patient_id)
            if not patient:
                warning = WarningDialog("Podaci o pacijentu nisu pronađeni.", self)
                warning.exec( )
                return

            patient_data = {
                "full_name": f"{patient[1]} {patient[2]}",  # name + last_name
                "birthday": patient[7],  # birthday
                "address": patient[8] or ""  # address
            }

            logo_path = resource_path("assets/icons/pdfLogo.png")
            pdf_base64 = generate_appointment_pdf(patient_data, diagnose_text, logo_path = logo_path)

            # Decode and save as temp PDF
            pdf_data = base64.b64decode(pdf_base64)
            with tempfile.NamedTemporaryFile(delete = False, suffix = ".pdf") as f:
                f.write(pdf_data)
                temp_path = f.name

            # Open in default web browser
            webbrowser.open(f"file:///{temp_path.replace(os.sep, '/')}")
        except Exception as e:
            warning = WarningDialog(f"Greška pri štampi: {str(e)}", self)
            warning.exec( )