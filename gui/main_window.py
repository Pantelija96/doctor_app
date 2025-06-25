import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QLineEdit, QTextEdit, QFrame, QGraphicsDropShadowEffect, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap, QFontDatabase, QFont, QIcon
from database_manager import DatabaseManager


class MainWindow(QMainWindow):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Doktorska evidencija")
        self.resize(1000, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # Skini sistemski title bar

        # Učitaj font
        font_path = os.path.join("assets", "Inter-VariableFont_opsz,wght.ttf")
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

    def create_title_bar(self):
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: #0C81E4;")

        layout = QGridLayout(title_bar)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(0)

        # === LOGO ===
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/icons/logo.png").scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))
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
        btn_min.setIcon(QIcon("assets/icons/minimize.png"))
        btn_min.setFixedSize(24, 24)
        btn_min.setStyleSheet("border: none;")
        btn_min.clicked.connect(self.showMinimized)

        btn_max = QPushButton()
        btn_max.setIcon(QIcon("assets/icons/maximize.png"))
        btn_max.setFixedSize(24, 24)
        btn_max.setStyleSheet("border: none;")
        btn_max.clicked.connect(self.toggle_maximize_restore)

        btn_close = QPushButton()
        btn_close.setIcon(QIcon("assets/icons/close.png"))
        btn_close.setFixedSize(24, 24)
        btn_close.setStyleSheet("border: none;")
        btn_close.clicked.connect(self.close)

        icon_layout.addWidget(btn_min)
        icon_layout.addWidget(btn_max)
        icon_layout.addWidget(btn_close)

        layout.addWidget(icon_container, 0, 2, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

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

        # === Pretraga ===
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(12, 4, 12, 4)
        search_layout.setSpacing(8)
        search_container.setStyleSheet("background-color: #f3f4f6; border-radius: 18px;")

        icon_label = QLabel()
        icon_label.setFixedSize(16, 16)
        icon_label.setPixmap(QPixmap("assets/icons/search.png").scaled(16, 16))
        icon_label.setStyleSheet("background-color: transparent;")

        search_input = QLineEdit()
        search_input.setPlaceholderText("Pretraži pacijente")
        search_input.setStyleSheet("border: none; background-color: transparent; font-size: 14px;")

        search_layout.addWidget(icon_label)
        search_layout.addWidget(search_input)
        self.apply_shadow(search_container)
        layout.addWidget(search_container)

        # === Lista pacijenata ===
        self.patient_list = QListWidget()
        self.patient_list.setStyleSheet("background-color: white; border-radius: 12px; padding: 6px;")
        self.apply_shadow(self.patient_list)
        layout.addWidget(self.patient_list)

        # === Dodaj pacijenta ===
        add_button = QPushButton("Dodaj pacijenta")
        add_button.setStyleSheet("background-color: #22C55E; color: white; font-weight: bold;")
        self.apply_shadow(add_button)
        layout.addWidget(add_button)

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

        label_name = QLabel("Pacijent: Marko Marković")
        label_name.setStyleSheet("font-weight: bold;")

        label_birthday = QLabel("Datum rođenja: 19.07.1978.")
        label_address = QLabel("Adresa: Bulevar revolucije 1a")
        label_gender = QLabel("Pol: Muški")

        grid.addWidget(label_name, 0, 0)
        grid.addWidget(label_birthday, 1, 0)
        grid.addWidget(label_address, 2, 0)
        grid.addWidget(label_gender, 3, 0)

        info_layout.addLayout(grid)

        # Napomena
        note_label = QLabel("Napomena:")
        note_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        info_layout.addWidget(note_label)

        self.note_edit = QTextEdit()
        self.note_edit.setFixedHeight(200)
        self.note_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        info_layout.addWidget(self.note_edit)

        layout.addWidget(info_frame)

        # === Istorija pregleda ===
        history_frame = QFrame()
        history_layout = QVBoxLayout(history_frame)
        history_layout.setContentsMargins(12, 12, 12, 12)
        history_frame.setStyleSheet("background-color: #ffffff; border-radius: 12px;")
        self.apply_shadow(history_frame)

        history_label = QLabel("Istorija pregleda")
        history_label.setStyleSheet("font-weight: bold;")

        self.history_list = QListWidget()

        history_layout.addWidget(history_label)
        history_layout.addWidget(self.history_list)
        layout.addWidget(history_frame)

        # === Dugmad ===
        button_layout = QHBoxLayout()

        btn_add_report = QPushButton("Dodaj izveštaj")
        btn_add_report.setStyleSheet("background-color: #22C55E; color: white; font-weight: bold;")
        self.apply_shadow(btn_add_report)

        btn_edit = QPushButton("Izmeni")
        btn_edit.setStyleSheet("background-color: white; color: black; font-weight: bold;")
        self.apply_shadow(btn_edit)

        btn_delete = QPushButton("Obriši")
        btn_delete.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold;")
        self.apply_shadow(btn_delete)

        button_layout.addWidget(btn_add_report)
        button_layout.addWidget(btn_edit)
        button_layout.addWidget(btn_delete)

        layout.addLayout(button_layout)
        return panel
