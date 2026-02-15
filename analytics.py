import numpy as np
import matplotlib.pyplot as plt
from calculator import CostCalculator

def run_tariff_sensitivity():
    """
    Evaluate landed cost sensitivity against fluctuating Section 301 tariff rates (0% to 30%).
    Baseline parcel: 50x40x30 cm, 12 kg, $1500 value, HS: 9018902010.
    """
    calc = CostCalculator()
    tariffs = np.linspace(0.0, 0.30, 31)  # 0% to 30% step 1%
    
    fx_rate = 7.2
    declared_cny = 1500 * fx_rate
    
    # Calculate baseline shipping freight + fuel (DHL baseline)
    dhl_freight = 4149.0
    dhl_fuel = dhl_freight * 0.22
    fixed_shipping_dhl = dhl_freight + dhl_fuel
    
    # Calculate landed costs across tariff range
    landed_costs = [fixed_shipping_dhl + (declared_cny * t) for t in tariffs]
    duty_proportions = [(declared_cny * t) / cost * 100 for t, cost in zip(tariffs, landed_costs)]
    
    plt.figure(figsize=(10, 5))
    
    # Subplot 1: Total Landed Cost vs Tariff Rate
    plt.subplot(1, 2, 1)
    plt.plot(tariffs * 100, landed_costs, color="#1f77b4", linewidth=2.5, label="Total Landed Cost")
    plt.axvline(x=7.5, color="red", linestyle="--", label="Current Tariff (7.5%)")
    plt.title("Landed Cost vs Section 301 Tariff", fontsize=12, fontweight="bold")
    plt.xlabel("Section 301 Tariff Rate (%)", fontsize=10)
    plt.ylabel("Total Landed Cost (RMB)", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    
    # Subplot 2: Duty Exposure Ratio (%)
    plt.subplot(1, 2, 2)
    plt.plot(tariffs * 100, duty_proportions, color="#ff7f0e", linewidth=2.5, label="Duty Exposure %")
    plt.axvline(x=7.5, color="red", linestyle="--", label="Current Tariff (7.5%)")
    plt.title("Customs Duty Proportion in Total Cost", fontsize=12, fontweight="bold")
    plt.xlabel("Section 301 Tariff Rate (%)", fontsize=10)
    plt.ylabel("Duty as % of Total Landed Cost", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig("assets/tariff_sensitivity_analysis.png", dpi=300)
    print("Saved: assets/tariff_sensitivity_analysis.png")


def run_fuel_switching_analysis():
    """
    Simulate carrier competition under volatile fuel surcharges (10% to 35%)
    for a time-tolerant order (SLA <= 8 days).
    """
    fuel_rates = np.linspace(0.10, 0.35, 26)
    duty_fixed = 810.0  # 1500 USD * 7.2 * 7.5%
    
    # Base freights for standard 12kg shipment
    base_dhl = 4149.0
    base_fdx = 3580.0
    base_ups = 2950.0
    
    dhl_costs = [base_dhl * (1 + f) + duty_fixed for f in fuel_rates]
    fdx_costs = [base_fdx * (1 + f) + duty_fixed for f in fuel_rates]
    ups_costs = [base_ups * (1 + f) + duty_fixed for f in fuel_rates]
    
    plt.figure(figsize=(8, 5))
    plt.plot(fuel_rates * 100, dhl_costs, label="DHL Express (Fastest, High Cost)", color="#d62728", linewidth=2)
    plt.plot(fuel_rates * 100, fdx_costs, label="FedEx Economy (Balanced)", color="#2ca02c", linewidth=2)
    plt.plot(fuel_rates * 100, ups_costs, label="UPS / Dedicated Air (Cost Leader)", color="#1f77b4", linewidth=2)
    
    plt.title("Carrier Total Cost Dynamic under Fuel Volatility (SLA <= 8 Days)", fontsize=12, fontweight="bold")
    plt.xlabel("Fuel Surcharge Rate (%)", fontsize=10)
    plt.ylabel("Total Landed Cost (RMB)", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig("assets/fuel_volatility_analysis.png", dpi=300)
    print("Saved: assets/fuel_volatility_analysis.png")


if __name__ == "__main__":
    print("Executing sensitivity simulations...")
    run_tariff_sensitivity()
    run_fuel_switching_analysis()
    print("All sensitivity models executed and charts generated successfully.")