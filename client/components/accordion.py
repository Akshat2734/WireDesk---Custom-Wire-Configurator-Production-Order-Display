from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt


class Accordion(QWidget):
    def __init__(self):
        super().__init__()
        self.sections = []

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(6)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def add_section(self, section):
        self.sections.append(section)
        self.layout.addWidget(section)

    def open_section(self, target):
        for section in self.sections:
            active = section is target
            section.content.setVisible(active)
            section.button.setChecked(active)


class AccordionSection(QWidget):
    def __init__(self, title, content, accordion):
        super().__init__()
        self.accordion = accordion

        self.button = QPushButton(title)
        self.button.setCheckable(True)
        self.button.clicked.connect(lambda: accordion.open_section(self))
        self.button.setStyleSheet("""
            QPushButton {
                text-align:left;
                padding:10px;
                font-weight:600;
                background:#2c2c2c;
            }
            QPushButton:checked {
                background:#3a3a3a;
            }
        """)

        self.content = content
        self.content.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.button)
        layout.addWidget(self.content)
