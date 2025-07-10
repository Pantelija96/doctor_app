from PyQt6.QtCore import Qt, QDate, QSize, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QPushButton, QHBoxLayout, QTextEdit, QLabel, QDateEdit, \
    QVBoxLayout, QDialog, QWidget

class WarningDialog(QDialog):
    def __init__(self, message="Niste popunili sva potrebna polja!", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
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
    def __init__(self, message="Uspešno ste dodali izvestaj!", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
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
        self.patient_id = patient_id
        self.db_manager = db_manager
        self.refresh_callback = refresh_callback
        self.setWindowTitle("Dodaj izveštaj")
        self.resize(500, 550)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: white;")

        # === Glavni layout ===
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.create_title_bar())

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(16)

        # === Datum pregleda ===
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

        # === Dijagnoza tekst ===
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

        # === Započni snimanje ===
        self.record_btn = QPushButton("Započni snimanje")
        self.record_btn.setIcon(QIcon("assets/icons/zapocni_snimanje_ikonica.png"))
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
        self.apply_shadow(self.record_btn)
        content_layout.addWidget(self.record_btn)

        # === Donja dugmad ===
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

    def save_report(self):
        diagnose_text = self.diagnose_input.toPlainText().strip()
        date_str = self.date_input.date().toString("yyyy-MM-dd")

        if not diagnose_text:
            warning = WarningDialog("Polje za dijagnozu ne sme biti prazno.", self)
            warning.exec()
            return

        appointment_id = self.db_manager.add_appointment(
            id_patient=self.patient_id,
            date=date_str,
            diagnose_text=diagnose_text,
            diagnose_sound=None  # kada dodaješ snimanje, ovde dodaš
        )

        if appointment_id:
            # 🔄 Osvežavanje istorije pregleda
            if hasattr(self, "refresh_callback") and self.refresh_callback:
                self.refresh_callback(self.patient_id)

            dialog = SuccessDialog("Uspešno ste dodali izveštaj!", self)
            dialog.exec()
            self.accept()
        else:
            warning = WarningDialog("Došlo je do greške pri dodavanju izveštaja.", self)
            warning.exec()

    def create_title_bar(self):
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: #0C81E4;")
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(10, 0, 10, 0)

        logo = QLabel()
        logo.setPixmap(QPixmap("assets/icons/logo.png").scaled(24, 24))
        layout.addWidget(logo)

        title = QLabel("Dodaj izveštaj")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        close_btn = QPushButton()
        close_btn.setIcon(QIcon("assets/icons/close.png"))
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