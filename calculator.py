import sqlite3
import math

class CostCalculator:
    def __init__(self, db_path="logistics_decision.db"):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_customs_cost(self, hs_code, declared_value_usd, fx_rate=7.2):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT product_name, base_duty_rate, sec301_tariff_rate FROM Customs_Tariffs WHERE hs_code = ?",
                (hs_code,)
            )
            row = cur.fetchone()

        if not row:
            raise KeyError(f"HS code {hs_code} not found in database.")

        name, base_rate, sec301_rate = row
        declared_value_cny = declared_value_usd * fx_rate
        base_duty = declared_value_cny * base_rate
        sec301_duty = declared_value_cny * sec301_rate
        total_tax = base_duty + sec301_duty

        return {
            "product_name": name,
            "declared_cny": declared_value_cny,
            "total_tax": round(total_tax, 2)
        }

    def evaluate_shipment(self, length, width, height, actual_weight, hs_code, value_usd, max_days):
        customs = self.get_customs_cost(hs_code, value_usd)
        duty_amount = customs["total_tax"]
        volume = length * width * height

        query = """
        SELECT r.carrier_id, r.carrier_name, r.base_rate_12kg, r.per_kg_increment,
               r.dim_divisor, r.fuel_surcharge_rate, s.min_transit_days, s.max_transit_days
        FROM Carriers_Rates r
        JOIN Routing_SLA s ON r.carrier_id = s.carrier_id
        WHERE s.origin_country = 'CN' AND s.dest_country = 'US'
        """

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query)
            carriers = cur.fetchall()

        valid_routes = []
        for row in carriers:
            cid, name, base_rate, step_rate, divisor, fuel_rate, min_t, max_t = row

            # Drop options violating customer lead time constraint
            if max_t > max_days:
                continue

            # Dimensional weight check and ceil to integer kg
            dim_weight = volume / divisor
            chargeable_weight = math.ceil(max(actual_weight, dim_weight))

            # Tiered freight calculation
            if chargeable_weight <= 12:
                freight = base_rate
            else:
                freight = base_rate + (chargeable_weight - 12) * step_rate

            fuel_surcharge = freight * fuel_rate
            landed_cost = freight + fuel_surcharge + duty_amount

            valid_routes.append({
                "carrier_id": cid,
                "carrier_name": name,
                "transit_time": f"{min_t}-{max_t} days",
                "max_days": max_t,
                "chargeable_weight": chargeable_weight,
                "net_freight": round(freight, 2),
                "fuel_surcharge": round(fuel_surcharge, 2),
                "customs_duty": duty_amount,
                "landed_cost": round(landed_cost, 2)
            })

        return valid_routes


if __name__ == "__main__":
    calc = CostCalculator()
    
    # Baseline benchmark: 50x40x30 cm, 12 kg, $1500 value, strict SLA <= 6 days
    results = calc.evaluate_shipment(
        length=50, width=40, height=30, actual_weight=12,
        hs_code="9018902010", value_usd=1500, max_days=6
    )

    print(f"Eligible carriers found: {len(results)}\n")
    for r in results:
        print(f"[{r['carrier_id']}] {r['carrier_name']}")
        print(f"  Transit: {r['transit_time']} | Chargeable Weight: {r['chargeable_weight']} kg")
        print(f"  Freight: RMB {r['net_freight']} | Fuel: RMB {r['fuel_surcharge']} | Duty: RMB {r['customs_duty']}")
        print(f"  Total Landed Cost: RMB {r['landed_cost']}\n")