import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget,
    QScrollArea
)
from ordersdashboard import OrderCard


class OrdersTab(QWidget):

    def __init__(self, status_filter, sync_manager):
        super().__init__()

        self.status_filter = status_filter
        self.sync_manager = sync_manager

        layout = QVBoxLayout(self)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)

        self.container = QWidget()
        self.cards_layout = QVBoxLayout(self.container)
        self.scroll.setWidget(self.container)

        self.load_orders()

    def load_orders(self):

        conn = sqlite3.connect("db/analytics.db")
        cur = conn.cursor()

        if self.status_filter:
            cur.execute("""
                SELECT *
                FROM analytics
                WHERE status=?
                ORDER BY order_id DESC
            """, (self.status_filter,))
        else:
            cur.execute("""
                SELECT *
                FROM analytics
                ORDER BY order_id DESC
            """)

        rows = cur.fetchall()
        columns = [c[0] for c in cur.description]
        conn.close()

        for row in rows:
            data = dict(zip(columns, row))
            card = OrderCard(data, self.sync_manager)
            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch()

    def refresh(self):

        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.load_orders()


class DashboardWindow(QWidget):

    def __init__(self, sync_manager):
        super().__init__()

        self.setWindowTitle("Production Orders Dashboard")
        self.resize(1000, 700)

        self.sync_manager = sync_manager
        self.sync_manager.update_received.connect(self.refresh)

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        self.all_tab = OrdersTab(None, sync_manager)
        self.preprocessing_tab = OrdersTab("preprocessing", sync_manager)
        self.processing_tab = OrdersTab("processing", sync_manager)
        self.done_tab = OrdersTab("done", sync_manager)

        self.tabs.addTab(self.all_tab, "All")
        self.tabs.addTab(self.preprocessing_tab, "Preprocessing")
        self.tabs.addTab(self.processing_tab, "Processing")
        self.tabs.addTab(self.done_tab, "Done")

        layout.addWidget(self.tabs)

    def refresh(self):
        self.all_tab.refresh()
        self.preprocessing_tab.refresh()
        self.processing_tab.refresh()
        self.done_tab.refresh()