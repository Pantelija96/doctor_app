from PyQt6.QtCore import Qt, QDate, QSize, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QPushButton, QHBoxLayout, QTextEdit, QLabel, QDateEdit, \
    QVBoxLayout, QDialog, QWidget, QLineEdit, QListWidget, QAbstractItemView, QSizePolicy
import os
from database_manager import DatabaseManager

class WarningDialog(QDialog):
    def __init__(self, message="Greška!", parent=None):
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
    def __init__(self, message="Uspešno ste odštampali dan.", parent=None):
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

class DayReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("DayReportDialog initialized")  # Debug
        self.setWindowTitle("Pregled dana")
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

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.create_title_bar())

        # Centralni deo (biće proširen kasnije)
        content_layout = QVBoxLayout()
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(16)

        # === Izbor datuma pregleda ===
        date_layout = QHBoxLayout()
        date_container = QWidget()
        date_container.setLayout(date_layout)
        date_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        date_label = QLabel("Odaberi datum pregleda:")
        date_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #111827;")

        self.date_input = QDateEdit()
        self.date_input.setDisplayFormat("dd.MM.yyyy.")
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setFixedHeight(36)
        self.date_input.setMinimumWidth(250)

        self.apply_shadow(self.date_input)

        self.date_input.setStyleSheet("""
            QDateEdit {
                border: 1px solid #ccc;
                background-color: white;
                padding: 6px;
                border-radius: 10px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid #ccc;
            }
            QDateEdit::down-arrow {
                image: url(assets/icons/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)

        calendar = self.date_input.calendarWidget()
        calendar.setStyleSheet("""
            QCalendarWidget QToolButton#qt_calendar_prevmonth,
            QCalendarWidget QToolButton#qt_calendar_nextmonth {
                qproperty-icon: url(assets/icons/left-arrow.png);
                width: 24px;
                height: 24px;
                icon-size: 12px;
                border-radius: 12px;
            }
            QCalendarWidget QToolButton#qt_calendar_nextmonth {
                qproperty-icon: url(assets/icons/right-arrow.png);
            }
            QCalendarWidget QToolButton {
                color: black;
            }
        """)

        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        content_layout.addWidget(date_container)

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

        # Dodaj u content layout
        content_layout.addWidget(self.patient_list)

        main_layout.addWidget(content_widget, stretch=1)  # <- srednji deo će se širiti

        # Donja dugmad
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(24, 16, 24, 24)
        btn_layout.setSpacing(16)

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

        btn_layout.addWidget(self.print_btn)
        btn_layout.addWidget(self.cancel_btn)

        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)
        main_layout.addWidget(btn_widget)

    def create_title_bar(self):
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: #0C81E4;"
                                "border-top-left-radius: 12px;"
                                "border-top-right-radius: 12px;")
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(10, 0, 10, 0)

        logo = QLabel()
        logo_path = "assets/icons/logo.png"
        logo.setPixmap(QPixmap(logo_path if os.path.exists(logo_path) else "").scaled(36, 36))
        layout.addWidget(logo)

        title = QLabel("Pretraga po danima")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        close_btn = QPushButton()
        close_icon_path = "assets/icons/close.png"
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