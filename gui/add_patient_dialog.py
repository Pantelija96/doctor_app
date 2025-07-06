from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QDateEdit, QComboBox, QWidget, QGridLayout, QTextEdit
)
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect


class WarningDialog(QDialog):
    def __init__(self, message="Polje 'Ime i prezime' ne sme biti prazno.", parent=None):
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
        self.setFixedSize(350, 130)

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

class AddPatientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dodaj pacijenta")
        self.resize(800, 450)
        self.setStyleSheet("background-color: white;")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # === Glavni layout: title bar + sadržaj ===
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # === Custom title bar ===
        main_layout.addWidget(self.create_title_bar())

        # === Sadržaj ===
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)
        content_layout.setContentsMargins(24, 24, 24, 24)

        # Leva kolona
        left_layout = QVBoxLayout()
        left_layout.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ime i prezime")
        left_layout.addWidget(QLabel("Ime i prezime:"))
        left_layout.addWidget(self.name_input)
        self.name_input.setFixedHeight(36)
        self.name_input.setMinimumWidth(320)
        self.name_input.setStyleSheet(
            """ QLineEdit { padding: 4px; border: 1px solid #ccc; border-radius: 10px; background-color: #ffffff; } """)
        self.apply_shadow(self.name_input)

        self.date_input = QDateEdit()
        self.date_input.setDisplayFormat("dd.MM.yyyy.")
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        left_layout.addWidget(QLabel("Datum rođenja:"))
        left_layout.addWidget(self.date_input)
        self.date_input.setFixedHeight(36)
        self.date_input.setMinimumWidth(320)
        self.apply_shadow(self.date_input)
        self.date_input.setStyleSheet(
            """ QDateEdit { border: 1px solid #ccc; background-color: white; padding: 6px; border-radius: 10px; } QDateEdit::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 24px; border-left: 1px solid #ccc; } QDateEdit::down-arrow { image: url(assets/icons/down-arrow.png); width: 12px; height: 12px; } """)

        calendar = self.date_input.calendarWidget()
        calendar.setStyleSheet(
            """ QCalendarWidget QToolButton#qt_calendar_prevmonth, QCalendarWidget QToolButton#qt_calendar_nextmonth { qproperty-icon: url(assets/icons/left-arrow.png); width: 24px; height: 24px; icon-size: 12px; border-radius: 12px; } QCalendarWidget QToolButton#qt_calendar_nextmonth { qproperty-icon: url(assets/icons/right-arrow.png); } QCalendarWidget QToolButton { color: black; } """)

        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female", "Other"])
        left_layout.addWidget(QLabel("Pol:"))
        left_layout.addWidget(self.gender_input)
        self.gender_input.setFixedHeight(36)
        self.gender_input.setMinimumWidth(320)
        self.gender_input.setStyleSheet(
            """ QComboBox { padding: 4px; border: 1px solid #ccc; border-radius: 10px; background-color: #ffffff; } QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 24px; border-left: 1px solid #ccc; } QComboBox::down-arrow { image: url(assets/icons/down-arrow.png); width: 12px; height: 12px; } QComboBox QAbstractItemView { border: 1px solid #ccc; border-radius: 8px; background-color: white; selection-background-color: #0C81E4; selection-color: white; } """)
        self.apply_shadow(self.gender_input)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Adresa")
        left_layout.addWidget(QLabel("Adresa:"))
        left_layout.addWidget(self.address_input)
        self.address_input.setFixedHeight(36)
        self.address_input.setMinimumWidth(320)
        self.address_input.setStyleSheet(
            """ QLineEdit { padding: 8px; border: 1px solid #ccc; border-radius: 8px; background-color: #ffffff; } """)
        self.apply_shadow(self.address_input)

        # Dugmad
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Sačuvaj")
        self.apply_shadow(self.save_btn)
        self.cancel_btn = QPushButton("Otkaži")
        self.apply_shadow(self.cancel_btn)

        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #22C55E;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
        """)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #111827;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        left_layout.addLayout(btn_layout)

        # Desna kolona
        right_layout = QVBoxLayout()
        right_layout.setSpacing(3)
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Unesite napomenu...")
        self.note_input.setFixedHeight(350)
        self.note_input.setStyleSheet(
            """ QTextEdit { border: 1px solid #ccc; border-radius: 12px; padding: 8px; background-color: white; } """)
        self.apply_shadow(self.note_input)
        right_layout.addWidget(QLabel("Napomena:"))
        right_layout.addWidget(self.note_input)
        self.note_input.setMinimumHeight(250)

        # Spoji obe kolone
        content_layout.addLayout(left_layout)
        content_layout.addLayout(right_layout)
        main_layout.addLayout(content_layout)

        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.validate_and_accept)

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            warning = WarningDialog(parent=self)
            warning.exec()
            return
        self.accept()

    def get_data(self):
        return {
            "full_name": self.name_input.text(),
            "birthday": self.date_input.date().toString("yyyy-MM-dd"),
            "gender": self.gender_input.currentText(),
            "address": self.address_input.text(),
            "note": self.note_input.toPlainText()
        }

    def create_title_bar(self):
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: #0C81E4;")

        layout = QGridLayout(title_bar)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(0)

        logo = QLabel()
        logo.setPixmap(QPixmap("assets/icons/logo.png").scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(logo, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        title = QLabel("Dodaj pacijenta")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        layout.addWidget(title, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        icon_container = QWidget()
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(4)

        btn_close = QPushButton()
        btn_close.setIcon(QIcon("assets/icons/close.png"))
        btn_close.setFixedSize(24, 24)
        btn_close.setStyleSheet("border: none;")
        btn_close.clicked.connect(self.close)

        icon_layout.addWidget(btn_close)
        layout.addWidget(icon_container, 0, 2, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 1)

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
