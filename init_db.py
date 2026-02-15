import sqlite3

DB_NAME = "logistics_decision.db"

def init_schema():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Carriers_Rates (
        carrier_id TEXT PRIMARY KEY,
        carrier_name TEXT NOT NULL,
        base_rate_12kg REAL NOT NULL,
        per_kg_increment REAL NOT NULL,
        dim_divisor INTEGER NOT NULL,
        fuel_surcharge_rate REAL NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Routing_SLA (
        route_id INTEGER PRIMARY KEY AUTOINCREMENT,
        carrier_id TEXT NOT NULL,
        origin_country TEXT NOT NULL,
        dest_country TEXT NOT NULL,
        min_transit_days INTEGER NOT NULL,
        max_transit_days INTEGER NOT NULL,
        FOREIGN KEY (carrier_id) REFERENCES Carriers_Rates (carrier_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Customs_Tariffs (
        hs_code TEXT PRIMARY KEY,
        product_name TEXT NOT NULL,
        base_duty_rate REAL NOT NULL,
        sec301_tariff_rate REAL NOT NULL
    );
    """)

    # Base pricing from DHL 2026 published tariff, paired with industry benchmark profiles
    carrier_records = [
        ("DHL_EXP", "DHL Express Worldwide", 4149.0, 300.0, 5000, 0.22),
        ("FDX_ECO", "FedEx International Economy", 3580.0, 260.0, 5000, 0.18),
        ("UPS_SAV", "UPS Saver / Dedicated Air", 2950.0, 210.0, 6000, 0.15)
    ]

    # Transit SLAs (CN to US lane)
    sla_records = [
        ("DHL_EXP", "CN", "US", 3, 4),
        ("FDX_ECO", "CN", "US", 5, 6),
        ("UPS_SAV", "CN", "US", 7, 8)
    ]

    # USITC import duty baseline and Section 301 punitive tariff rates
    tariff_records = [
        ("9018902010", "Portable Blood Pressure Monitor", 0.00, 0.075),
        ("6307909889", "Protective Medical Coverall", 0.045, 0.25),
        ("9018908400", "Surgical Metallic Parts", 0.00, 0.25)
    ]

    cur.executemany("INSERT OR REPLACE INTO Carriers_Rates VALUES (?, ?, ?, ?, ?, ?);", carrier_records)
    cur.executemany("INSERT OR REPLACE INTO Routing_SLA (carrier_id, origin_country, dest_country, min_transit_days, max_transit_days) VALUES (?, ?, ?, ?, ?);", sla_records)
    cur.executemany("INSERT OR REPLACE INTO Customs_Tariffs VALUES (?, ?, ?, ?);", tariff_records)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_schema()
    print("Database schema and seed data initialized successfully.")