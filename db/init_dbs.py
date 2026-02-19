import sqlite3

# ========== ANALYTICS DB ==========
conn_a = sqlite3.connect("db/analytics.db")
cur_a = conn_a.cursor()

cur_a.execute("""
CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT UNIQUE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    wire_type TEXT,
    table_ref TEXT,
    conductor_class TEXT,
    variant TEXT,
    material TEXT,
    conductor_weight_kg REAL,
    aluminium_weight_kg REAL,
    copper_rate_per_kg REAL,
    metal_rate_per_kg REAL,
    pvc_rate_per_kg REAL,
    pvc_weight_kg REAL,
    weight_per_meter_kg REAL,
    cost_per_meter REAL,
    total_cost REAL,
    length_meters INTEGER
)
""")

conn_a.commit()
conn_a.close()


# ========== ORDERS DB ==========
conn_o = sqlite3.connect("db/orders.db")
cur_o = conn_o.cursor()

cur_o.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT UNIQUE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    wire_type TEXT,
    variant TEXT,
    material TEXT,
    nominal_area_sqmm REAL,
    number_of_cores INTEGER,
    conductor_class REAL,
    nominal_insulation_ti_mm REAL,
    nominal_sheath_ts_mm REAL,
    max_width_mm REAL,
    max_height_mm REAL,
    max_overall_diameter_mm REAL,
    max_twisted_diameter_mm REAL,
    recommended_core_layup REAL,
    strand_diameter_mm REAL,
    tolerance_percent REAL,
    number_of_strands_per_core INTEGER,
    number_of_strands INTEGER,
    insulation_percent REAL,
    inner_layer_percent REAL,
    outer_layer_percent REAL,
    bedding_percent REAL,
    sheath_percent REAL,
    length_meters INT
)
""")

conn_o.commit()
conn_o.close()

print("analytics.db + orders.db created")
