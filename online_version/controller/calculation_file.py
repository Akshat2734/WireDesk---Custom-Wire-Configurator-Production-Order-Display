import math
from PyQt6.QtWidgets import QLineEdit, QComboBox
from offiline_folder.lookup_table.lookup_registry import LOOKUP_TABLES

class CalculationEngine:
    #Here json data is the data that is recieved from the pyqt ui
    #Here context is a dictionary that will store every key:value for json recieved
    #for example for json_data = {name:3_Core_Wire, .....} then context will be a dictionary which name: 3_Core_wire, and so on.
    #safe_globals gets constants from the json_data and pass them to the build_safe_globals function.
    def __init__(self, json_data):
        self.data = json_data
        self.context = {}
        self.safe_globals = self.build_safe_globals(json_data.get("constants", {}))
    
    #checks if the constant name is in math directory, if yes then stores as key and value where key is the name of the math and value is of the name, example pi = key and value = 3.14
    def build_safe_globals(self, constants):
        safe = {"__builtins__": {}, "PI": math.pi}
        for name in dir(math):
            if not name.startswith("_"): safe[name] = getattr(math, name)
        for k, v in constants.items():
            if isinstance(v, (int, float)): safe[k] = v
        return safe

    #func goes through the json_data and checks if the data is contained inside calculated section of dictionary and skips that, now for the rest it goes through nested key value loop ensuring that if the key is a dictionary it can go through getting the real key and value
    #2nd loop checks if the key is not user input or from lookup and only get the the correct value for example dimensions, etc.
    def load_static_values(self, data=None):
        if data is None: data = self.data
        for k, v in data.items():
            if k == "calculated": continue 
            if isinstance(v, dict):
                self.load_static_values(v)
            elif isinstance(v, (int, float, str)):
                if v not in ["USER_INPUT", "FROM_LOOKUP"]:
                    # Only load static value if it's NOT already in context
                    if k not in self.context:
                        self.context[k] = v
                        
    #it loads user inputs from the ui, will be converted into getting data from middleware which will get data from ui
    #right now, data will be accepted from dictionary
    def load_user_inputs(self, inputs):
        for key, value in inputs.items():
            name = key.split(".")[-1]
            if type(value) == str:
                cleaned_string = value.strip()
                try:
                    self.context[name] = float(cleaned_string)
                except ValueError:
                    if cleaned_string:
                        self.context[name] = cleaned_string
                    else:
                        self.context[name] = 0.0
            else:
                self.context[name] = value

            """if isinstance(widget, QLineEdit):
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
                    self.context[name] = 0"""

    def load_fixed_lookup_values(self):
        """Loads fixed values from JSON (e.g. table_ref='Table 3 / Table 5')."""
        lookup = self.data.get("lookup_standard", {})
        for k, v in lookup.items():
            if v != "FROM_LOOKUP":
                # If the user selected 'Table 3', don't let JSON overwrite it with 'Table 3 / Table 5'
                if k not in self.context:
                    self.context[k] = v

    def load_lookup_tables(self):
        """
        Executes the lookup logic.
        Strictly prioritizes the single active table in self.context['table_ref'].
        """
        # 1. Get the table reference to run
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

    #responsible for calculation
    def evaluate_block(self, block):
        results = {}
        # Creates a single "allowed variable dictionary" for the math formulas.
        # Combines the safe math functions (like PI), current user/lookup context, and running results.
        eval_scope = self.safe_globals | self.context | results
        
        for key, expr in block.items():
            if isinstance(expr, str):
                try:
                    # Evaluates the math string (e.g., "core_thickness * 2.5").
                    # {"__builtins__": {}} is a crucial security measure that prevents 
                    # the formula from executing dangerous Python system commands.
                    res = eval(expr, {"__builtins__": {}}, eval_scope)
                    # Store the successful math result
                    results[key] = res
                    # Instantly add the new result back into eval_scope so that 
                    # subsequent formulas in the same block can use this new variable.
                    eval_scope[key] = res 
                except Exception as e:
                    # If the math fails (e.g., dividing by zero or missing variable), catch it safely.
                    results[key] = f"Error: {str(e)}"
            elif isinstance(expr, dict):
                # If the calculation block has nested dictionaries, run this function recursively
                results[key] = self.evaluate_block(expr)
            else:
                # If the value is already a raw number instead of a formula string, just save it.
                results[key] = expr
        # Merge all the newly calculated math results back into the main engine state
        self.context.update(results)
        return results

    """
        The master pipeline that processes an order from start to finish.
        The order of execution dictates priority (later steps overwrite earlier ones).
    """
    def calculate(self, inputs):
        # 0. Clear any leftover data from a previous order
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
        
        # Wraps everything in a root node, ready to be sent over WebSockets or REST API.
        return {"root": final_output}
    