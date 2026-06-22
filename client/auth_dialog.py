from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QMessageBox, QPushButton,
    QVBoxLayout,
)

from api_client import ApiError


class AuthDialog(QDialog):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setWindowTitle("WireDesk Sign In")

        self.username = QLineEdit()
        self.email = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        form = QFormLayout()
        form.addRow("Username", self.username)
        form.addRow("Email", self.email)
        form.addRow("Password", self.password)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        sign_in = QPushButton("Sign In")
        register = QPushButton("Register")
        buttons.addButton(sign_in, QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.addButton(register, QDialogButtonBox.ButtonRole.ActionRole)
        sign_in.clicked.connect(self.sign_in)
        register.clicked.connect(self.register)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def credentials(self):
        return (
            self.username.text().strip(),
            self.email.text().strip(),
            self.password.text(),
        )

    def sign_in(self):
        try:
            self.api_client.sign_in(*self.credentials())
        except ApiError as exc:
            QMessageBox.warning(self, "Sign In Failed", str(exc))
            return
        self.accept()

    def register(self):
        try:
            self.api_client.register(*self.credentials())
            self.api_client.sign_in(*self.credentials())
        except ApiError as exc:
            QMessageBox.warning(self, "Registration Failed", str(exc))
            return
        self.accept()
