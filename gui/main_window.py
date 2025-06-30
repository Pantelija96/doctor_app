import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QLineEdit, QTextEdit, QFrame, QGraphicsDropShadowEffect, QSizePolicy, QGridLayout, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap, QFontDatabase, QFont, QIcon
from database_manager import DatabaseManager

class PatientCard(QFrame):
    def __init__(self, name: str, birth_year: str, selected: bool = False):
        super().__init__()
        self.selected = selected
        self.hovered = False

        self.setObjectName("PatientCard")
        self.setFixedHeight(70)
        self.setStyleSheet("""
            QFrame#PatientCard {
                background-color: white;
                border-radius: 12px;
            }
        """)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)

        # Senka
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(2)

        # Labela imena i godine
        self.name_label = QLabel(name)
        self.name_label.setFont(QFont("Montserrat", 11, QFont.Weight.Medium))
        self.name_label.setStyleSheet("color: #111827;")

        self.year_label = QLabel(f"Godina rođenja: {birth_year}")
        self.year_label.setFont(QFont("Inter", 10))
        self.year_label.setStyleSheet("color: #6B7280;")

        layout.addWidget(self.name_label)
        layout.addWidget(self.year_label)

        self.update_style()

    def enterEvent(self, event):
        self.hovered = True
        self.update_style()

    def leaveEvent(self, event):
        self.hovered = False
        self.update_style()

    def set_selected(self, selected: bool):
        self.selected = selected
        self.update_style()

    def update_style(self):
        if self.hovered:
            bg = "#0C81E4"  # Plava kao title bar
            name_color = "white"
            year_color = "white"
        else:
            bg = "white"
            name_color = "#111827"
            year_color = "#6B7280"

        self.setStyleSheet(f"""
            QFrame#PatientCard {{
                background-color: {bg};
                border-radius: 12px;
                border: none;
            }}
        """)
        self.name_label.setStyleSheet(f"color: {name_color}; background-color: transparent;")
        self.year_label.setStyleSheet(f"color: {year_color}; background-color: transparent;")

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
        self.load_patients()

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
            self.update_patient_info(patient)

    def update_patient_info(self, patient):
        full_name = patient[1] or "-"
        birth_date = patient[2] or "-"
        address = patient[3] or "-"
        gender = patient[4] or "-"
        note = patient[5] or ""

        try:
            if hasattr(birth_date, 'strftime'):
                birth_date_str = birth_date.strftime("%d.%m.%Y.")
            else:
                birth_date_str = birth_date
        except:
            birth_date_str = birth_date

        self.label_name.setText(f"Pacijent: {full_name}")
        self.label_birthday.setText(f"Datum rođenja: {birth_date_str}")
        self.label_address.setText(f"Adresa: {address}")
        self.label_gender.setText(f"Pol: {gender}")
        self.note_edit.setPlainText(note)

        self.history_list.clear()  # zasad prazno

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
        """)
        self.patient_list.setSpacing(8)
        self.patient_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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
