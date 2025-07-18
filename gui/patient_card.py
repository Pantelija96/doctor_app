from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QVBoxLayout, QLabel


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
        self.setContentsMargins(0, 6, 0, 6)  # Gornji i donji razmak

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
        if self.selected or self.hovered:
            bg = "#0C81E4"  # Plava kao za hover
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