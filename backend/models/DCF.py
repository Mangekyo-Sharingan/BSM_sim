import numpy as np


class DiscountedCashFlowModel:
    """
    A class to perform a Discounted Cash Flow (DCF) analysis.

    This class encapsulates the logic for a DCF valuation, including projecting
    free cash flows, calculating terminal value, discounting those values back
    to the present, and ultimately deriving an intrinsic value per share.
    """

    def __init__(self, enterprise_value, debt, cash, shares_outstanding, last_fcf, growth_rate, wacc,
                 terminal_growth_rate):
        """
        Initializes the DCF model with the necessary parameters.

        Args:
            enterprise_value (float): The company's enterprise value.
            debt (float): The company's total debt.
            cash (float): The company's cash and cash equivalents.
            shares_outstanding (float): The number of shares outstanding.
            last_fcf (float): The most recent free cash flow.
            growth_rate (float): The projected growth rate for free cash flows.
            wacc (float): The Weighted Average Cost of Capital.
            terminal_growth_rate (float): The perpetual growth rate for the terminal value.
        """
        self.enterprise_value = enterprise_value
        self.debt = debt
        self.cash = cash
        self.shares_outstanding = shares_outstanding
        self.last_fcf = last_fcf
        self.growth_rate = growth_rate
        self.wacc = wacc
        self.terminal_growth_rate = terminal_growth_rate

    def calculate_equity_value(self):
        """
        Calculates the equity value of the company.

        Equity Value = Enterprise Value - Total Debt + Cash
        """
        return self.enterprise_value - self.debt + self.cash

    def calculate_implied_share_price(self):
        """
        Calculates the implied share price from the equity value.
        """
        equity_value = self.calculate_equity_value()
        return equity_value / self.shares_outstanding

    def project_free_cash_flows(self, years=5):
        """
        Projects future free cash flows for a given number of years.

        Args:
            years (int): The number of years to project.

        Returns:
            list: A list of projected free cash flows.
        """
        projected_fcf = []
        for year in range(1, years + 1):
            fcf = self.last_fcf * (1 + self.growth_rate) ** year
            projected_fcf.append(fcf)
        return projected_fcf

    def calculate_terminal_value(self, final_fcf):
        """
        Calculates the terminal value using the perpetuity growth model.

        Terminal Value = (Final Year FCF * (1 + Terminal Growth Rate)) / (WACC - Terminal Growth Rate)

        Args:
            final_fcf (float): The free cash flow of the final projected year.

        Returns:
            float: The calculated terminal value.
        """
        return (final_fcf * (1 + self.terminal_growth_rate)) / (self.wacc - self.terminal_growth_rate)

    def calculate_present_value(self, cash_flows, terminal_value):
        """
        Calculates the present value of future cash flows and the terminal value.

        Args:
            cash_flows (list): A list of projected future cash flows.
            terminal_value (float): The calculated terminal value.

        Returns:
            float: The total present value (intrinsic value).
        """
        pv_fcf = 0
        # Discount each projected free cash flow
        for i, fcf in enumerate(cash_flows):
            pv_fcf += fcf / ((1 + self.wacc) ** (i + 1))

        # Discount the terminal value
        pv_terminal_value = terminal_value / ((1 + self.wacc) ** len(cash_flows))

        # The enterprise value is the sum of the present values
        enterprise_value = pv_fcf + pv_terminal_value
        return enterprise_value

    def calculate_intrinsic_value(self, years=5):
        """
        Performs the full DCF analysis to find the intrinsic value per share.

        Args:
            years (int): The number of years for the projection period.

        Returns:
            float: The intrinsic value per share.
        """
        # 1. Project future free cash flows
        projected_fcf = self.project_free_cash_flows(years)
        final_fcf = projected_fcf[-1]

        # 2. Calculate the terminal value
        terminal_value = self.calculate_terminal_value(final_fcf)

        # 3. Calculate the present value of all future cash flows
        intrinsic_enterprise_value = self.calculate_present_value(projected_fcf, terminal_value)

        # 4. Calculate the intrinsic equity value
        intrinsic_equity_value = intrinsic_enterprise_value - self.debt + self.cash

        # 5. Calculate the intrinsic value per share
        intrinsic_value_per_share = intrinsic_equity_value / self.shares_outstanding

        return intrinsic_value_per_share


if __name__ == '__main__':
    # This is an example of how to use the DCF model class.
    # You would typically import the class into your main script.

    # --- INPUTS ---
    # These values would come from your financial data source (e.g., financial statements)
    enterprise_value = 1000  # In millions
    debt = 200  # In millions
    cash = 50  # In millions
    shares_outstanding = 100  # In millions
    last_fcf = 60  # In millions (Free Cash Flow for the last period)

    # --- ASSUMPTIONS ---
    # These are your assumptions about the company's future performance
    growth_rate = 0.05  # 5% annual growth rate in FCF
    wacc = 0.08  # 8% Weighted Average Cost of Capital
    terminal_growth_rate = 0.02  # 2% perpetual growth rate

    # --- ANALYSIS ---
    # Create an instance of the model
    dcf_model = DiscountedCashFlowModel(
        enterprise_value=enterprise_value,
        debt=debt,
        cash=cash,
        shares_outstanding=shares_outstanding,
        last_fcf=last_fcf,
        growth_rate=growth_rate,
        wacc=wacc,
        terminal_growth_rate=terminal_growth_rate
    )

    # Calculate the intrinsic value
    intrinsic_value = dcf_model.calculate_intrinsic_value(years=5)

    # --- OUTPUT ---
    print(f"--- DCF Model Inputs ---")
    print(f"Enterprise Value: ${enterprise_value:,.2f}M")
    print(f"Debt: ${debt:,.2f}M")
    print(f"Cash: ${cash:,.2f}M")
    print(f"Shares Outstanding: {shares_outstanding}M")
    print(f"Last Year's FCF: ${last_fcf:,.2f}M")
    print(f"FCF Growth Rate: {growth_rate:.2%}")
    print(f"WACC: {wacc:.2%}")
    print(f"Terminal Growth Rate: {terminal_growth_rate:.2%}")
    print("-" * 26)
    print(f"\nCalculated Intrinsic Value per Share: ${intrinsic_value:.2f}")

    # You can also access other calculations
    implied_share_price = dcf_model.calculate_implied_share_price()
    print(f"Current Implied Share Price (from EV): ${implied_share_price:.2f}")
