"""
Configuration module for Black-Scholes Model default parameters.
"""

# Default parameters for Black-Scholes Model
DEFAULT_PARAMS = {
    'S0': 50.0,      # Initial stock price
    'K': 61.0,       # Strike price
    'T': 2.0,        # Time to maturity in years
    'r': 0.06,       # Risk-free interest rate
    'sigma': 0.24,   # Volatility
}

# Monte Carlo simulation parameters
MC_SIMULATION_SIZES = [int(10**i) for i in range(2, 8)]  # 1e2 to 1e7

# Sensitivity analysis ranges
SIGMA_RANGE = {
    'probability': (0.01, 1.0, 0.01),  # (start, stop, step)
    'price': (0.05, 0.81, 0.01),
}

K_RANGE = (20, 100.5, 0.5)  # (start, stop, step)