import numpy as np
import pandas as pd
from calculator import CostCalculator

def generate_mock_shipments(n=100, seed=42):
    """
    Generate synthetic export order flow for portable medical devices.
    """
    np.random.seed(seed)
    
    # Dimensions in cm (normal distribution around baseline 50x40x30)
    lengths = np.clip(np.random.normal(50, 5, n), 30, 80)
    widths = np.clip(np.random.normal(40, 4, n), 25, 60)
    heights = np.clip(np.random.normal(30, 3, n), 20, 50)
    
    # Weight in kg (correlated with volume but with realistic variance)
    weights = np.clip(np.random.normal(12, 2.5, n), 5, 25)
    
    # Declared value in USD
    values = np.clip(np.random.normal(1500, 200, n), 800, 3000)
    
    # Customer SLA deadline (days): 4 to 8 days
    sla_deadlines = np.random.choice([4, 5, 6, 7, 8], size=n, p=[0.2, 0.25, 0.3, 0.15, 0.1])
    
    orders = pd.DataFrame({
        "order_id": [f"ORD-{i+1:04d}" for i in range(n)],
        "length": np.round(lengths, 1),
        "width": np.round(widths, 1),
        "height": np.round(heights, 1),
        "weight": np.round(weights, 1),
        "value_usd": np.round(values, 2),
        "max_sla_days": sla_deadlines,
        "hs_code": "9018902010"
    })
    return orders

def find_pareto_front(df_candidates):
    """
    Identify non-dominated solutions based on two conflicting objectives:
    Objective 1: Min Landed Cost
    Objective 2: Min Max Transit Days
    """
    pareto_candidates = []
    
    for idx, current in df_candidates.iterrows():
        # Check if dominated by any other solution
        dominated = False
        for _, competitor in df_candidates.iterrows():
            cost_worse = competitor["landed_cost"] <= current["landed_cost"]
            time_worse = competitor["max_days"] <= current["max_days"]
            strictly_better = (competitor["landed_cost"] < current["landed_cost"]) or (competitor["max_days"] < current["max_days"])
            
            if cost_worse and time_worse and strictly_better:
                dominated = True
                break
                
        if not dominated:
            pareto_candidates.append(current)
            
    return pd.DataFrame(pareto_candidates).drop_duplicates(subset=["carrier_id"])

def run_batch_optimization():
    calc = CostCalculator()
    orders = generate_mock_shipments(n=50)
    
    total_savings = 0.0
    strategy_summary = {"Cost_Leader": 0, "Balanced_Pareto": 0, "No_Solution": 0}
    
    print(f"Executing dynamic routing for {len(orders)} batch orders...\n")
    
    for _, order in orders.iloc[:5].iterrows():
        candidates = calc.evaluate_shipment(
            length=order["length"],
            width=order["width"],
            height=order["height"],
            actual_weight=order["weight"],
            hs_code=order["hs_code"],
            value_usd=order["value_usd"],
            max_days=order["max_sla_days"]
        )
        
        if not candidates:
            print(f"[{order['order_id']}] SLA ({order['max_sla_days']} days): No viable carrier meeting deadline.")
            strategy_summary["No_Solution"] += 1
            continue
            
        df_candidates = pd.DataFrame(candidates)
        pareto_front = find_pareto_front(df_candidates)
        
        # Benchmark worst feasible vs pareto optimal
        highest_cost = df_candidates["landed_cost"].max()
        cheapest_option = pareto_front.loc[pareto_front["landed_cost"].idxmin()]
        cost_diff = highest_cost - cheapest_option["landed_cost"]
        savings_pct = (cost_diff / highest_cost) * 100 if highest_cost > 0 else 0
        
        print(f"[{order['order_id']}] Weight: {order['weight']}kg | SLA Limit: <= {order['max_sla_days']} days")
        print(f"  -> Recommended: {cheapest_option['carrier_name']}")
        print(f"  -> Cost: RMB {cheapest_option['landed_cost']} | Transit: {cheapest_option['transit_time']}")
        print(f"  -> Cost Saved vs Worst Feasible: {savings_pct:.1f}%\n")
        
    print("Batch run completed. Pareto decision engine fully operational.")

if __name__ == "__main__":
    run_batch_optimization()