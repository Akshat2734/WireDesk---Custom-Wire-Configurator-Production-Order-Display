import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from api_client import ApiClient
from network_sync import SyncManager
from components.ordersdashboard import OrdersDashboard
from styles import GLOBAL_STYLE


class FactoryDisplayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Production Display")
        self.setMinimumSize(1000, 700)
        self.api_client = ApiClient()
        self.sync_manager = SyncManager(self.api_client)
        self.setCentralWidget(OrdersDashboard(self.sync_manager))

    def closeEvent(self, event):
        self.sync_manager.close()
        super().closeEvent(event)


if __name__ == "__main__":
    application = QApplication(sys.argv)
    application.setStyleSheet(GLOBAL_STYLE)
    window = FactoryDisplayWindow()
    window.show()
    sys.exit(application.exec())
