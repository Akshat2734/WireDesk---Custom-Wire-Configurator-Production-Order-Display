from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget,
)

from api_client import ApiError


class OrderCard(QFrame):
    STATUS_OPTIONS = ["preprocessing", "processing", "done"]

    def __init__(self, order, sync_manager):
        super().__init__()
        self.sync_manager = sync_manager
        self.order = order
        self.order_id = order["order_id"]
        self.setObjectName("OrderCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout = QVBoxLayout(self)
        self.header = QPushButton(f"Order #{self.order_id}")
        self.header.clicked.connect(self.toggle_expand)
        layout.addWidget(self.header)
        
        user_role = getattr(self.sync_manager.api_client, 'role', 'view')
        current_status = order.get("status", "preprocessing")

        if user_role == "admin":
            self.status_box = QComboBox()
            self.status_box.addItems(self.STATUS_OPTIONS)
            self.status_box.setCurrentText(current_status)
            self.status_box.currentTextChanged.connect(self.update_status)
            self.status_box.currentTextChanged.connect(self.update_status_style)
            layout.addWidget(self.status_box)
            self.update_status_style(current_status)
        else:
            self.status_label = QLabel(current_status.upper())
            color = {"preprocessing": "#f4d35e", "processing": "#17c3b2", "done": "#28c76f"}.get(current_status, "#ffffff")
            self.status_label.setStyleSheet(
                f"border: 1px solid {color}; border-radius: 6px; padding: 6px; "
                f"color: {color}; background-color: #2a3142; font-weight: bold;"
            )
            self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.status_label)

        self.details_widget = QWidget()
        columns = QHBoxLayout(self.details_widget)
        order_layout = QVBoxLayout()
        analytics_layout = QVBoxLayout()
        order_layout.addWidget(QLabel("Order Details"))
        analytics_layout.addWidget(QLabel("Analytics Details"))
        for key, value in order.items():
            if key not in {"analytics", "id", "user_id"}:
                order_layout.addWidget(QLabel(f"{key.replace('_', ' ').title()}: {value}"))
        for key, value in order.get("analytics", {}).items():
            if key not in {"id", "user_id", "order_id"}:
                analytics_layout.addWidget(QLabel(f"{key.replace('_', ' ').title()}: {value}"))
        columns.addLayout(order_layout)
        columns.addLayout(analytics_layout)
        self.details_widget.setVisible(False)
        layout.addWidget(self.details_widget)

    def toggle_expand(self):
        self.details_widget.setVisible(not self.details_widget.isVisible())

    def update_status(self, status):
        try:
            self.sync_manager.api_client.update_order_status(self.order_id, status)
        except ApiError:
            self.status_box.blockSignals(True)
            self.status_box.setCurrentText(self.order.get("status", "preprocessing"))
            self.status_box.blockSignals(False)

    def update_status_style(self, status):
        color = {
            "preprocessing": "#f4d35e", "processing": "#17c3b2", "done": "#28c76f"
        }.get(status, "#ffffff")
        self.status_box.setStyleSheet(
            f"QComboBox {{ border: 1px solid {color}; border-radius: 6px; "
            f"padding: 4px; color: {color}; background-color: #2a3142; }}"
        )


class OrdersDashboard(QWidget):
    def __init__(self, sync_manager):
        super().__init__()
        self.sync_manager = sync_manager
        self.layout = QVBoxLayout(self)
        self.sync_manager.update_received.connect(self.refresh)
        self.load_orders()

    def load_orders(self):
        try:
            rows = self.sync_manager.api_client.get_orders()
        except ApiError:
            rows = []
        for row in rows:
            if row.get("status") != "done":
                self.layout.addWidget(OrderCard(row, self.sync_manager))
        self.layout.addStretch()

    def refresh(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.load_orders()
