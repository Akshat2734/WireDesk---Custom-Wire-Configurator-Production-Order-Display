import sqlite3
import re

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout,
    QComboBox, QFrame, QPushButton
)

from PyQt6.QtCore import Qt

# Import SyncManager
from network_sync import SyncManager


# ======================
# HELPER FUNCTION
# ======================

def format_wire_name(name):
    if not name:
        return ""
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', name)


# ======================
# ORDER CARD
# ======================

class OrderCard(QWidget):

    STATUS_OPTIONS = ["preprocessing", "processing", "done"]

    def __init__(self, order_data, sync_manager):

        super().__init__()

        self.order_id = order_data["order_id"]
        self.wire_type = order_data["wire_type"]
        self.length = order_data["length_meters"]
        self.total_cost = order_data["total_cost"]
        self.status = order_data["status"]

        self.sync_manager = sync_manager

        self.expanded = False

        main_layout = QVBoxLayout(self)

        self.frame = QFrame()

        self.frame.setStyleSheet("""
            QFrame {
                background:#3a3a3a;
                border-radius:8px;
                padding:10px;
            }
        """)

        frame_layout = QVBoxLayout(self.frame)

        # Header
        self.header_btn = QPushButton(f"Order ID: {self.order_id}")

        self.header_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.header_btn.setStyleSheet("""
            QPushButton {
                text-align:left;
                font-weight:bold;
                font-size:15px;
                border:none;
                color:white;
            }

            QPushButton:hover {
                color:#4da3ff;
            }
        """)

        self.header_btn.clicked.connect(self.toggle_expand)

        frame_layout.addWidget(self.header_btn)

        # Status dropdown
        self.status_box = QComboBox()

        self.status_box.addItems(self.STATUS_OPTIONS)

        self.status_box.setCurrentText(self.status)

        self.status_box.currentTextChanged.connect(self.update_status)

        frame_layout.addWidget(self.status_box)

        # Details
        self.details_widget = QWidget()

        details_layout = QVBoxLayout(self.details_widget)

        details_layout.addWidget(QLabel(
            f"Wire Name: {format_wire_name(self.wire_type)}"
        ))

        details_layout.addWidget(QLabel(
            f"Length: {self.length} meters"
        ))

        details_layout.addWidget(QLabel(
            f"Total Cost: ₹{self.total_cost}"
        ))

        self.details_widget.setVisible(False)

        frame_layout.addWidget(self.details_widget)

        main_layout.addWidget(self.frame)


    def toggle_expand(self):

        self.expanded = not self.expanded

        self.details_widget.setVisible(self.expanded)


    def update_status(self, new_status):

        try:

            # Update analytics DB
            conn = sqlite3.connect("db/analytics.db")

            conn.execute(
                "UPDATE analytics SET status=? WHERE order_id=?",
                (new_status, self.order_id)
            )

            conn.commit()
            conn.close()


            # Update orders DB
            conn = sqlite3.connect("db/orders.db")

            conn.execute(
                "UPDATE orders SET status=? WHERE order_id=?",
                (new_status, self.order_id)
            )

            conn.commit()
            conn.close()


            # Broadcast to all apps
            self.sync_manager.broadcast()

        except Exception as e:

            print("Status update error:", e)


# ======================
# DASHBOARD
# ======================

class OrdersDashboard(QWidget):

    def __init__(self):

        super().__init__()

        self.layout = QVBoxLayout(self)

        # Initialize sync manager
        self.sync_manager = SyncManager()

        # Listen for network updates
        self.sync_manager.update_received.connect(self.refresh)

        self.load_orders()


    def load_orders(self):

        conn = sqlite3.connect("db/analytics.db")

        cur = conn.cursor()

        cur.execute("""
            SELECT order_id,
                   wire_type,
                   length_meters,
                   total_cost,
                   status
            FROM analytics
            WHERE status != 'done'
            ORDER BY order_id DESC
        """)

        rows = cur.fetchall()

        conn.close()


        for row in rows:

            order_data = {

                "order_id": row[0],
                "wire_type": row[1],
                "length_meters": row[2],
                "total_cost": row[3],
                "status": row[4]

            }

            card = OrderCard(
                order_data,
                self.sync_manager
            )

            self.layout.addWidget(card)

        self.layout.addStretch()


    def refresh(self):

        while self.layout.count():

            item = self.layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

        self.load_orders()