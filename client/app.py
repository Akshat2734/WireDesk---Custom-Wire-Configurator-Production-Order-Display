import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QMainWindow, QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from api_client import ApiClient, ApiError
from auth_dialog import AuthDialog
from components.card_widget import Card
from components.dashboard_window import DashboardWindow
from components.overlay import Overlay
from network_sync import SyncManager
from styles import GLOBAL_STYLE, PRIMARY_COLOR


CLIENT_DIR = Path(__file__).resolve().parent
PRODUCT_DIR = CLIENT_DIR / "data"
CARDS = [
    ("House Wire / Multistrand Wire", "house_wire.jpg", "house_wire.json"),
    ("Multi Core Round Cable", "multicore_cable.jpg", "multi_core_round_cable.json"),
    ("3 Core Flat Submersible Cable", "3_core_flat_submersible_cable.jpg", "3_core_flat_submersible_cable.json"),
    ("Service Wire", "service_wire.jpg", "service_wire.json"),
    ("Flexible Twisted Wire", "flexible_twisted_wire.jpg", "flexible_twisted_wire.json"),
    ("Aluminium Cable and Wire", "aluminium_cable_and_wire.jpg", "aluminium_cable_and_wire.json"),
    ("Speaker Wire", "speaker_wire.jpg", "speaker_wire.json"),
    ("Parallel Flat Wire", "parallel_flat_wire.jpg", "parallel_flat_wire.json"),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_client = ApiClient()
        self.sync_manager = SyncManager(self.api_client)
        self.sync_manager.update_received.connect(self.load_compact_orders)
        self.dashboard_window = DashboardWindow(self.sync_manager)
        self.overlay = Overlay(self.api_client, self)
        self.overlay.hide()
        self.overlay.order_added.connect(self.load_compact_orders)

        self.setWindowTitle("WireDesk - Production Management")
        self.setMinimumSize(1200, 750)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        top = QWidget()
        top.setFixedHeight(65)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(25, 0, 25, 0)
        brand = QLabel("WIREDESK")
        brand.setStyleSheet(f"color:{PRIMARY_COLOR};font-size:20px;font-weight:800;")
        top_layout.addWidget(brand)
        top_layout.addStretch()
        self.sign_in_btn = QPushButton("Sign In")
        dashboard_btn = QPushButton("View Dashboard")
        sync_btn = QPushButton("Sync Network")
        self.sign_in_btn.clicked.connect(self.open_login)
        dashboard_btn.clicked.connect(self.dashboard_window.show)
        sync_btn.clicked.connect(self.sync_manager.broadcast)
        for button in (self.sign_in_btn, dashboard_btn, sync_btn):
            top_layout.addWidget(button)

        right_bar = QWidget()
        right_bar.setFixedWidth(380)
        right_layout = QVBoxLayout(right_bar)
        right_layout.addWidget(QLabel("Live Orders"))
        self.compact_scroll = QScrollArea()
        self.compact_scroll.setWidgetResizable(True)
        self.compact_container = QWidget()
        self.compact_layout = QVBoxLayout(self.compact_container)
        self.compact_scroll.setWidget(self.compact_container)
        right_layout.addWidget(self.compact_scroll)

        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(25)
        for index, (title, image, definition) in enumerate(CARDS):
            card = Card(
                title, "", str(CLIENT_DIR / "assets" / image),
                str(PRODUCT_DIR / definition),
            )
            card.clicked.connect(self.open_overlay)
            grid.addWidget(card, index // 3, index % 3)
        product_scroll = QScrollArea()
        product_scroll.setWidgetResizable(True)
        product_scroll.setWidget(grid_widget)

        content = QHBoxLayout()
        content.addWidget(product_scroll, 3)
        content.addWidget(right_bar, 1)
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(top)
        root.addLayout(content)
        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)
        self.load_compact_orders()

    def open_login(self):
        if AuthDialog(self.api_client, self).exec():
            self.sign_in_btn.setText("Signed In")
            self.sync_manager.connect_to_server()

    def open_overlay(self, json_file, title):
        if not self.api_client.token:
            self.open_login()
        if not self.api_client.token:
            return
        self.overlay.loadJson(json_file, title)
        self.overlay.show()
        self.overlay.raise_()

    def load_compact_orders(self):
        while self.compact_layout.count():
            item = self.compact_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        try:
            orders = self.api_client.get_orders()
        except ApiError:
            orders = []
        for order in orders:
            if order.get("status") != "done":
                self.compact_layout.addWidget(CompactOrderCard(order, self.sync_manager))
        self.compact_layout.addStretch()

    def closeEvent(self, event):
        self.sync_manager.close()
        super().closeEvent(event)


class CompactOrderCard(QFrame):
    STATUS_OPTIONS = ["preprocessing", "processing", "done"]

    def __init__(self, order, sync_manager):
        super().__init__()
        self.order = order
        self.sync_manager = sync_manager
        self.order_id = order["order_id"]
        layout = QVBoxLayout(self)
        self.header = QPushButton(f"Order #{self.order_id}")
        layout.addWidget(self.header)
        self.status_box = QComboBox()
        self.status_box.addItems(self.STATUS_OPTIONS)
        self.status_box.setCurrentText(order.get("status", "preprocessing"))
        self.status_box.currentTextChanged.connect(self.update_status)
        layout.addWidget(self.status_box)
        analytics = order.get("analytics", {})
        self.details = QLabel(
            f"Wire: {order.get('wire_type')}\nLength: {order.get('length_meters')} m\n"
            f"Total cost: INR {analytics.get('total_cost')}"
        )
        self.details.setVisible(False)
        self.header.clicked.connect(
            lambda: self.details.setVisible(not self.details.isVisible())
        )
        layout.addWidget(self.details)

    def update_status(self, status):
        try:
            self.sync_manager.api_client.update_order_status(self.order_id, status)
        except ApiError as exc:
            QMessageBox.warning(self, "Status Not Updated", str(exc))
            self.status_box.blockSignals(True)
            self.status_box.setCurrentText(self.order.get("status", "preprocessing"))
            self.status_box.blockSignals(False)


if __name__ == "__main__":
    application = QApplication(sys.argv)
    application.setStyleSheet(GLOBAL_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(application.exec())
