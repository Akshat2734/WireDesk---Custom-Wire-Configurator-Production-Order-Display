import json
from datetime import datetime

from PyQt6.QtCore import QEvent, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)

from api_client import ApiError
from calculation_engine import CalculationEngine
from components.accordion import Accordion, AccordionSection
from components.json_form import JsonForm


class Overlay(QWidget):
    order_added = pyqtSignal()
    COMPLIANCE_FIELDS = {
        "insulation_meets_standard", "sheath_meets_standard",
        "dimensions_within_limit", "is_fully_compliant",
    }

    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.json_data = {}
        self.forms = []
        self.setStyleSheet("background: rgba(0,0,0,160);")
        if parent:
            self.setGeometry(parent.rect())
            parent.installEventFilter(self)

        main = QVBoxLayout(self)
        panel = QWidget()
        panel.setStyleSheet("background:#020302;border-radius:14px;")
        panel.setMinimumSize(600, 420)
        main.addWidget(panel, alignment=Qt.AlignmentFlag.AlignCenter)
        panel_layout = QVBoxLayout(panel)

        self.title = QLabel()
        self.title.setStyleSheet("font-size:18px;font-weight:700;")
        panel_layout.addWidget(self.title)
        self.accordion = Accordion()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.accordion)
        panel_layout.addWidget(scroll)

        buttons = QHBoxLayout()
        add = QPushButton("Add")
        close = QPushButton("Close")
        add.clicked.connect(self.add_order)
        close.clicked.connect(self.close)
        buttons.addWidget(add, alignment=Qt.AlignmentFlag.AlignCenter)
        buttons.addWidget(close, alignment=Qt.AlignmentFlag.AlignCenter)
        panel_layout.addLayout(buttons)

    def loadJson(self, path, title):
        try:
            with open(path, encoding="utf-8") as source:
                self.json_data = json.load(source)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "Product Error", str(exc))
            return

        self.title.setText(title)
        for section in self.accordion.sections:
            section.setParent(None)
        self.accordion.sections.clear()
        self.forms = []
        lookup_standard = self.json_data.get("lookup_standard", {})
        for key, value in self.json_data.items():
            if not isinstance(value, dict):
                continue
            form = JsonForm(value, lookup_standard)
            self.forms.append(form)
            self.accordion.add_section(AccordionSection(
                key.replace("_", " ").title(), form, self.accordion
            ))
            for field in form.inputs.values():
                if isinstance(field, QLineEdit):
                    field.textChanged.connect(self.recalculate)
                elif isinstance(field, QComboBox):
                    field.currentIndexChanged.connect(self.recalculate)
        if self.accordion.sections:
            self.accordion.open_section(self.accordion.sections[0])
        self.recalculate()

    def _calculate(self):
        inputs = {}
        for form in self.forms:
            inputs.update(form.inputs)
        root = CalculationEngine(self.json_data).calculate(inputs).get("root", {})
        flattened = {}

        def flatten(value):
            for key, item in value.items():
                if isinstance(item, dict):
                    flatten(item)
                else:
                    flattened[key] = item

        flatten(root)
        return flattened

    def recalculate(self):
        try:
            results = self._calculate()
        except Exception:
            return
        for form in self.forms:
            for output_key, widget in form.outputs.items():
                value = results.get(output_key.split(".")[-1], "")
                widget.setText(f"{value:.3f}" if isinstance(value, float) else str(value))

    def add_order(self):
        try:
            payload = self._calculate()
        except Exception as exc:
            QMessageBox.critical(self, "Calculation Error", str(exc))
            return

        failed = [
            field for field in self.COMPLIANCE_FIELDS if payload.get(field) != "Yes"
        ]
        if failed:
            QMessageBox.warning(
                self, "Compliance Failed", "These checks failed:\n\n" + "\n".join(failed)
            )
            return
        payload["order_id"] = "ORD" + datetime.now().strftime("%Y%m%d%H%M%S%f")
        try:
            self.api_client.create_order(payload)
        except ApiError as exc:
            QMessageBox.critical(self, "Order Not Saved", str(exc))
            return

        self.order_added.emit()
        QMessageBox.information(self, "Success", "Order saved to the server")
        self.close()

    def eventFilter(self, obj, event):
        if obj is self.parent() and event.type() == QEvent.Type.Resize:
            self.setGeometry(self.parent().rect())
        return super().eventFilter(obj, event)
