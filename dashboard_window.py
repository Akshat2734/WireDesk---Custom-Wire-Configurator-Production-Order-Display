import sqlite3

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QTabWidget,
    QScrollArea,
    QComboBox,
    QSizePolicy,
    QHBoxLayout
)

from PyQt6.QtCore import Qt


# ============================================
# ORDER CARD
# ============================================

class OrderCard(QFrame):

    STATUS_OPTIONS = ["preprocessing", "processing", "done"]

    def __init__(self, analytics_data, refresh_callback):

        super().__init__()

        self.analytics_data = analytics_data
        self.order_id = analytics_data["order_id"]

        self.refresh_callback = refresh_callback

        self.setObjectName("OrderCard")

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        main_layout = QVBoxLayout(self)

        # ====================================
        # HEADER BUTTON
        # ====================================

        self.header = QPushButton(f"Order #{self.order_id}")

        self.header.setObjectName("OrderHeader")

        self.header.setCursor(Qt.CursorShape.PointingHandCursor)

        self.header.clicked.connect(self.toggle_expand)

        main_layout.addWidget(self.header)

        # ====================================
        # STATUS DROPDOWN
        # ====================================

        self.status_box = QComboBox()

        self.status_box.addItems(self.STATUS_OPTIONS)

        self.status_box.setCurrentText(
            analytics_data.get("status", "preprocessing")
        )

        self.status_box.currentTextChanged.connect(
            self.update_status
        )

        main_layout.addWidget(self.status_box)

        # ====================================
        # DETAILS AREA (2 COLUMN)
        # ====================================

        self.details_widget = QWidget()

        details_layout = QHBoxLayout(self.details_widget)

        # LEFT COLUMN → orders.db
        left_column = QVBoxLayout()

        # RIGHT COLUMN → analytics.db
        right_column = QVBoxLayout()

        order_data = self.fetch_order_db()

        # remove duplicate keys
        analytics_unique = {
            k: v for k, v in analytics_data.items()
            if k not in order_data
        }

        # LEFT SIDE
        left_column.addWidget(QLabel("<b>Order Info</b>"))

        for key, value in order_data.items():

            label = QLabel(
                f"{key.replace('_',' ').title()}: {value}"
            )

            label.setWordWrap(True)

            left_column.addWidget(label)

        # RIGHT SIDE
        right_column.addWidget(QLabel("<b>Analytics Info</b>"))

        for key, value in analytics_unique.items():

            label = QLabel(
                f"{key.replace('_',' ').title()}: {value}"
            )

            label.setWordWrap(True)

            right_column.addWidget(label)

        details_layout.addLayout(left_column)
        details_layout.addLayout(right_column)

        self.details_widget.setVisible(False)

        main_layout.addWidget(self.details_widget)

    # ====================================
    # FETCH ORDER DB DATA
    # ====================================

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

    # ====================================
    # TOGGLE DETAILS
    # ====================================

    def toggle_expand(self):

        visible = self.details_widget.isVisible()

        self.details_widget.setVisible(not visible)

        self.adjustSize()

        self.updateGeometry()

    # ====================================
    # UPDATE STATUS BOTH DATABASES
    # ====================================

    def update_status(self, new_status):

        try:

            # analytics.db
            conn_a = sqlite3.connect("db/analytics.db")
            cur_a = conn_a.cursor()

            cur_a.execute("""
                UPDATE analytics
                SET status=?
                WHERE order_id=?
            """, (new_status, self.order_id))

            conn_a.commit()
            conn_a.close()

            # orders.db
            conn_o = sqlite3.connect("db/orders.db")
            cur_o = conn_o.cursor()

            cur_o.execute("""
                UPDATE orders
                SET status=?
                WHERE order_id=?
            """, (new_status, self.order_id))

            conn_o.commit()
            conn_o.close()

            self.refresh_callback()

        except Exception as e:

            print("Status update error:", e)


# ============================================
# TAB WITH SCROLL
# ============================================

class OrdersTab(QWidget):

    def __init__(self, status_filter=None):

        super().__init__()

        self.status_filter = status_filter

        main_layout = QVBoxLayout(self)

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(True)

        main_layout.addWidget(self.scroll)

        self.container = QWidget()

        self.container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        self.cards_layout = QVBoxLayout(self.container)

        self.cards_layout.setSpacing(12)

        self.cards_layout.setSizeConstraint(
            QVBoxLayout.SizeConstraint.SetMinAndMaxSize
        )

        self.scroll.setWidget(self.container)

        self.load_orders()

    # ====================================
    # LOAD ORDERS
    # ====================================

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

        columns = [col[0] for col in cur.description]

        conn.close()

        for row in rows:

            analytics_data = dict(zip(columns, row))

            card = OrderCard(
                analytics_data,
                self.refresh
            )

            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch()

        self.container.adjustSize()

    # ====================================
    # REFRESH TAB
    # ====================================

    def refresh(self):

        while self.cards_layout.count():

            item = self.cards_layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

        self.load_orders()


# ============================================
# MAIN DASHBOARD WINDOW
# ============================================

class DashboardWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Production Orders Dashboard"
        )

        self.resize(1000, 700)

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        self.all_tab = OrdersTab()

        self.preprocessing_tab = OrdersTab("preprocessing")

        self.processing_tab = OrdersTab("processing")

        self.done_tab = OrdersTab("done")

        self.tabs.addTab(self.all_tab, "All")

        self.tabs.addTab(
            self.preprocessing_tab,
            "Preprocessing"
        )

        self.tabs.addTab(
            self.processing_tab,
            "Processing"
        )

        self.tabs.addTab(
            self.done_tab,
            "Done"
        )

        layout.addWidget(self.tabs)

        self.setStyleSheet(PRODUCTION_STYLE)

    def refresh(self):

        self.all_tab.refresh()

        self.preprocessing_tab.refresh()

        self.processing_tab.refresh()

        self.done_tab.refresh()


# ============================================
# PRODUCTION UI STYLE
# ============================================

PRODUCTION_STYLE = """

QWidget {
    background:#1e1e1e;
    color:white;
    font-family:Segoe UI;
}

QFrame#OrderCard {
    background:#2a2a2a;
    border-radius:8px;
    padding:10px;
}

QFrame#OrderCard:hover {
    background:#323232;
}

QPushButton#OrderHeader {
    border:none;
    text-align:left;
    font-weight:bold;
    font-size:15px;
}

QScrollArea {
    border:none;
}

QTabBar::tab {
    background:#2a2a2a;
    padding:10px 20px;
}

QTabBar::tab:selected {
    background:#0078d4;
}

"""
