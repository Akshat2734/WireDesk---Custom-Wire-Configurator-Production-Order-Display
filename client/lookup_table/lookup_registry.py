from lookup_table.lookup_table_3 import IS_694_TABLE_3
from lookup_table.lookup_table_4 import IS_694_TABLE_4
from lookup_table.lookup_table_5 import IS_694_TABLE_5
from lookup_table.lookup_table_6 import IS_694_TABLE_6
from lookup_table.lookup_table_7 import IS_694_TABLE_7
from lookup_table.lookup_table_9 import IS_694_TABLE_9
from lookup_table.lookup_table_10 import IS_694_TABLE_10

def smart_get(dictionary, key):
    if dictionary is None: return None
    if key in dictionary: return dictionary[key]
    try: return dictionary[float(key)]
    except: pass
    try: return dictionary[int(float(key))]
    except: pass
    return dictionary.get(str(key))

# --- HANDLERS ---

def handler_table_3(context):
    area = context.get("nominal_area_sqmm")
    cls_input = context.get("conductor_class") or context.get("class")
    
    cls_key = 2
    if cls_input:
        s_input = str(cls_input)
        if "1" in s_input: cls_key = 1
        elif "2" in s_input: cls_key = 2
        elif s_input == "1": cls_key = 1
        elif s_input == "2": cls_key = 2

    area_data = smart_get(IS_694_TABLE_3, area)
    if area_data:
        return area_data.get(cls_key, {})
    return {}

def handler_table_4(context):
    area = context.get("nominal_area_sqmm")
    return smart_get(IS_694_TABLE_4, area) or {}

def handler_table_5(context):
    area = context.get("nominal_area_sqmm")
    cores = context.get("number_of_cores")
    result = {}
    
    root_data = smart_get(IS_694_TABLE_5, area)
    if root_data:
        for k, v in root_data.items():
            if k != "cores": result[k] = v
        cores_dict = root_data.get("cores", {})
        core_data = smart_get(cores_dict, cores)
        if core_data: result.update(core_data)
    return result

def handler_table_6(context):
    area = context.get("nominal_area_sqmm")
    cores = context.get("number_of_cores")
    result = {}
    root_data = smart_get(IS_694_TABLE_6, area)
    if root_data:
        for k, v in root_data.items():
            if k != "cores": result[k] = v
        cores_dict = root_data.get("cores", {})
        core_data = smart_get(cores_dict, cores)
        if core_data: result.update(core_data)
    return result

def handler_table_7(context):
    area = context.get("nominal_area_sqmm")
    variant = context.get("variant", "")
    result = {}
    root_data = smart_get(IS_694_TABLE_7, area)
    if root_data:
        for k, v in root_data.items():
            if k not in ["cores", "parallel_twin", "twisted_twin"]: result[k] = v
        
        if variant == "TwinFlat":
            result.update(root_data.get("parallel_twin", {}))
        elif variant == "TwinTwisted":
            data = root_data.get("twisted_twin", {})
            result.update(data)
            if "max_overall_diameter_mm" in result:
                result["max_twisted_diameter_mm"] = result["max_overall_diameter_mm"]
        else:
            cores = context.get("number_of_cores")
            if cores:
                cores_dict = root_data.get("cores", {})
                core_data = smart_get(cores_dict, cores)
                if core_data: result.update(core_data)
    return result

def handler_table_9(context):
    area = context.get("nominal_area_sqmm")
    cores = context.get("number_of_cores")
    cores_data = smart_get(IS_694_TABLE_9, cores)
    if cores_data: return smart_get(cores_data, area) or {}
    return {}

def handler_table_10(context):
    area = context.get("nominal_area_sqmm")
    cores = context.get("number_of_cores")
    result = {}
    root_data = smart_get(IS_694_TABLE_10, area)
    if root_data:
        for k, v in root_data.items():
            if k != "cores": result[k] = v
        cores_dict = root_data.get("cores", {})
        core_data = smart_get(cores_dict, cores)
        if core_data: result.update(core_data)
    return result

# --- UI OPTIONS ---

def get_table_options(table_name):
    options = {"areas": [], "cores": [], "classes": []}
    def get_keys(d): return sorted(list(d.keys())) if d else []

    if table_name == "Table 3":
        options["areas"] = get_keys(IS_694_TABLE_3)
        found_classes = set()
        for area_data in IS_694_TABLE_3.values():
            found_classes.update(area_data.keys())
        for k in sorted(found_classes):
            options["classes"].append(f"Class {k}")
        
    elif table_name == "Table 4":
        options["areas"] = get_keys(IS_694_TABLE_4)
        
    elif table_name == "Table 5":
        options["areas"] = get_keys(IS_694_TABLE_5)
        c = set()
        for v in IS_694_TABLE_5.values():
            if "cores" in v: c.update(v["cores"].keys())
        options["cores"] = sorted(list(c))

    elif table_name == "Table 6":
        options["areas"] = get_keys(IS_694_TABLE_6)
        c = set()
        for v in IS_694_TABLE_6.values():
            if "cores" in v: c.update(v["cores"].keys())
        options["cores"] = sorted(list(c))
        
    elif table_name == "Table 7":
        options["areas"] = get_keys(IS_694_TABLE_7)
        c = set()
        for v in IS_694_TABLE_7.values():
            if "cores" in v: c.update(v["cores"].keys())
        options["cores"] = sorted(list(c))

    elif table_name == "Table 9":
        options["cores"] = get_keys(IS_694_TABLE_9)
        a = set()
        for v in IS_694_TABLE_9.values():
            a.update(v.keys())
        options["areas"] = sorted(list(a))
        
    elif table_name == "Table 10":
        options["areas"] = get_keys(IS_694_TABLE_10)
        c = set()
        for v in IS_694_TABLE_10.values():
            if "cores" in v: c.update(v["cores"].keys())
        options["cores"] = sorted(list(c))

    return options

LOOKUP_TABLES = {
    "Table 3": handler_table_3,
    "Table 4": handler_table_4,
    "Table 5": handler_table_5,
    "Table 6": handler_table_6,
    "Table 7": handler_table_7,
    "Table 9": handler_table_9,
    "Table 10": handler_table_10,
}
