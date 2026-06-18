from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt
from old_py_files.lookup_table.lookup_registry import get_table_options

USER_INPUT = "USER_INPUT"
FROM_LOOKUP = "FROM_LOOKUP"

SELECTOR_KEYS = {
    "table_ref",
    "nominal_area_sqmm",
    "number_of_cores",
    "conductor_class",
    "class"
}

class JsonForm(QWidget):
    def __init__(self, data, lookup_standard=None):
        super().__init__()
        self.inputs = {}
        self.outputs = {}
        self.lookup_standard = lookup_standard or {}

        # Widget Refs
        self.ref_combo_table = None
        self.ref_combo_area = None
        self.ref_combo_cores = None
        self.ref_combo_class = None
        
        # Row Refs
        self.row_widget_cores = None
        self.row_widget_class = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.build(data, layout, section=None)
        
        if self.ref_combo_table:
            self.update_selectors()

    def build(self, data, layout, prefix="", section=None):
        for key, value in data.items():

            if isinstance(value, dict):
                header = QLabel(key.replace("_", " ").title())
                header.setStyleSheet("font-weight:600;margin-top:10px;")
                layout.addWidget(header)
                
                next_section = section
                if key in ("per_core", "assembly", "weights", "pricing", "compliance"):
                    next_section = "calculated"
                
                self.build(value, layout, f"{prefix}{key}.", next_section)
                continue

            row_container = QWidget()
            row_layout = QHBoxLayout(row_container)
            row_layout.setContentsMargins(0,0,0,0)
            
            label = QLabel(key.replace("_", " ").title())
            label.setMinimumWidth(240)

            if value == USER_INPUT:
                field = QLineEdit()
                field.setAlignment(Qt.AlignmentFlag.AlignRight)
                self.inputs[f"{prefix}{key}"] = field
                row_layout.addWidget(label)
                row_layout.addWidget(field)
                layout.addWidget(row_container)
                continue

            if key == "table_ref":
                combo = QComboBox()
                tables = [t.strip() for t in value.split("/")]
                for t in tables:
                    combo.addItem(t, t)
                
                combo.currentIndexChanged.connect(self.update_selectors)
                self.inputs[f"{prefix}{key}"] = combo
                self.ref_combo_table = combo

                row_layout.addWidget(label)
                row_layout.addWidget(combo)
                layout.addWidget(row_container)
                continue

            if value == FROM_LOOKUP and key in SELECTOR_KEYS:
                combo = QComboBox()
                self.inputs[f"{prefix}{key}"] = combo
                
                row_layout.addWidget(label)
                row_layout.addWidget(combo)
                layout.addWidget(row_container)

                if "nominal_area_sqmm" in key:
                    self.ref_combo_area = combo
                elif "number_of_cores" in key:
                    self.ref_combo_cores = combo
                    self.row_widget_cores = row_container
                elif "conductor_class" in key or key == "class":
                    self.ref_combo_class = combo
                    self.row_widget_class = row_container
                
                continue

            field = QLineEdit()
            field.setReadOnly(True)
            field.setAlignment(Qt.AlignmentFlag.AlignRight)
            if isinstance(value, (int, float, str)) and value != FROM_LOOKUP:
                field.setText(str(value))
            self.outputs[f"{prefix}{key}"] = field
            row_layout.addWidget(label)
            row_layout.addWidget(field)
            layout.addWidget(row_container)

    def update_selectors(self):
        if not self.ref_combo_table: return

        table_name = self.ref_combo_table.currentData()
        if not table_name: return

        options = get_table_options(table_name)
        
        def configure_field(combo, row_widget, data_list):
            if combo is None: return 

            if data_list:
                if row_widget: row_widget.setVisible(True)
                
                old_val = combo.currentData()
                
                # 1. Clear old data (Block signals to prevent intermediate noise)
                combo.blockSignals(True)
                combo.clear()
                for item in data_list:
                    combo.addItem(str(item), item)
                combo.blockSignals(False) 
                
                # 2. Set Index (This MUST trigger signal if we want auto-recalc)
                # We do NOT block signals here so the engine knows data changed
                idx = combo.findData(old_val)
                if idx >= 0:
                    if combo.currentIndex() != idx:
                        combo.setCurrentIndex(idx) # This triggers signal if changed
                    else:
                        # If index is same but underlying context changed (new table),
                        # we might need to force emit.
                        combo.currentIndexChanged.emit(idx)
                elif combo.count() > 0:
                    combo.setCurrentIndex(0) # This triggers signal
            else:
                if row_widget: 
                    row_widget.setVisible(False)
                    combo.blockSignals(True)
                    combo.clear()
                    combo.blockSignals(False)

        configure_field(self.ref_combo_area, None, options.get("areas", []))
        configure_field(self.ref_combo_cores, self.row_widget_cores, options.get("cores", []))
        configure_field(self.ref_combo_class, self.row_widget_class, options.get("classes", []))