import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)

from api_client import ApiClient, ApiError
from network_sync import SyncManager
from app import MainWindow
from display_app import FactoryDisplayWindow
from styles import GLOBAL_STYLE, PRIMARY_COLOR


class LoginWindow(QWidget):
    def __init__(self, api_client=None):
        super().__init__()
        self.api_client = api_client or ApiClient() 
        self.sync_manager = SyncManager(self.api_client)
        self.setWindowTitle("WireDesk - Authentication")
        self.resize(450, 550)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        # Logo
        logo = QLabel("WIREDESK")
        logo.setStyleSheet(f"color: {PRIMARY_COLOR}; font-size: 36px; font-weight: 900; letter-spacing: 2px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        layout.addSpacing(30)

        # Inputs
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email Address")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        for field in (self.username, self.email, self.password):
            field.setMinimumHeight(45)
            layout.addWidget(field)

        layout.addSpacing(20)

        # Buttons
        self.sign_in_btn = QPushButton("Sign In")
        self.sign_in_btn.setMinimumHeight(45)
        self.sign_in_btn.setStyleSheet(f"background-color: {PRIMARY_COLOR}; color: black; font-weight: bold;")
        self.sign_in_btn.clicked.connect(self.sign_in)

        self.register_btn = QPushButton("Register")
        self.register_btn.setMinimumHeight(45)
        self.register_btn.clicked.connect(self.register)

        layout.addWidget(self.sign_in_btn)
        layout.addWidget(self.register_btn)

    def credentials(self):
        return (
            self.username.text().strip(),
            self.email.text().strip(),
            self.password.text()
        )

    def sign_in(self):
        try:
            self.api_client.sign_in(*self.credentials())
            self.route_user()
        except ApiError as exc:
            QMessageBox.warning(self, "Sign In Failed", str(exc))

    def register(self):
        try:
            self.api_client.register(*self.credentials())
            self.api_client.sign_in(*self.credentials())  # Auto sign-in after register
            self.route_user()
        except ApiError as exc:
            QMessageBox.warning(self, "Registration Failed", str(exc))

    def route_user(self):
        # NOTE: Ensure your backend /login route returns the user role.
        # e.g., getattr(self.api_client, 'role', 'viewer')
        # For now, we will assume 'admin' if not explicitly defined to prevent breaking.
        role = getattr(self.api_client, 'role', 'admin')

        if role == 'view':
            self.app_window = FactoryDisplayWindow(self.api_client)
        else:
            self.app_window = MainWindow(self.api_client)

        self.app_window.show()
        self.close()


if __name__ == "__main__":
    application = QApplication(sys.argv)
    application.setStyleSheet(GLOBAL_STYLE)
    
    window = LoginWindow()
    window.show()
    
    sys.exit(application.exec())