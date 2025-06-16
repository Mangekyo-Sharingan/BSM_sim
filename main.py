"""
Main script for running Black-Scholes Model simulations and visualizations.
"""

import numpy as np
import pandas as pd
import time

from blackscholes.models.black_scholes import BlackScholesModel
from blackscholes.config import DEFAULT_PARAMS, MC_SIMULATION_SIZES, SIGMA_RANGE, K_RANGE
from blackscholes.visualization import plot_sensitivity

def main():
    """Main function to run Black-Scholes Model simulations and visualizations."""
    # Extract default parameters
    S0_base = DEFAULT_PARAMS['S0']
    K_base = DEFAULT_PARAMS['K']
    r_base = DEFAULT_PARAMS['r']
    sigma_base = DEFAULT_PARAMS['sigma']
    T_base = DEFAULT_PARAMS['T']

    # --- Section 2: Black-Scholes Analytical Calculations ---
    print("--- Black-Scholes Analytical Model ---")

    # 2.1 & 2.4: Calculate single probability and price
    bsm_model = BlackScholesModel(S0=S0_base, K=K_base, T=T_base, r=r_base, sigma=sigma_base)

    p_ex = bsm_model.calculate_probability()
    print(f"P[S_T > K] = {p_ex:.6f}")

    call_price_analytical = bsm_model.calculate_call_price()
    print(f"The analytical Black-Scholes call price is: {call_price_analytical:.6f}\n")

    # 2.3: Plot P[ST > K] as a function of sigma
    sigma_range = np.arange(*SIGMA_RANGE['probability'])
    prob_model = BlackScholesModel(S0=S0_base, K=K_base, T=T_base, r=r_base, sigma=sigma_range)
    probs = prob_model.calculate_probability()
    plot_sensitivity(sigma_range, probs, "P[ST > K] as a function of sigma", "Volatility (sigma)", "P[ST > K]")

    # 2.5: Plot Call price as a function of sigma
    sigma_range_2 = np.arange(*SIGMA_RANGE['price'])
    price_model_sigma = BlackScholesModel(S0=S0_base, K=K_base, T=T_base, r=r_base, sigma=sigma_range_2)
    call_prices_sigma = price_model_sigma.calculate_call_price()
    plot_sensitivity(sigma_range_2, call_prices_sigma, "Call Option Price at Varying Sigma", "Volatility (sigma)", "Call Option Price")

    # 2.6: Plot Call price as a function of K
    K_range_values = np.arange(*K_RANGE)
    price_model_k = BlackScholesModel(S0=S0_base, K=K_range_values, T=T_base, r=r_base, sigma=sigma_base)
    call_prices_k = price_model_k.calculate_call_price()
    plot_sensitivity(K_range_values, call_prices_k, "Call Option Price at Varying Strike Price (K)", "Strike Price (K)", "Call Option Price")

    # --- Section 3: Monte Carlo Simulation ---
    print("\n--- Monte Carlo Simulation Results ---")

    # 3.1 & 3.2: Vectorized MC simulation with timing
    mc_model = BlackScholesModel(S0=S0_base, K=K_base, T=T_base, r=r_base, sigma=sigma_base)
    n_values = MC_SIMULATION_SIZES

    mc_results = []

    for n in n_values:
        mc_price, exec_time = mc_model.run_mc_simulation(n)
        mc_results.append({
            "n": f"{n:1.0e}", # Scientific notation for readability
            "MonteCarloPrice": mc_price,
            "TimeInSeconds": exec_time,
            "AnalyticalPrice": call_price_analytical
        })

    # Display results in a pandas DataFrame
    results_df = pd.DataFrame(mc_results)
    print(results_df.to_string(index=False))

if __name__ == "__main__":
    main()
