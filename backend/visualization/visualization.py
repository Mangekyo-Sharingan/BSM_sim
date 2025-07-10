import matplotlib.pyplot as plt

def plot_sensitivity(x_values, y_values, title, xlabel, ylabel):
    """
    Generic plotting function for sensitivity analysis.
    
    Args:
        x_values (array-like): Values for the x-axis
        y_values (array-like): Values for the y-axis
        title (str): Plot title
        xlabel (str): Label for the x-axis
        ylabel (str): Label for the y-axis
    """
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, lw=2, color="blue")
    plt.title(title, fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True)
    plt.show()