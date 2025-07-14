import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, Union, Optional


class YahooFinanceDataProcessor:
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)

    def get_financial_data(self) -> Dict[str, Union[float, str]]:
        try:
            #get company info
            income_stmt = self.stock.financials
            balance_sheet = self.stock.balance_sheet
            cash_flow = self.stock.cashflow
            info = self.stock.info

            #key metrics
            data = {
                'shares_outstanding': info.get('sharesOutstanding', 0) / 1e6,  # Convert to millions
                'market_cap': info.get('marketCap', 0) / 1e6,  # Convert to millions
                'enterprise_value': info.get('enterpriseValue', 0) / 1e6 if info.get('enterpriseValue') else 0,
                'debt': self._get_latest_value(balance_sheet, 'Total Debt') / 1e6,
                'cash': self._get_latest_value(balance_sheet, 'Cash And Cash Equivalents') / 1e6,
                'last_fcf': self._get_latest_value(cash_flow, 'Free Cash Flow') / 1e6,
                'revenue': self._get_latest_value(income_stmt, 'Total Revenue') / 1e6,
                'industry': info.get('industry', 'N/A'),  # Get the industry
            }
            if data['enterprise_value'] == 0 and data['market_cap'] > 0:
                data['enterprise_value'] = data['market_cap'] + data['debt'] - data['cash']
            return data

        except Exception as e:
            raise ValueError(f"Error fetching data for {self.ticker}: {str(e)}")

    def _get_latest_value(self, df: pd.DataFrame, key: str) -> float:
        try:
            #try match first
            if key in df.index:
                return float(df.loc[key].iloc[0])

            #try alternative naming
            alternatives = self._get_alternative_keys(key)
            for alt_key in alternatives:
                if alt_key in df.index:
                    return float(df.loc[alt_key].iloc[0])

            return 0.0
        except (IndexError, KeyError, TypeError):
            return 0.0

    def _get_alternative_keys(self, key: str) -> list:
        alternatives = {
            'Total Debt': ['Total Debt', 'Long Term Debt', 'Total Liabilities Net Minority Interest'],
            'Cash And Cash Equivalents': ['Cash', 'Cash And Cash Equivalents', 'Cash and Short Term Investments'],
            'Free Cash Flow': ['Free Cash Flow', 'Operating Cash Flow'],
            'Total Revenue': ['Total Revenue', 'Revenue', 'Net Sales']
        }
        return alternatives.get(key, [key])


class FileDataProcessor:
    @staticmethod
    def load_from_file(file_path: str) -> Dict[str, Union[float, str]]:
        try:
            # Determine file type and read accordingly
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format. Please use CSV or Excel files.")
            required_columns = {
                'enterprise_value': ['enterprise_value', 'Enterprise Value', 'EV'],
                'debt': ['debt', 'total_debt', 'Total Debt', 'Debt'],
                'cash': ['cash', 'Cash', 'Cash And Cash Equivalents'],
                'shares_outstanding': ['shares_outstanding', 'Shares Outstanding', 'shares'],
                'last_fcf': ['last_fcf', 'FCF', 'Free Cash Flow', 'fcf'],
                'growth_rate': ['growth_rate', 'Growth Rate', 'FCF Growth'],
                'wacc': ['wacc', 'WACC', 'discount_rate'],
                'terminal_growth_rate': ['terminal_growth_rate', 'Terminal Growth', 'terminal_growth'],
                'industry': ['industry', 'Industry']
            }

            #Extract data
            data = {}
            for param, possible_cols in required_columns.items():
                value = FileDataProcessor._find_value_in_df(df, possible_cols)
                if value is not None:
                    try:
                        data[param] = float(value)
                    except (ValueError, TypeError):
                        data[param] = value
                elif param != 'industry': # Industry is optional from file
                    raise ValueError(f"Could not find column for parameter: {param}")

            return data

        except Exception as e:
            raise ValueError(f"Error loading file {file_path}: {str(e)}")

    @staticmethod
    def _find_value_in_df(df: pd.DataFrame, possible_columns: list) -> Optional[Union[float, str]]:
        """Find value in DataFrame using multiple possible column names."""
        # Check exact matches first
        for col in possible_columns:
            if col in df.columns:
                return df[col].iloc[0]

        # Check case-insensitive matches
        df_cols_lower = [c.lower() for c in df.columns]
        for col in possible_columns:
            col_lower = col.lower()
            if col_lower in df_cols_lower:
                idx = df_cols_lower.index(col_lower)
                actual_col = df.columns[idx]
                return df[actual_col].iloc[0]

        return None


class DCFDataManager:
    def __init__(self):
        self.yahoo_processor = None

    def load_from_yahoo(self, ticker: str, assumptions: Dict[str, float]) -> Dict[str, Union[float, str]]:
        """Load financial data from Yahoo Finance and combine with assumptions."""
        self.yahoo_processor = YahooFinanceDataProcessor(ticker)
        financial_data = self.yahoo_processor.get_financial_data()

        # Combine with user assumptions
        dcf_params = {**financial_data, **assumptions}

        # Validate required parameters (industry is not required here as it's fetched)
        required_params = ['enterprise_value', 'debt', 'cash', 'shares_outstanding',
                           'last_fcf', 'growth_rate', 'wacc', 'terminal_growth_rate']

        missing_params = [p for p in required_params if p not in dcf_params or dcf_params[p] is None]
        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")

        return dcf_params

    def load_from_file(self, file_path: str) -> Dict[str, Union[float, str]]:
        return FileDataProcessor.load_from_file(file_path)

    def create_template_file(self, file_path: str, file_type: str = 'csv'):
        template_data = {
            'enterprise_value': [1000.0],
            'debt': [200.0],
            'cash': [50.0],
            'shares_outstanding': [100.0],
            'last_fcf': [60.0],
            'growth_rate': [0.05],
            'wacc': [0.08],
            'terminal_growth_rate': [0.02],
            'industry': ['Technology'] # Added industry to template
        }

        df = pd.DataFrame(template_data)

        if file_type.lower() == 'csv':
            df.to_csv(file_path, index=False)
        elif file_type.lower() in ['xlsx', 'excel']:
            df.to_excel(file_path, index=False)
        else:
            raise ValueError("Supported file types: 'csv', 'xlsx', 'excel'")