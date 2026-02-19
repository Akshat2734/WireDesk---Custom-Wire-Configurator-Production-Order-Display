import json
from datetime import datetime
import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout,
    QPushButton, QScrollArea, QLineEdit, QComboBox, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QEvent

from json_form import JsonForm
from calculation_engine import CalculationEngine
from accordion import Accordion, AccordionSection

class Overlay(QWidget):
    
    COMPLIANCE_FIELDS = {
    "insulation_meets_standard",
    "sheath_meets_standard",
    "dimensions_within_limit",
    "is_fully_compliant"
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
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

        self.title = QLabel("")
        self.title.setStyleSheet("font-size:18px;font-weight:700;")
        panel_layout.addWidget(self.title)

        self.accordion = Accordion()

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.accordion)
        panel_layout.addWidget(self.scroll)

        button_layout = QHBoxLayout()

        close = QPushButton("Close")
        close.clicked.connect(self.close)

        add = QPushButton("Add")
        add.clicked.connect(self.addButton)
        
        close.setStyleSheet("background:#5A5A5A ;padding: 5px 50px 5px;border-radius:14px;")
        add.setStyleSheet("background:#5A5A5A ;padding: 5px 50px 5px;border-radius:14px;")

        button_layout.addWidget(add, alignment=Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(close, alignment=Qt.AlignmentFlag.AlignCenter)

        panel_layout.addLayout(button_layout)

    def loadJson(self, path, title):
        try:
            with open(path) as f:
                self.json_data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return

        self.title.setText(title)

        for sec in self.accordion.sections:
            sec.setParent(None)
        self.accordion.sections.clear()

        self.forms = []
        lookup_standard = self.json_data.get("lookup_standard", {})

        for key, value in self.json_data.items():
            if not isinstance(value, dict): continue

            form = JsonForm(value, lookup_standard)
            self.forms.append(form)

            section = AccordionSection(
                key.replace("_", " ").title(),
                form,
                self.accordion
            )
            self.accordion.add_section(section)

            for field in form.inputs.values():
                if isinstance(field, QLineEdit):
                    field.textChanged.connect(self.recalculate)
                elif isinstance(field, QComboBox):
                    field.currentIndexChanged.connect(self.recalculate)

        if self.accordion.sections:
            self.accordion.open_section(self.accordion.sections[0])    
        
        self.recalculate()
            
    def recalculate(self):
        inputs = {}
        outputs = {}

        for form in self.forms:
            inputs.update(form.inputs)
            outputs.update(form.outputs)

        try:
            engine = CalculationEngine(self.json_data)
            result = engine.calculate(inputs)
            data_root = result.get("root", {})
        except Exception as e:
            print(f"Engine Error: {e}")
            return

        flat_results = {}
        def flatten(d):
            for k, v in d.items():
                if isinstance(v, dict):
                    flatten(v)
                else:
                    flat_results[k] = v
        flatten(data_root)

        # --- FIX: CLEAR OLD VALUES ---
        for out_key, widget in outputs.items():
            field_name = out_key.split(".")[-1]
            
            if field_name in flat_results:
                val = flat_results[field_name]
                if isinstance(val, (int, float)):
                    widget.setText(f"{val:.3f}") 
                else:
                    widget.setText(str(val))
            else:
                # IMPORTANT: If the value is not in the new results, clear the field.
                # This fixes the "stale values" issue when switching tables.
                widget.setText("")

    def eventFilter(self, obj, event):
        if obj is self.parent() and event.type() == QEvent.Type.Resize:
            self.setGeometry(self.parent().rect())
        return super().eventFilter(obj, event)
    
    #@staticmethod
    def generate_order_id():
        return "ORD" + datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    def addButton(self):
        inputs = {}

        for form in self.forms:
            inputs.update(form.inputs)

        engine = CalculationEngine(self.json_data)

        try:
            result = engine.calculate(inputs)
            root = result.get("root", {})
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        failed = []

        for field in self.COMPLIANCE_FIELDS:
            if root.get(field) != "Yes":
                failed.append(field)

        if failed:
            QMessageBox.warning(
                self,
                "Compliance Failed",
                "These checks failed:\n\n" + "\n".join(failed)
            )
            return
        
        # for streamlit and right dashboard
        data_analysis = {
            #"order_id",
            "wire_type": root.get("wire_type"),
            "table_ref": root.get("table_ref"),
            "conductor_class": root.get("conductor_class"),
            "variant": root.get("variant"),
            "material": root.get("material"),
            "conductor_weight_kg": root.get("conductor_weight_kg"),
            "aluminium_weight_kg": root.get("aluminium_weight_kg"),
            "copper_rate_per_kg": root.get("copper_rate_per_kg"),
            "metal_rate_per_kg": root.get("metal_rate_per_kg"),
            "pvc_rate_per_kg": root.get("pvc_rate_per_kg"),
            "pvc_weight_kg": root.get("pvc_weight_kg"),
            "weight_per_meter_kg": root.get("weight_per_meter_kg"),
            "cost_per_meter": root.get("cost_per_meter"),
            "total_cost": root.get("total_cost"),
            "length_meters": root.get("length_meters")
        }
        
        order_display = {
            "wire_type": root.get("wire_type"),
            "variant": root.get("variant"),
            "material": root.get("material"),
            "nominal_area_sqmm": root.get("nominal_area_sqmm"),
            "number_of_cores": root.get("number_of_cores"),
            "nominal_insulation_ti_mm": root.get("nominal_insulation_ti_mm"),
            "nominal_sheath_ts_mm": root.get("nominal_sheath_ts_mm"),
            "max_width_mm": root.get("max_width_mm"),
            "max_height_mm": root.get("max_height_mm"),
            "max_overall_diameter_mm": root.get("max_overall_diameter_mm"),
            "max_twisted_diameter_mm" :root.get("max_twisted_diameter_mm"),
            "recommended_core_layup" : root.get("recommended_core_layup"),
            "tolerance_percent": root.get("tolerance_percent"),
            "number_of_strands": root.get("number_of_strands"),
            "inner_layer_percent": root.get("inner_layer_percent"),
            "outer_layer_percent": root.get("outer_layer_percent"),
            "length_meters": root.get("length_meters"),
            "number_of_strands_per_core": root.get("number_of_strands_per_core"),
            "strand_diameter_mm": root.get("strand_diameter_mm"),
            "insulation_percent": root.get("insulation_percent"),
            "bedding_percent": root.get("bedding_percent"),
            "sheath_percent": root.get("sheath_percent")
        }

        print(data_analysis)
        print(order_display)
        
        Overlay.save_both_dbs(data_analysis, order_display)
        
        QMessageBox.information(
            self,
                "Success",
                "Order saved successfully"
        )
        
        self.close()
    
    
    @staticmethod
    def save_both_dbs(analytics, order):

        order_id = Overlay.generate_order_id()

        # ---------- Analytics DB ----------
        conn_a = sqlite3.connect("db/analytics.db")
        cur_a = conn_a.cursor()

        cur_a.execute("""
            INSERT INTO analytics
            (
                order_id,
                wire_type,
                table_ref,
                conductor_class,
                variant,
                material,
                conductor_weight_kg,
                aluminium_weight_kg,
                copper_rate_per_kg,
                metal_rate_per_kg,
                pvc_rate_per_kg,
                pvc_weight_kg,
                weight_per_meter_kg,
                cost_per_meter,
                total_cost,
                length_meters
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_id,
                analytics.get("wire_type"),
                analytics.get("table_ref"),
                analytics.get("conductor_class"),
                analytics.get("variant"),
                analytics.get("material"),
                analytics.get("conductor_weight_kg"),
                analytics.get("aluminium_weight_kg"),
                analytics.get("copper_rate_per_kg"),
                analytics.get("metal_rate_per_kg"),
                analytics.get("pvc_rate_per_kg"),
                analytics.get("pvc_weight_kg"),
                analytics.get("weight_per_meter_kg"),
                analytics.get("cost_per_meter"),
                analytics.get("total_cost"),
                analytics.get("length_meters")
            ))


        conn_a.commit()
        conn_a.close()

        # ---------- Orders DB ----------
        conn_o = sqlite3.connect("db/orders.db")
        cur_o = conn_o.cursor()

        cur_o.execute("""
            INSERT INTO orders
            (
                order_id,
                wire_type,
                variant,
                material,
                nominal_area_sqmm,
                number_of_cores,
                conductor_class,
                nominal_insulation_ti_mm,
                nominal_sheath_ts_mm,
                max_width_mm,
                max_height_mm,
                max_overall_diameter_mm,
                max_twisted_diameter_mm,
                recommended_core_layup,
                strand_diameter_mm,
                tolerance_percent,
                number_of_strands_per_core,
                number_of_strands,
                insulation_percent,
                inner_layer_percent,
                outer_layer_percent,
                bedding_percent,
                sheath_percent,
                length_meters
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_id,
                order.get("wire_type"),
                order.get("variant"),
                order.get("material"),
                order.get("nominal_area_sqmm"),
                order.get("number_of_cores"),
                order.get("conductor_class"),
                order.get("nominal_insulation_ti_mm"),
                order.get("nominal_sheath_ts_mm"),
                order.get("max_width_mm"),
                order.get("max_height_mm"),
                order.get("max_overall_diameter_mm"),
                order.get("max_twisted_diameter_mm"),
                order.get("recommended_core_layup"),
                order.get("strand_diameter_mm"),
                order.get("tolerance_percent"),
                order.get("number_of_strands_per_core"),
                order.get("number_of_strands"),
                order.get("insulation_percent"),
                order.get("inner_layer_percent"),
                order.get("outer_layer_percent"),
                order.get("bedding_percent"),
                order.get("sheath_percent"),
                order.get("length_meters")
            ))


        conn_o.commit()
        conn_o.close()

        print("Saved Order:", order_id)