import sqlite3
import re

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QFrame,
    QPushButton
)

from PyQt6.QtCore import Qt


# ======================
# HELPER FUNCTION
# Adds space before capitals
# Example: FlatSubmersibleCable → Flat Submersible Cable
# ======================

def format_wire_name(name):

    if not name:
        return ""

    return re.sub(r'(?<!^)(?=[A-Z])', ' ', name)


# ======================
# ORDER CARD WIDGET
# ======================

class OrderCard(QWidget):

    STATUS_OPTIONS = ["preprocessing", "processing", "done"]

    def __init__(self, order_data, refresh_callback):

        super().__init__()

        self.order_id = order_data["order_id"]
        self.wire_type = order_data["wire_type"]
        self.length = order_data["length_meters"]
        self.total_cost = order_data["total_cost"]
        self.status = order_data["status"]

        self.refresh_callback = refresh_callback

        self.expanded = False

        main_layout = QVBoxLayout(self)

        self.frame = QFrame()

        self.frame.setStyleSheet("""
            QFrame {
                background:#3a3a3a;
                border-radius:8px;
                padding:8px;
            }
        """)

        frame_layout = QVBoxLayout(self.frame)

        # ======================
        # ORDER ID BUTTON
        # ======================

        self.header_btn = QPushButton(f"Order ID: {self.order_id}")

        self.header_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # HOVER EFFECT → BLUE
        self.header_btn.setStyleSheet("""
            QPushButton {
                text-align:left;
                font-weight:bold;
                font-size:14px;
                border:none;
                color:white;
            }

            QPushButton:hover {
                color:#4da3ff;
            }
        """)

        self.header_btn.clicked.connect(self.toggle_expand)

        frame_layout.addWidget(self.header_btn)

        # ======================
        # STATUS DROPDOWN
        # ======================

        self.status_box = QComboBox()

        self.status_box.addItems(self.STATUS_OPTIONS)

        self.status_box.setCurrentText(self.status)

        self.status_box.currentTextChanged.connect(self.update_status)

        frame_layout.addWidget(self.status_box)

        # ======================
        # DETAILS DROPDOWN
        # ======================

        self.details_widget = QWidget()

        details_layout = QVBoxLayout(self.details_widget)

        wire_name = format_wire_name(self.wire_type)

        details_layout.addWidget(QLabel(f"Wire Name: {wire_name}"))

        details_layout.addWidget(QLabel(f"Length: {self.length} meters"))

        details_layout.addWidget(QLabel(f"Total Cost: ₹{self.total_cost}"))

        self.details_widget.setVisible(False)

        frame_layout.addWidget(self.details_widget)

        main_layout.addWidget(self.frame)

    # ======================
    # TOGGLE DROPDOWN
    # ======================

    def toggle_expand(self):

        self.expanded = not self.expanded

        self.details_widget.setVisible(self.expanded)

    # ======================
    # UPDATE STATUS
    # ======================

    def update_status(self, new_status):

        try:
            conn_a = sqlite3.connect("db/analytics.db")
            cur_a = conn_a.cursor()

            cur_a.execute("""
                UPDATE analytics
                SET status = ?
                WHERE order_id = ?
            """, (new_status, self.order_id))

            conn_a.commit()
            conn_a.close()


            conn_o = sqlite3.connect("db/orders.db")
            cur_o = conn_o.cursor()

            cur_o.execute("""
                UPDATE orders
                SET status = ?
                WHERE order_id = ?
            """, (new_status, self.order_id))

            conn_o.commit()
            conn_o.close()

            self.refresh_callback()

        except Exception as e:
            print("Error updating status:", e)



# ======================
# DASHBOARD
# ======================

class OrdersDashboard(QWidget):

    def __init__(self):

        super().__init__()

        self.layout = QVBoxLayout(self)

        self.load_orders()

    # ======================
    # LOAD ORDERS
    # ======================

    def load_orders(self):

        conn = sqlite3.connect("db/analytics.db")

        cur = conn.cursor()

        # IMPORTANT → get required fields
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

            card = OrderCard(order_data, self.refresh)

            self.layout.addWidget(card)

        self.layout.addStretch()

    # ======================
    # REFRESH DASHBOARD
    # ======================

    def refresh(self):

        while self.layout.count():

            item = self.layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

        self.load_orders()
