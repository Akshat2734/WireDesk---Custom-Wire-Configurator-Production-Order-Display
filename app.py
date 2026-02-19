import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea
)
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import Qt
import qdarkstyle

from card_widget import Card
from overlay import Overlay

cards_data = [
    {
        "title": "House Wire / Multistrand Wire",
        "details": "NULL",
        "img": "img/house_wire.jpg",
        "json": "data/house_wire.json"
    },
    {
        "title": "Multi Core Round Cable",
        "details": "NULL",
        "img": "img/multicore_cable.jpg",
        "json": "data/multi_core_round_cable.json"
    },
    {
        "title": "3 Core Flat Submersible Cable",
        "details": "NULL",
        "img": "img/3_core_flat_submersible_cable.jpg",
        "json": "data/3_core_flat_submersible_cable.json"
    },
    {
        "title": "Service Wire",
        "details": "NULL",
        "img": "img/service_wire.jpg",
        "json": "data/service_wire.json"
    },
    {
        "title": "Flexible Twisted Wire",
        "details": "NULL",
        "img": "img/flexible_twisted_wire.jpg",
        "json": "data/flexible_twisted_wire.json"
    },
    {
        "title": "Aluminium Cable and Wire",
        "details": "NULL",
        "img": "img/aluminium_cable_and_wire.jpg",
        "json": "data/aluminium_cable_and_wire.json"
    },
    {
        "title": "Speaker Wire",
        "details": "NULL",
        "img": "img/speaker_wire.jpg",
        "json": "data/speaker_wire.json"
    },
    {
        "title": "Parallel Flat Wire",
        "details": "NULL",
        "img": "img/parallel_flat_wire.jpg",
        "json": "data/parallel_flat_wire.json"
    }
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WireDesk - Custom Wire Configurator & Production Order Display")
        self.setMinimumSize(1000, 700)
        
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.overlay = Overlay(self)
        self.overlay.hide()

        # ---------- Top Bar ----------
        top = QWidget()
        top_layout = QHBoxLayout(top)
        top_layout.addWidget(QLabel("WireDesk - Custom Wire Configurator & Production Order Display"))
        top_layout.addStretch()
        top_layout.addWidget(QLabel("Dashboard"))
        top_layout.addWidget(QLabel("Add"))
        top.setFixedHeight(50)
        top.setStyleSheet("background:#444;color:white;padding:10px;")

        # ----- Right Bar ----- 
        rightBar = QWidget() 
        rightLayout = QVBoxLayout(rightBar) 
        rightLayout.addWidget(QLabel("Hello World")) 
        rightLayout.addStretch() 
        rightBar.setStyleSheet("background:#2e2e2e; color:white;")

        # ---------- Cards ----------
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(20)
        grid.setContentsMargins(0, 0, 0, 0) 

        row = col = 0
        for data in cards_data:
            card = Card(
                data["title"],
                data["details"],
                data["img"],
                data["json"]
            )
            card.clicked.connect(self.openOverlay)
            grid.addWidget(card, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1
            card.setObjectName("card")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(grid_widget)
        
        # ----- Horizontal section (Right+ Left) -----
        contentLayout = QHBoxLayout() 
        contentLayout.addWidget(scroll) 
        contentLayout.addWidget(rightBar) 
        # proportions like % using stretch 
        contentLayout.setStretch(0, 3) # left (bigger)  
        contentLayout.setStretch(1, 1) # right (smaller)

        # ---------- Layout ----------
        content = QVBoxLayout()
        content.addWidget(top)
        content.addLayout(contentLayout)

        container = QWidget()
        container.setLayout(content)
        self.setCentralWidget(container)

    def openOverlay(self, json_file, title):
        self.overlay.loadJson(json_file, title)
        self.overlay.show()
        self.overlay.raise_()

    def resizeEvent(self, event):
        center = QGuiApplication.primaryScreen().geometry().center()
        self.move(center - self.rect().center())
        super().resizeEvent(event)


app = QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet())
window = MainWindow()
window.show()
sys.exit(app.exec())
