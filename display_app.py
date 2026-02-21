import sys
import qdarkstyle
from PyQt6.QtWidgets import QApplication, QMainWindow
from ordersdashboard import OrdersDashboard

class McDonaldDisplayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Production Display")
        self.setMinimumSize(1000, 700)
        
        # Embed the exact same dashboard
        self.dashboard = OrdersDashboard()
        self.setCentralWidget(self.dashboard)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    
    window = McDonaldDisplayWindow()
    window.show()
    
    sys.exit(app.exec())