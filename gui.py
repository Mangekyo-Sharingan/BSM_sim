import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# --- NEW: Import for the dark theme ---
import sv_ttk

# --- Adapted Imports for your file structure ---
from backend.models.black_scholes import BlackScholesModel
from backend.utils.config import DEFAULT_PARAMS, MC_SIMULATION_SIZES, SIGMA_RANGE, K_RANGE


class BlackScholesGUI:
    def __init__(self, master):
        self.master = master
        master.title("Black-Scholes Model Dashboard")
        master.geometry("1100x700")

        # --- Main Tabbed Layout ---
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create and add tabs
        self.analytical_tab = ttk.Frame(self.notebook)
        self.mc_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.analytical_tab, text='Analytical & Plots')
        self.notebook.add(self.mc_tab, text='Monte Carlo Simulation')

        # Populate each tab
        self.create_analytical_tab(self.analytical_tab)
        self.create_mc_tab(self.mc_tab)

    def create_analytical_tab(self, parent):
        # This function remains the same as before
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

        # --- Matplotlib plot styling for dark theme ---
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_pane)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.ax.set_title("Select a plot to display")
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        self.canvas.draw()

    def create_mc_tab(self, parent):
        """Creates the content for the Monte Carlo Simulation tab."""
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

        # --- UPDATED: Custom simulation sizes input ---
        ttk.Separator(sim_size_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(sim_size_frame, text="Custom Sizes (comma-separated):").pack(anchor='w', padx=5)
        self.custom_sizes_var = tk.StringVar()
        ttk.Entry(sim_size_frame, textvariable=self.custom_sizes_var).pack(fill='x', padx=5, pady=(0, 5))

        ttk.Button(controls_pane, text="Run Monte Carlo Simulation", command=self.run_mc_simulation).pack(fill=tk.X,
                                                                                                          pady=20)

        self.mc_table = ttk.Treeview(results_pane, columns=("n", "mc_price", "analytical_price", "time"),
                                     show='headings')
        self.mc_table.heading("n", text="Simulations (n)")
        self.mc_table.heading("mc_price", text="MC Price")
        self.mc_table.heading("analytical_price", text="Analytical Price")
        self.mc_table.heading("time", text="Time (s)")
        self.mc_table.pack(fill=tk.BOTH, expand=True)

    def _get_current_params(self):
        return {key: var.get() for key, var in self.params.items()}

    def run_analytical_calc(self):
        self.notebook.select(self.analytical_tab)
        try:
            params = self._get_current_params()
            model = BlackScholesModel(**params)
            price = model.calculate_call_price()
            prob = model.calculate_probability()
            self.result_price.set(f"{price:.6f}")
            self.result_prob.set(f"{prob:.6f}")
        except Exception as e:
            self.result_price.set("Error")
            self.result_prob.set(str(e))

    def run_mc_simulation(self):
        """Runs the MC simulation for selected sizes, including multiple custom sizes."""
        selected_sizes = {size for size, var in self.mc_sim_vars.items() if var.get()}

        # --- UPDATED: Parse multiple custom sizes ---
        custom_sizes_str = self.custom_sizes_var.get()
        if custom_sizes_str:
            try:
                # Split by comma, strip whitespace, convert to int
                custom_vals = [int(val.strip()) for val in custom_sizes_str.split(',') if val.strip()]
                for val in custom_vals:
                    if val > 0:
                        selected_sizes.add(val)
                    else:
                        raise ValueError("Simulation size must be positive.")
            except ValueError:
                messagebox.showerror("Invalid Input",
                                     f"Please enter positive, comma-separated numbers only.\nInvalid value found in '{custom_sizes_str}'.")
                return

        if not selected_sizes:
            messagebox.showwarning("No Selection", "Please select or enter at least one simulation size.")
            return

        for i in self.mc_table.get_children():
            self.mc_table.delete(i)

        try:
            params = self._get_current_params()
            mc_model = BlackScholesModel(**params)
            analytical_price = mc_model.calculate_call_price()

            final_sizes = sorted(list(selected_sizes))
            for n in final_sizes:
                mc_price, exec_time = mc_model.run_mc_simulation(n)
                self.mc_table.insert("", "end", values=(f"{n:1.0e}", f"{mc_price:.6f}", f"{analytical_price:.6f}",
                                                        f"{exec_time:.4f}"))
                self.master.update_idletasks()
        except Exception as e:
            self.mc_table.insert("", "end", values=("Error", str(e), "", ""))

    def plot_sensitivity(self, plot_type):
        self.notebook.select(self.analytical_tab)
        self.ax.clear()

        try:
            params = self._get_current_params()
            title, xlabel, ylabel = "", "", ""
            x_values, y_values = None, None

            # Reusing plotting logic from before...
            if plot_type == 'sigma_price':
                x_values = np.arange(*SIGMA_RANGE['price'])
                model = BlackScholesModel(S0=params['S0'], K=params['K'], T=params['T'], r=params['r'], sigma=x_values)
                y_values = model.calculate_call_price()
                title, xlabel, ylabel = "Call Price vs. Volatility", "Volatility (sigma)", "Call Option Price"

            elif plot_type == 'k_price':
                x_values = np.arange(*K_RANGE)
                model = BlackScholesModel(S0=params['S0'], K=x_values, T=params['T'], r=params['r'],
                                          sigma=params['sigma'])
                y_values = model.calculate_call_price()
                title, xlabel, ylabel = "Call Price vs. Strike Price", "Strike Price (K)", "Call Option Price"

            elif plot_type == 'sigma_prob':
                x_values = np.arange(*SIGMA_RANGE['probability'])
                model = BlackScholesModel(S0=params['S0'], K=params['K'], T=params['T'], r=params['r'], sigma=x_values)
                y_values = model.calculate_probability()
                title, xlabel, ylabel = "P[ST > K] vs. Volatility", "Volatility (sigma)", "P[ST > K]"

            self.ax.plot(x_values, y_values, lw=2, color="#007bff")  # A nice blue for dark mode
            self.ax.set_title(title, fontsize=14)
            self.ax.set_xlabel(xlabel, fontsize=10)
            self.ax.set_ylabel(ylabel, fontsize=10)
            self.ax.grid(True, which='both', linestyle='--', linewidth=0.5)
            self.canvas.draw()

        except Exception as e:
            self.ax.text(0.5, 0.5, f"Error generating plot:\n{e}", ha='center', va='center')
            self.canvas.draw()


def main():
    root = tk.Tk()

    # --- NEW: Set the dark theme ---
    sv_ttk.set_theme("dark")

    app = BlackScholesGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()