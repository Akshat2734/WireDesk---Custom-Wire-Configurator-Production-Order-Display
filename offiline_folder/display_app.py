import sys
import qdarkstyle
from PyQt6.QtWidgets import QApplication, QMainWindow
from old_py_files.network_sync import SyncManager
from old_py_files.ordersdashboard import OrdersDashboard
from old_py_files.styles import GLOBAL_STYLE

class McDonaldDisplayWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Live Production Display")
        self.setMinimumSize(1000, 700)

        self.sync_manager = SyncManager()

        self.dashboard = OrdersDashboard(self.sync_manager)
        self.setCentralWidget(self.dashboard)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_STYLE)
    
    window = McDonaldDisplayWindow()
    window.show()
    
    sys.exit(app.exec())