import sys
import os
from init_db import init_schema
from calculator import CostCalculator
from optimizer import run_batch_optimization
from analytics import run_tariff_sensitivity, run_fuel_switching_analysis

def main():
    print("=" * 60)
    print("Cross-Border Logistics Decision & Optimization Pipeline")
    print("=" * 60)

    # Step 1: Database Initialization
    print("\n[Step 1/4] Initializing Database Schema & Seed Tariffs...")
    init_schema()

    # Step 2: Baseline Single Consignment Assessment
    print("\n[Step 2/4] Evaluating Baseline Consignment (Portable BP Monitor)...")
    calc = CostCalculator()
    baseline_results = calc.evaluate_shipment(
        length=50, width=40, height=30, actual_weight=12,
        hs_code="9018902010", value_usd=1500, max_days=6
    )
    for r in baseline_results:
        print(f"  - [{r['carrier_id']}] {r['carrier_name']}: "
              f"Landed Cost = RMB {r['landed_cost']} | Transit = {r['transit_time']}")

    # Step 3: Batch Simulation & Pareto Optimization
    print("\n[Step 3/4] Running 50-Order Batch Pareto Optimization...")
    run_batch_optimization()

    # Step 4: Sensitivity Modeling & Visual Analytics
    print("\n[Step 4/4] Executing Sensitivity Models & Generating Visuals...")
    os.makedirs("assets", exist_ok=True)
    run_tariff_sensitivity()
    run_fuel_switching_analysis()

    print("\n" + "=" * 60)
    print("Pipeline finished successfully! All analytical assets generated.")
    print("=" * 60)

if __name__ == "__main__":
    main()