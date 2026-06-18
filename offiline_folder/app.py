import sys
import sqlite3

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QPushButton,
    QSizePolicy, QFrame, QComboBox
)
from PyQt6.QtCore import Qt

from old_py_files.card_widget import Card
from old_py_files.overlay import Overlay
from old_py_files.ordersdashboard import OrdersDashboard
from old_py_files.dashboard_window import DashboardWindow
from old_py_files.styles import GLOBAL_STYLE, PRIMARY_COLOR
from old_py_files.network_sync import SyncManager


cards_data = [
    {"title": "House Wire / Multistrand Wire", "details": "NULL", "img": "img/house_wire.jpg", "json": "data/house_wire.json"},
    {"title": "Multi Core Round Cable", "details": "NULL", "img": "img/multicore_cable.jpg", "json": "data/multi_core_round_cable.json"},
    {"title": "3 Core Flat Submersible Cable", "details": "NULL", "img": "img/3_core_flat_submersible_cable.jpg", "json": "data/3_core_flat_submersible_cable.json"},
    {"title": "Service Wire", "details": "NULL", "img": "img/service_wire.jpg", "json": "data/service_wire.json"},
    {"title": "Flexible Twisted Wire", "details": "NULL", "img": "img/flexible_twisted_wire.jpg", "json": "data/flexible_twisted_wire.json"},
    {"title": "Aluminium Cable and Wire", "details": "NULL", "img": "img/aluminium_cable_and_wire.jpg", "json": "data/aluminium_cable_and_wire.json"},
    {"title": "Speaker Wire", "details": "NULL", "img": "img/speaker_wire.jpg", "json": "data/speaker_wire.json"},
    {"title": "Parallel Flat Wire", "details": "NULL", "img": "img/parallel_flat_wire.jpg", "json": "data/parallel_flat_wire.json"}
]


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Sync manager
        self.sync_manager = SyncManager()
        self.sync_manager.update_received.connect(self.load_compact_orders)

        # Full dashboard window
        self.dashboard_window = DashboardWindow(self.sync_manager)

        self.setWindowTitle("WireDesk - Production Management")
        self.setMinimumSize(1200, 750)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Overlay
        self.overlay = Overlay(self)
        self.overlay.hide()
        self.overlay.order_added.connect(self.load_compact_orders)

        # ---------- TOP BAR ----------
        top = QWidget()
        top.setFixedHeight(65)

        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(25, 0, 25, 0)

        brand_label = QLabel("WIREDESK")
        brand_label.setStyleSheet(
            f"color: {PRIMARY_COLOR}; font-size: 20px; font-weight: 800;"
        )
        top_layout.addWidget(brand_label)
        top_layout.addStretch()

        self.dash_btn = QPushButton("View Dashboard")
        self.sync_btn = QPushButton("Sync Network")

        for btn in [self.dash_btn, self.sync_btn]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedWidth(140)

        self.dash_btn.clicked.connect(self.open_dashboard)
        self.sync_btn.clicked.connect(self.ping_update)

        top_layout.addWidget(self.dash_btn)
        top_layout.addSpacing(10)
        top_layout.addWidget(self.sync_btn)

        # ---------- RIGHT SIDEBAR ----------
        rightBar = QWidget()
        rightBar.setFixedWidth(380)

        rightLayout = QVBoxLayout(rightBar)
        rightLayout.setContentsMargins(8, 20, 8, 20)
        rightLayout.setSpacing(12)

        summary_title = QLabel("Live Orders")
        summary_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        rightLayout.addWidget(summary_title)

        self.compact_scroll = QScrollArea()
        self.compact_scroll.setWidgetResizable(True)

        self.compact_container = QWidget()
        self.compact_layout = QVBoxLayout(self.compact_container)
        self.compact_layout.setSpacing(10)

        self.compact_scroll.setWidget(self.compact_container)
        rightLayout.addWidget(self.compact_scroll)

        self.load_compact_orders()

        # ---------- PRODUCT GRID ----------
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(25)
        grid.setContentsMargins(30, 30, 30, 30)

        row = col = 0
        for data in cards_data:
            card = Card(data["title"], data["details"], data["img"], data["json"])
            card.clicked.connect(self.openOverlay)
            grid.addWidget(card, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(grid_widget)
        scroll.setStyleSheet("border: none; background-color: transparent;")

        contentLayout = QHBoxLayout()
        contentLayout.setSpacing(0)
        contentLayout.addWidget(scroll, stretch=3)
        contentLayout.addWidget(rightBar, stretch=1)

        main_content = QVBoxLayout()
        main_content.setContentsMargins(0, 0, 0, 0)
        main_content.setSpacing(0)
        main_content.addWidget(top)
        main_content.addLayout(contentLayout)

        container = QWidget()
        container.setLayout(main_content)
        self.setCentralWidget(container)

    # ---------- FUNCTIONS ----------

    def openOverlay(self, json_file, title):
        self.overlay.loadJson(json_file, title)
        self.overlay.show()
        self.overlay.raise_()

    def open_dashboard(self):
        self.dashboard_window.show()
        self.dashboard_window.raise_()

    def ping_update(self):
        self.sync_manager.broadcast()

    def load_compact_orders(self):

        while self.compact_layout.count():
            item = self.compact_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        conn = sqlite3.connect("db/analytics.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT order_id, wire_type, length_meters, total_cost, status
            FROM analytics
            WHERE status != 'done'
            ORDER BY order_id DESC
        """)

        rows = cur.fetchall()
        conn.close()

        for row in rows:
            analytics_data = {
                "order_id": row[0],
                "wire_type": row[1],
                "length_meters": row[2],
                "total_cost": row[3],
                "status": row[4]
            }

            card = CompactOrderCard(analytics_data, self.sync_manager)
            self.compact_layout.addWidget(card)

        self.compact_layout.addStretch()


# ---------- COMPACT CARD ----------

class CompactOrderCard(QFrame):

    STATUS_OPTIONS = ["preprocessing", "processing", "done"]

    def __init__(self, analytics_data, sync_manager):
        super().__init__()

        self.sync_manager = sync_manager
        self.order_id = analytics_data["order_id"]

        self.setObjectName("OrderCard")

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        self.header = QPushButton(f"Order #{self.order_id}")
        self.header.setObjectName("OrderHeader")
        self.header.clicked.connect(self.toggle_expand)
        layout.addWidget(self.header)

        self.status_box = QComboBox()
        self.status_box.addItems(self.STATUS_OPTIONS)
        self.status_box.setCurrentText(analytics_data.get("status"))
        self.status_box.currentTextChanged.connect(self.update_status)
        self.status_box.currentTextChanged.connect(self.update_status_style)
        layout.addWidget(self.status_box)

        self.details = QWidget()
        details_layout = QVBoxLayout(self.details)
        self.update_status_style(self.status_box.currentText())

        details_layout.addWidget(QLabel(f"Wire Type: {analytics_data['wire_type']}"))
        details_layout.addWidget(QLabel(f"Length: {analytics_data['length_meters']} m"))
        details_layout.addWidget(QLabel(f"Total Cost: ₹ {analytics_data['total_cost']}"))

        self.details.setVisible(False)
        layout.addWidget(self.details)

    def toggle_expand(self):
        self.details.setVisible(not self.details.isVisible())

    def update_status(self, new_status):

        conn = sqlite3.connect("db/analytics.db")
        conn.execute("UPDATE analytics SET status=? WHERE order_id=?",
                    (new_status, self.order_id))
        conn.commit()
        conn.close()

        conn = sqlite3.connect("db/orders.db")
        conn.execute("UPDATE orders SET status=? WHERE order_id=?",
                    (new_status, self.order_id))
        conn.commit()
        conn.close()

        self.sync_manager.broadcast()
        
    def update_status_style(self, status):
        styles = {
            "preprocessing": "#f4d35e",
            "processing": "#17c3b2",
            "done": "#28c76f"
        }

        color = styles.get(status, "#ffffff")

        self.status_box.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {color};
                border-radius: 6px;
                padding: 4px;
                color: {color};
                background-color: #2a3142;
            }}
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())