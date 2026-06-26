PRIMARY_COLOR = "#4da3ff"

GLOBAL_STYLE = """
/* ===== App Background ===== */
QWidget {
    background-color: #181c24;
    color: #e6edf3;
    font-family: Segoe UI;
    font-size: 13px;
}

/* ===== Top Bar ===== */
QPushButton {
    background-color: #232937;
    border-radius: 6px;
    padding: 6px 12px;
}

QPushButton:hover {
    background-color: #2d3545;
}

QPushButton:pressed {
    background-color: #3a4357;
}

/* ===== Cards ===== */
QFrame#OrderCard {
    background-color: #232937;
    border-radius: 12px;
    padding: 14px;
    border: 1px solid #2f3748;
}

QFrame#OrderCard:hover {
    border: 1px solid #4da3ff;
}

/* ===== Card Header ===== */
QPushButton#OrderHeader {
    border: none;
    text-align: left;
    font-weight: 600;
    font-size: 15px;
    color: #ffffff;
}

/* ===== Dropdown ===== */
QComboBox {
    background-color: #2d3545;
    border: 1px solid #3d475c;
    border-radius: 6px;
    padding: 4px 8px;
}

QComboBox:hover {
    border: 1px solid #4da3ff;
}

/* ===== Scroll Area ===== */
QScrollArea {
    border: none;
}

/* ===== Tabs ===== */
QTabWidget::pane {
    border: none;
}

QTabBar::tab {
    background: #232937;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background: #4da3ff;
    color: black;
}

QTabBar::tab:hover {
    background: #2d3545;
}

QLineEdit, QComboBox {
    background-color: #232937;
    border: 1px solid #3d475c;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e6edf3;
}

QLineEdit:hover, QComboBox:hover, QLineEdit:focus, QComboBox:focus {
    border: 1px solid #4da3ff;
    background-color: #2d3545;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

/* The dropdown menu list */
QComboBox QAbstractItemView {
    background-color: #232937;
    border: 1px solid #4da3ff;
    border-radius: 6px;
    selection-background-color: #4da3ff;
    selection-color: #000000;
    outline: none; /* Removes the dotted focus rect */
    padding: 4px;
}
"""