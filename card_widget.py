from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

class Card(QFrame):
    clicked = pyqtSignal(str, str)

    def __init__(self, title, details, img, json_file):
        super().__init__()
        
        # 1. Identity for CSS
        self.setObjectName("card") 
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.default_style = """
        QFrame#card {
            background-color: #2a2d32;
            border: 2px solid #3a3f45;
            border-radius: 22px;
        }
        """

        self.hover_style = """
        QFrame#card {
            background-color: #32363c;
            border: 2px solid #0078d4;
            border-radius: 22px;
        }
        """

        self.setStyleSheet(self.default_style)
        
        # 2. Required for custom QFrame subclasses to render CSS
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.json_file = json_file
        self.title = title
        self.setMinimumSize(220, 240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Image Container
        image = QLabel()
        pix = QPixmap(img)
        if not pix.isNull():
            image.setPixmap(
                pix.scaled(180, 140, Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation)
            )
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title Container
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        # Note: We removed the hardcoded setStyleSheet here to prevent interference

        layout.addWidget(image)
        layout.addWidget(title_label)

        # 3. Ensure clicks and hover events reach the QFrame
        image.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.json_file, self.title)
            
    def enterEvent(self, event):
        self.setStyleSheet(self.hover_style)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.default_style)
        super().leaveEvent(event)