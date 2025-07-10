import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os
from tkinterdnd2 import DND_FILES, TkinterDnD
import sv_ttk

# --- Adapted Imports (ensure your file structure matches) ---
from backend.models.black_scholes import BlackScholesModel
from backend.models.DCF import DiscountedCashFlowModel
from backend.utils.config import DEFAULT_PARAMS, MC_SIMULATION_SIZES, SIGMA_RANGE, K_RANGE
from backend.utils.DataProcessor import DCFDataManager


class FinanceDashboard:
    def __init__(self, master):
        self.master = master
        master.title("Fintech & Stat Model Dashboard")
        master.geometry("1100x700")

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.analytical_tab = ttk.Frame(self.notebook)
        self.mc_tab = ttk.Frame(self.notebook)
        self.dcf_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.analytical_tab, text='Black-Scholes Plots')
        self.notebook.add(self.mc_tab, text='Monte Carlo Simulation')
        self.notebook.add(self.dcf_tab, text='DCF Valuation')

        self.create_analytical_tab(self.analytical_tab)
        self.create_mc_tab(self.mc_tab)
        self.create_dcf_tab(self.dcf_tab)

        self.dcf_data_manager = DCFDataManager()

    def create_analytical_tab(self, parent):
        left_pane = ttk.Frame(parent, width=350)
        left_pane.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10, expand=False)
        left_pane.pack_propagate(False)
        right_pane = ttk.Frame(parent)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=10)
        controls_frame = ttk.LabelFrame(left_pane, text="Model Parameters", padding="10")
        controls_frame.pack(fill=tk.X)
        self.params = {}
        for i, (name, value) in enumerate(DEFAULT_PARAMS.items()):
            ttk.Label(controls_frame, text=f"{name}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            self.params[name] = tk.DoubleVar(value=value)
            ttk.Entry(controls_frame, textvariable=self.params[name], width=15).grid(row=i, column=1, sticky=tk.EW,
                                                                                     padx=5, pady=5)
        controls_frame.columnconfigure(1, weight=1)
        actions_frame = ttk.LabelFrame(left_pane, text="Actions", padding="10")
        actions_frame.pack(fill=tk.X, pady=10)
        ttk.Button(actions_frame, text="Calculate Analytical Price", command=self.run_analytical_calc).pack(fill=tk.X,
                                                                                                            pady=2)
        ttk.Button(actions_frame, text="Plot Price vs. Sigma",
                   command=lambda: self.plot_sensitivity('sigma_price')).pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="Plot Price vs. Strike (K)",
                   command=lambda: self.plot_sensitivity('k_price')).pack(fill=tk.X, pady=2)
        ttk.Button(actions_frame, text="Plot Probability vs. Sigma",
                   command=lambda: self.plot_sensitivity('sigma_prob')).pack(fill=tk.X, pady=2)
        results_frame = ttk.LabelFrame(left_pane, text="Analytical Results", padding="10")
        results_frame.pack(fill=tk.X)
        self.result_prob = tk.StringVar()
        self.result_price = tk.StringVar()
        ttk.Label(results_frame, text="P[S_T > K]:").pack(anchor="w")
        ttk.Label(results_frame, textvariable=self.result_prob, font=("Courier", 10)).pack(anchor="w", pady=(0, 5))
        ttk.Label(results_frame, text="Call Price:").pack(anchor="w")
        ttk.Label(results_frame, textvariable=self.result_price, font=("Courier", 10)).pack(anchor="w")
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_pane)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.ax.set_title("Select a plot to display")
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        self.canvas.draw()

    def create_mc_tab(self, parent):
        controls_pane = ttk.Frame(parent, width=350)
        controls_pane.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10, expand=False)
        controls_pane.pack_propagate(False)
        results_pane = ttk.Frame(parent)
        results_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=10)
        sim_size_frame = ttk.LabelFrame(controls_pane, text="Select Simulation Sizes", padding="10")
        sim_size_frame.pack(fill=tk.X)
        self.mc_sim_vars = {}
        for size in MC_SIMULATION_SIZES:
            self.mc_sim_vars[size] = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(sim_size_frame, text=f"{size:,}", variable=self.mc_sim_vars[size])
            cb.pack(anchor='w', padx=5)
        ttk.Separator(sim_size_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(sim_size_frame, text="Custom Sizes (comma-separated):").pack(anchor='w', padx=5)
        self.custom_sizes_var = tk.StringVar()
        ttk.Entry(sim_size_frame, textvariable=self.custom_sizes_var).pack(fill='x', padx=5, pady=(0, 5))
        ttk.Button(controls_pane, text="Run Monte Carlo Simulation", command=self.run_mc_simulation).pack(fill=tk.X,
                                                                                                          pady=20)
        self.mc_table = ttk.Treeview(results_pane, columns=("n", "mc_price", "deviation_pct", "time"), show='headings')
        self.mc_table.heading("n", text="Simulations (n)")
        self.mc_table.heading("mc_price", text="MC Price")
        self.mc_table.heading("deviation_pct", text="Deviation (%)")
        self.mc_table.heading("time", text="Time (s)")
        self.mc_table.pack(fill=tk.BOTH, expand=True)

    def create_dcf_tab(self, parent):
        controls_pane = ttk.Frame(parent, width=400)
        controls_pane.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10, expand=False)
        controls_pane.pack_propagate(False)
        results_pane = ttk.Frame(parent)
        results_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=10)
        input_frame = ttk.LabelFrame(controls_pane, text="Data Input", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        yahoo_frame = ttk.Frame(input_frame)
        yahoo_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(yahoo_frame, text="Yahoo Finance Ticker:").pack(anchor='w')
        ticker_frame = ttk.Frame(yahoo_frame)
        ticker_frame.pack(fill=tk.X, pady=(2, 5))
        self.ticker_var = tk.StringVar(value="AAPL")
        ttk.Entry(ticker_frame, textvariable=self.ticker_var, width=10).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(ticker_frame, text="Fetch Data", command=self.fetch_yahoo_data).pack(side=tk.LEFT)
        ttk.Separator(input_frame, orient='horizontal').pack(fill='x', pady=10)
        file_frame = ttk.LabelFrame(input_frame, text="File Import", padding="5")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        self.drop_label = ttk.Label(file_frame, text="Drag & Drop CSV/Excel file here\nor click to browse",
                                    padding=(10, 30), relief='sunken', anchor=tk.CENTER, justify=tk.CENTER)
        self.drop_label.pack(fill=tk.X, pady=(0, 5))
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.on_file_drop)
        self.drop_label.bind('<Button-1>', self.browse_file)
        template_frame = ttk.Frame(file_frame)
        template_frame.pack(fill=tk.X)
        ttk.Button(template_frame, text="Generate CSV Template", command=lambda: self.generate_template('csv')).pack(
            side=tk.LEFT, padx=(0, 5))
        ttk.Button(template_frame, text="Generate Excel Template", command=lambda: self.generate_template('xlsx')).pack(
            side=tk.LEFT)
        params_frame = ttk.LabelFrame(controls_pane, text="DCF Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 10))
        self.dcf_params = {}
        dcf_param_names = {'enterprise_value': 'Enterprise Value (M)', 'debt': 'Total Debt (M)',
                           'cash': 'Cash & Equivalents (M)', 'shares_outstanding': 'Shares Outstanding (M)',
                           'last_fcf': 'Last FCF (M)', 'growth_rate': 'FCF Growth Rate', 'wacc': 'WACC',
                           'terminal_growth_rate': 'Terminal Growth Rate'}
        default_values = {'enterprise_value': 1000.0, 'debt': 200.0, 'cash': 50.0, 'shares_outstanding': 100.0,
                          'last_fcf': 60.0, 'growth_rate': 0.05, 'wacc': 0.08, 'terminal_growth_rate': 0.02}
        for i, (param, display_name) in enumerate(dcf_param_names.items()):
            ttk.Label(params_frame, text=f"{display_name}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            self.dcf_params[param] = tk.DoubleVar(value=default_values[param])
            entry = ttk.Entry(params_frame, textvariable=self.dcf_params[param], width=15)
            entry.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2)
        params_frame.columnconfigure(1, weight=1)
        analysis_frame = ttk.LabelFrame(controls_pane, text="Analysis", padding="10")
        analysis_frame.pack(fill=tk.X)
        self.projection_years_var = tk.IntVar(value=5)
        ttk.Label(analysis_frame, text="Projection Years:").pack(anchor='w')
        ttk.Scale(analysis_frame, from_=3, to=10, variable=self.projection_years_var, orient=tk.HORIZONTAL,
                  command=lambda s: self.projection_years_var.set(int(float(s)))).pack(fill=tk.X, pady=(0, 5))
        ttk.Label(analysis_frame, textvariable=self.projection_years_var).pack(anchor='w', pady=(0, 10))
        ttk.Button(analysis_frame, text="Calculate DCF", command=self.calculate_dcf).pack(fill=tk.X, pady=5)
        results_frame = ttk.LabelFrame(results_pane, text="DCF Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        self.results_text = tk.Text(results_frame, height=15, font=('Courier', 10), wrap='word')
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        table_frame = ttk.LabelFrame(results_pane, text="Cash Flow Projections", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.cf_table = ttk.Treeview(table_frame, columns=("year", "fcf", "pv_fcf"), show='headings', height=8)
        self.cf_table.heading("year", text="Year");
        self.cf_table.heading("fcf", text="Projected FCF");
        self.cf_table.heading("pv_fcf", text="Present Value")
        self.cf_table.column("year", width=80, anchor='center');
        self.cf_table.column("fcf", width=120, anchor='e');
        self.cf_table.column("pv_fcf", width=120, anchor='e')
        self.cf_table.pack(fill=tk.BOTH, expand=True)

    def run_analytical_calc(self):
        try:
            params = self._get_current_params()
            model = BlackScholesModel(**params)
            probability = model.calculate_probability()
            call_price = model.calculate_call_price()
            self.result_prob.set(f"{probability:.6f}")
            self.result_price.set(f"{call_price:.6f}")
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error in calculation:\n{str(e)}")
            self.result_prob.set("Error")
            self.result_price.set("Error")

    def _get_current_params(self):
        return {name: var.get() for name, var in self.params.items()}

    def run_mc_simulation(self):
        selected_sizes = {size for size, var in self.mc_sim_vars.items() if var.get()}
        custom_sizes_str = self.custom_sizes_var.get()
        if custom_sizes_str:
            try:
                custom_sizes = [int(x.strip()) for x in custom_sizes_str.split(',') if x.strip()]
                selected_sizes.update(custom_sizes)
            except ValueError:
                messagebox.showerror("Invalid Input", "Custom sizes must be integers separated by commas.")
                return
        if not selected_sizes:
            messagebox.showwarning("No Selection", "Please select or enter at least one simulation size.")
            return
        for i in self.mc_table.get_children(): self.mc_table.delete(i)
        try:
            params = self._get_current_params()
            mc_model = BlackScholesModel(**params)
            analytical_price = mc_model.calculate_call_price()
            for n in sorted(list(selected_sizes)):
                mc_price, exec_time = mc_model.run_mc_simulation(n)
                if analytical_price != 0:
                    deviation_pct = ((mc_price - analytical_price) / analytical_price) * 100
                    deviation_str = f"{deviation_pct:+.2f}%"
                else:
                    deviation_str = "N/A"
                self.mc_table.insert("", "end", values=(f"{n:,}", f"{mc_price:.6f}", deviation_str, f"{exec_time:.4f}"))
        except Exception as e:
            self.mc_table.insert("", "end", values=("Error", str(e), "", ""))

    def plot_sensitivity(self, plot_type):
        self.notebook.select(self.analytical_tab)
        self.ax.clear()
        try:
            params = self._get_current_params()
            title, xlabel, ylabel = "", "", ""
            x_values, y_values = None, None
            if plot_type == 'sigma_price':
                sigma_range = np.arange(*SIGMA_RANGE['price'])
                price_model = BlackScholesModel(S0=params['S0'], K=params['K'], T=params['T'], r=params['r'],
                                                sigma=sigma_range)
                x_values, y_values = sigma_range, price_model.calculate_call_price()
                title, xlabel, ylabel = "Call Price vs. Volatility", "Volatility (σ)", "Call Price"
            elif plot_type == 'k_price':
                k_range = np.arange(*K_RANGE)
                price_model = BlackScholesModel(S0=params['S0'], K=k_range, T=params['T'], r=params['r'],
                                                sigma=params['sigma'])
                x_values, y_values = k_range, price_model.calculate_call_price()
                title, xlabel, ylabel = "Call Price vs. Strike Price", "Strike Price (K)", "Call Price"
            elif plot_type == 'sigma_prob':
                sigma_range = np.arange(*SIGMA_RANGE['probability'])
                prob_model = BlackScholesModel(S0=params['S0'], K=params['K'], T=params['T'], r=params['r'],
                                               sigma=sigma_range)
                x_values, y_values = sigma_range, prob_model.calculate_probability()
                title, xlabel, ylabel = "P[ST > K] vs. Volatility", "Volatility (σ)", "P[ST > K]"
            self.ax.plot(x_values, y_values, lw=2, color="#007bff")
            self.ax.set_title(title, fontsize=14)
            self.ax.set_xlabel(xlabel, fontsize=10)
            self.ax.set_ylabel(ylabel, fontsize=10)
            self.ax.grid(True, which='both', linestyle='--', linewidth=0.5)
            self.canvas.draw()
        except Exception as e:
            self.ax.text(0.5, 0.5, f"Error generating plot:\n{e}", ha='center', va='center')
            self.canvas.draw()

    def fetch_yahoo_data(self):
        ticker = self.ticker_var.get().strip().upper()
        if not ticker:
            messagebox.showerror("Error", "Please enter a valid ticker symbol")
            return
        try:
            assumptions = {'growth_rate': self.dcf_params['growth_rate'].get(), 'wacc': self.dcf_params['wacc'].get(),
                           'terminal_growth_rate': self.dcf_params['terminal_growth_rate'].get()}
            params = self.dcf_data_manager.load_from_yahoo(ticker, assumptions)
            for param, value in params.items():
                if param in self.dcf_params:
                    self.dcf_params[param].set(value)
            messagebox.showinfo("Success", f"Data for {ticker} loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data for {ticker}:\n{str(e)}")

    def on_file_drop(self, event):
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        if os.path.exists(file_path):
            self.load_file_data(file_path)
        else:
            messagebox.showerror("Error", f"Invalid file path: {file_path}")

    def browse_file(self, event=None):
        file_path = filedialog.askopenfilename(title="Select DCF Parameters File",
                                               filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"),
                                                          ("All files", "*.*")])
        if file_path:
            self.load_file_data(file_path)

    def load_file_data(self, file_path):
        try:
            self.drop_label.config(text=f"Loading: {os.path.basename(file_path)}")
            self.master.update()
            params = self.dcf_data_manager.load_from_file(file_path)
            for param, value in params.items():
                if param in self.dcf_params:
                    self.dcf_params[param].set(value)
            self.drop_label.config(text=f"Loaded: {os.path.basename(file_path)}")
            messagebox.showinfo("Success", f"Data loaded from {os.path.basename(file_path)}")
        except Exception as e:
            self.drop_label.config(text="Drag & Drop CSV/Excel file here\nor click to browse")
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

    def generate_template(self, file_type):
        try:
            file_path = filedialog.asksaveasfilename(title=f"Save {file_type.upper()} Template",
                                                     defaultextension=f'.{file_type}',
                                                     filetypes=[(f"{file_type.upper()} files", f"*.{file_type}")])
            if file_path:
                self.dcf_data_manager.create_template_file(file_path, file_type)
                messagebox.showinfo("Success", f"Template saved to {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create template:\n{str(e)}")

    def calculate_dcf(self):
        """Calculate DCF valuation."""
        try:
            params = {name: var.get() for name, var in self.dcf_params.items()}
            # --- THIS IS THE FIX ---
            # The variable is named self.projection_years_var, not self.projection_years
            years = self.projection_years_var.get()

            dcf_model = DiscountedCashFlowModel(**params)
            intrinsic_value = dcf_model.calculate_intrinsic_value(years)
            current_implied_price = dcf_model.calculate_implied_share_price()
            projected_fcf = dcf_model.project_free_cash_flows(years)
            final_fcf = projected_fcf[-1]
            terminal_value = dcf_model.calculate_terminal_value(final_fcf)
            intrinsic_enterprise_value = dcf_model.calculate_present_value(projected_fcf, terminal_value)

            self.display_dcf_results(dcf_model, intrinsic_value, current_implied_price, intrinsic_enterprise_value,
                                     terminal_value, years)
            self.update_cf_table(projected_fcf, dcf_model.wacc, terminal_value, years)
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error in DCF calculation:\n{str(e)}")

    def display_dcf_results(self, dcf_model, intrinsic_value, current_price, enterprise_value, terminal_value, years):
        self.results_text.delete(1.0, tk.END)
        results = f"""
=== DCF VALUATION RESULTS ===

INPUT PARAMETERS:
Enterprise Value:        ${dcf_model.enterprise_value:,.0f}M
Total Debt:             ${dcf_model.debt:,.0f}M
Cash & Equivalents:     ${dcf_model.cash:,.0f}M
Shares Outstanding:     {dcf_model.shares_outstanding:,.0f}M
Last Year FCF:          ${dcf_model.last_fcf:,.0f}M
FCF Growth Rate:        {dcf_model.growth_rate:.2%}
WACC:                   {dcf_model.wacc:.2%}
Terminal Growth:        {dcf_model.terminal_growth_rate:.2%}
Projection Years:       {years}

CALCULATED VALUES:
Intrinsic Enterprise Value: ${enterprise_value:,.0f}M
Terminal Value:            ${terminal_value:,.0f}M
Intrinsic Equity Value:    ${enterprise_value - dcf_model.debt + dcf_model.cash:,.0f}M

SHARE PRICE ANALYSIS:
Current Implied Price:     ${current_price:.2f}
Intrinsic Value per Share: ${intrinsic_value:.2f}
Upside/Downside:          {((intrinsic_value - current_price) / current_price * 100):+.1f}%

VALUATION SUMMARY:
{'UNDERVALUED' if intrinsic_value > current_price else 'OVERVALUED'} by ${abs(intrinsic_value - current_price):.2f} per share
        """
        self.results_text.insert(tk.END, results)

    def update_cf_table(self, projected_fcf, wacc, terminal_value, years):
        for item in self.cf_table.get_children():
            self.cf_table.delete(item)
        for i, fcf in enumerate(projected_fcf):
            year = i + 1
            pv_fcf = fcf / ((1 + wacc) ** year)
            self.cf_table.insert("", "end", values=(f"Year {year}", f"${fcf:.1f}M", f"${pv_fcf:.1f}M"))
        pv_terminal = terminal_value / ((1 + wacc) ** years)
        self.cf_table.insert("", "end", values=("Terminal", f"${terminal_value:.1f}M", f"${pv_terminal:.1f}M"))


def main():
    root = TkinterDnD.Tk()
    root.title("Fintech & Stat Model Dashboard")
    sv_ttk.set_theme("dark")
    app = FinanceDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()