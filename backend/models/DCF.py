import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, Union, Optional
# Correct the import path if your file structure is different
from backend.utils.DataProcessor import DCFDataManager

class DiscountedCashFlowModel:
    def __init__(self, enterprise_value, debt, cash, shares_outstanding, last_fcf, growth_rate, wacc,
                 terminal_growth_rate):
        self.enterprise_value = enterprise_value
        self.debt = debt
        self.cash = cash
        self.shares_outstanding = shares_outstanding
        self.last_fcf = last_fcf
        self.growth_rate = growth_rate
        self.wacc = wacc
        self.terminal_growth_rate = terminal_growth_rate

    def calculate_equity_value(self):
        return self.enterprise_value - self.debt + self.cash

    def calculate_implied_share_price(self):
        equity_value = self.calculate_equity_value()
        # Avoid division by zero
        return equity_value / self.shares_outstanding if self.shares_outstanding else 0

    def project_free_cash_flows(self, years=5):
        projected_fcf = []
        for year in range(1, years + 1):
            fcf = self.last_fcf * (1 + self.growth_rate) ** year
            projected_fcf.append(fcf)
        return projected_fcf

    def calculate_terminal_value(self, final_fcf):
        # Avoid division by zero if WACC equals terminal growth rate
        denominator = self.wacc - self.terminal_growth_rate
        if denominator == 0:
            return 0
        return (final_fcf * (1 + self.terminal_growth_rate)) / denominator

    def calculate_present_value(self, cash_flows, terminal_value):
        pv_fcf = sum(fcf / ((1 + self.wacc) ** (i + 1)) for i, fcf in enumerate(cash_flows))
        pv_terminal_value = terminal_value / ((1 + self.wacc) ** len(cash_flows))
        return pv_fcf + pv_terminal_value

    def calculate_intrinsic_value(self, years=5):
        projected_fcf = self.project_free_cash_flows(years)
        if not projected_fcf:
            return 0
        final_fcf = projected_fcf[-1]
        terminal_value = self.calculate_terminal_value(final_fcf)
        intrinsic_enterprise_value = self.calculate_present_value(projected_fcf, terminal_value)
        intrinsic_equity_value = intrinsic_enterprise_value - self.debt + self.cash
        # Avoid division by zero
        return intrinsic_equity_value / self.shares_outstanding if self.shares_outstanding else 0

    # --- FIXED: Classmethods are now correctly placed inside the class ---
    @classmethod
    def from_yahoo_finance(cls, ticker: str, assumptions: Dict[str, float]):
        """Create DCF model using Yahoo Finance data."""
        data_manager = DCFDataManager()
        params = data_manager.load_from_yahoo(ticker, assumptions)
        return cls(**params)

    @classmethod
    def from_file(cls, file_path: str):
        """Create DCF model from CSV or Excel file."""
        data_manager = DCFDataManager()
        params = data_manager.load_from_file(file_path)
        return cls(**params)

# The __main__ block remains for testing purposes but is not used by the GUI
if __name__ == '__main__':
    # ... (Your example usage code remains unchanged)
    pass