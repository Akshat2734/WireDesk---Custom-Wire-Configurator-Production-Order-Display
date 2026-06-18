import sqlite3
import re

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout,
    QComboBox, QFrame, QPushButton, QSizePolicy, QHBoxLayout
)
from PyQt6.QtCore import Qt


def format_wire_name(name):
    if not name:
        return ""
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', name)


class OrderCard(QFrame):

    STATUS_OPTIONS = ["preprocessing", "processing", "done"]

    def __init__(self, analytics_data, sync_manager):
        super().__init__()

        self.sync_manager = sync_manager
        self.analytics_data = analytics_data
        self.order_id = analytics_data["order_id"]

        self.setObjectName("OrderCard")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # ================= HEADER =================
        self.header = QPushButton(f"Order #{self.order_id}")
        self.header.setObjectName("OrderHeader")
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header.setMinimumHeight(34)
        self.header.clicked.connect(self.toggle_expand)

        main_layout.addWidget(self.header)

        # ================= STATUS =================
        self.status_box = QComboBox()
        self.status_box.addItems(self.STATUS_OPTIONS)
        self.status_box.setCurrentText(
            analytics_data.get("status", "preprocessing")
        )

        self.status_box.currentTextChanged.connect(self.update_status)
        self.status_box.currentTextChanged.connect(self.update_status_style)

        main_layout.addWidget(self.status_box)

        self.update_status_style(self.status_box.currentText())

        # ================= DETAILS =================
        self.details_widget = QWidget()
        details_layout = QHBoxLayout(self.details_widget)
        details_layout.setSpacing(20)

        left_column = QVBoxLayout()
        right_column = QVBoxLayout()

        order_data = self.fetch_order_db()

        analytics_unique = {
            k: v for k, v in analytics_data.items()
            if k not in order_data
        }

        # ----- LEFT : ORDER DB -----
        left_title = QLabel("Order Details")
        left_title.setStyleSheet("font-weight:600; font-size:14px;")
        left_column.addWidget(left_title)

        for key, value in order_data.items():
            label = QLabel(
                f"{key.replace('_',' ').title()}: {value}"
            )
            label.setWordWrap(True)
            left_column.addWidget(label)

        left_column.addStretch()

        # ----- RIGHT : ANALYTICS DB -----
        right_title = QLabel("Analytics Details")
        right_title.setStyleSheet("font-weight:600; font-size:14px;")
        right_column.addWidget(right_title)

        for key, value in analytics_unique.items():
            label = QLabel(
                f"{key.replace('_',' ').title()}: {value}"
            )
            label.setWordWrap(True)
            right_column.addWidget(label)

        right_column.addStretch()

        details_layout.addLayout(left_column, 1)
        details_layout.addLayout(right_column, 1)

        self.details_widget.setVisible(False)
        main_layout.addWidget(self.details_widget)

    # ================= FETCH ORDER DB =================

    def fetch_order_db(self):

        conn = sqlite3.connect("db/orders.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM orders
            WHERE order_id=?
        """, (self.order_id,))

        row = cur.fetchone()
        columns = [col[0] for col in cur.description]
        conn.close()

        if row:
            return dict(zip(columns, row))

        return {}

    # ================= TOGGLE =================

    def toggle_expand(self):

        self.details_widget.setVisible(
            not self.details_widget.isVisible()
        )

        self.adjustSize()

    # ================= STATUS UPDATE =================

    def update_status(self, new_status):

        conn = sqlite3.connect("db/analytics.db")
        conn.execute(
            "UPDATE analytics SET status=? WHERE order_id=?",
            (new_status, self.order_id)
        )
        conn.commit()
        conn.close()

        conn = sqlite3.connect("db/orders.db")
        conn.execute(
            "UPDATE orders SET status=? WHERE order_id=?",
            (new_status, self.order_id)
        )
        conn.commit()
        conn.close()

        self.sync_manager.broadcast()

    # ================= STATUS COLOR =================

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

class OrdersDashboard(QWidget):

    def __init__(self, sync_manager):
        super().__init__()
        self.layout = QVBoxLayout(self)
        # Initialize sync manager
        self.sync_manager = sync_manager
        # Listen for network updates
        self.sync_manager.update_received.connect(self.refresh)
        #self.sync_manager.update_received.connect(self.load_compact_orders)
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
