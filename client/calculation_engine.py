import math
from PyQt6.QtWidgets import QLineEdit, QComboBox
from lookup_table.lookup_registry import LOOKUP_TABLES

class CalculationEngine:
    def __init__(self, json_data):
        self.data = json_data
        self.context = {}
        self.safe_globals = self.build_safe_globals(json_data.get("constants", {}))

    def build_safe_globals(self, constants):
        safe = {"__builtins__": {}, "PI": math.pi}
        for name in dir(math):
            if not name.startswith("_"): safe[name] = getattr(math, name)
        for k, v in constants.items():
            if isinstance(v, (int, float)): safe[k] = v
        return safe

    def load_static_values(self, data=None):
        if data is None: data = self.data
        for k, v in data.items():
            if k == "calculated": continue 
            if isinstance(v, dict):
                self.load_static_values(v)
            elif isinstance(v, (int, float, str)):
                if v not in ["USER_INPUT", "FROM_LOOKUP"]:
                    # FIX 1: Only load static value if it's NOT already in context
                    if k not in self.context:
                        self.context[k] = v

    def load_user_inputs(self, inputs):
        for key, widget in inputs.items():
            name = key.split(".")[-1]

            if isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if text:
                    try:
                        self.context[name] = float(text)
                    except ValueError:
                        self.context[name] = 0.0
            
            elif isinstance(widget, QComboBox):
                val = widget.currentData()
                if val is not None:
                    self.context[name] = val
                else:
                    self.context[name] = 0

    def load_fixed_lookup_values(self):
        """Loads fixed values from JSON (e.g. table_ref='Table 3 / Table 5')."""
        lookup = self.data.get("lookup_standard", {})
        for k, v in lookup.items():
            if v != "FROM_LOOKUP":
                # FIX 2: CRITICAL - Do not overwrite User Selection!
                # If the user selected 'Table 3', don't let JSON overwrite it with 'Table 3 / Table 5'
                if k not in self.context:
                    self.context[k] = v

    def load_lookup_tables(self):
        """
        Executes the lookup logic.
        Strictly prioritizes the single active table in self.context['table_ref'].
        """
        # 1. Get the table reference to run
        # Because of FIX 2, self.context['table_ref'] now holds the USER SELECTION (e.g., "Table 3")
        # instead of the JSON string (e.g., "Table 3 / Table 5").
        ref_raw = self.context.get("table_ref")
        
        tables_to_run = []

        if isinstance(ref_raw, str):
            # If the value contains a slash (meaning multiple tables defined but NO user selection made yet),
            # split them. Otherwise, use the single string.
            if "/" in ref_raw:
                tables_to_run = [t.strip() for t in ref_raw.split("/")]
            else:
                tables_to_run = [ref_raw]
        elif isinstance(ref_raw, list):
            tables_to_run = ref_raw

        # 2. Execute
        # If the user selected "Table 3", tables_to_run is just ["Table 3"].
        # Table 5 never runs, preventing the overwrite/max value issue.
        for table_name in tables_to_run:
            handler = LOOKUP_TABLES.get(table_name)
            if callable(handler):
                result = handler(self.context)
                self.context.update(result)

    def evaluate_block(self, block):
        results = {}
        eval_scope = self.safe_globals | self.context | results
        
        for key, expr in block.items():
            if isinstance(expr, str):
                try:
                    res = eval(expr, {"__builtins__": {}}, eval_scope)
                    results[key] = res
                    eval_scope[key] = res 
                except Exception as e:
                    results[key] = f"Error: {str(e)}"
            elif isinstance(expr, dict):
                results[key] = self.evaluate_block(expr)
            else:
                results[key] = expr
        self.context.update(results)
        return results

    def calculate(self, inputs):
        self.context.clear()
        
        # 1. Load Constants (lowest priority)
        self.load_static_values()

        # 2. Load User Inputs (User choice overrides constants)
        self.load_user_inputs(inputs)

        # 3. Load Fixed JSON values (Only if User didn't provide them)
        self.load_fixed_lookup_values()
        
        # 4. Lookup Data (Now runs strictly 1 table if selected)
        self.load_lookup_tables()
        
        # 5. Calculations
        calculated_results = self.evaluate_block(self.data.get("calculated", {}))
        
        # 6. Return Full Context
        final_output = self.context.copy()
        final_output.update(calculated_results)
        
        return {"root": final_output}
    
