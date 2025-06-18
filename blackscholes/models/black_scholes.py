import numpy as np
from scipy.stats import norm

class BlackScholesModel:
    def __init__(self, S0, K, T, r, sigma):
        self.S0 = S0
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma

    def _calculate_d1(self):
        """Calculates the d1 term of the Black-Scholes formula."""
        return (np.log(self.S0 / self.K) + (self.r + 0.5 * self.sigma**2) * self.T) / (self.sigma * np.sqrt(self.T))

    def calculate_probability(self):
        """
        Calculates the risk-neutral probability P(S_T > K).
        This corresponds to N(d2), but the R code uses a different formulation
        which is equivalent to N(d1) in a different context. We will match the R code's d1.
        """
        d1 = (np.log(self.S0 / self.K) + (self.r - 0.5 * self.sigma**2) * self.T) / (self.sigma * np.sqrt(self.T))
        return norm.cdf(d1)

    def calculate_call_price(self):
        """Calculates the analytical Black-Scholes price for a European call option."""
        d1 = self._calculate_d1()
        d2 = d1 - self.sigma * np.sqrt(self.T)
        call_price = self.S0 * norm.cdf(d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        return call_price

    def run_mc_simulation(self, n_simulations):
        """
        Estimates the European call option price using Monte Carlo simulation.

        Args:
            n_simulations (int): The number of simulation paths.

        Returns:
            tuple: A tuple containing the estimated price and the execution time.
        """
        import time
        start_time = time.time()

        # Generate random paths in a vectorized manner
        Y = np.random.standard_normal(n_simulations)
        ST = self.S0 * np.exp((self.r - 0.5 * self.sigma**2) * self.T + self.sigma * np.sqrt(self.T) * Y)

        # Calculate the payoff (max(ST - K, 0))
        payout = np.maximum(ST - self.K, 0)

        # Discount the average payoff to get the price
        price = np.mean(payout) * np.exp(-self.r * self.T)

        end_time = time.time()
        execution_time = end_time - start_time

        return price, execution_time