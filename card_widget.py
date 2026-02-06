from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

class Card(QFrame):
    clicked = pyqtSignal(str, str)

    def __init__(self, title, details, img, json_file):
        super().__init__()
        
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        self.setStyleSheet(
            """ 
            QFrame
                { background:#2e2e2e; 
                color:white; } 
            QFrame:hover 
                { background:#3a3a3a; } 
            """)

        self.json_file = json_file
        self.title = title
        self.setObjectName("card")
        self.setMinimumSize(200, 220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        image = QLabel()
        pix = QPixmap(img)
        image.setPixmap(
            pix.scaled(180, 120, Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation)
        )
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)

        layout.addWidget(image)
        layout.addWidget(title_label)

        for w in (image, title_label):
            w.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)    
            w.setStyleSheet("background: transparent;")

    def mousePressEvent(self, event):
        self.clicked.emit(self.json_file, self.title)
