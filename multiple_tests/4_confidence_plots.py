import os
import json
import numpy as np
import matplotlib.pyplot as plt

# Base directory and settings
working_directory = os.getcwd()
base_dir = os.path.join(working_directory, 'iperf3_results')

# Distance from AP for each station
distances = [1, 8.14, 15.32, 22.517, 29.70, 36.87, 44.06, 51.24, 58.24, 65.62, 72.79]

# Function to load iperf3 results from a scheme directory for a specific test
def load_iperf3_results(test_path):
    throughput_values_tcp = []
    
    for i in range(1, 12):
        try:
            with open(f"{test_path}/tcp/sta{i}_iperf3.json", "r") as f:
                data = json.load(f)
                throughput_tcp = data['end']['sum_received']['bits_per_second'] / 1e6  # Convert to Mbps
                throughput_values_tcp.append(throughput_tcp)
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass

    return throughput_values_tcp

# Function to load and average iperf3 results from multiple test directories in a scheme
def load_and_average_iperf3_results(scheme_dir):
    throughput_values_tcp = []

    test_dirs = [d for d in os.listdir(scheme_dir) if d.startswith('test_')]
    for test_dir in test_dirs:
        test_path = os.path.join(scheme_dir, test_dir)
        tcp_throughput = load_iperf3_results(test_path)

        if tcp_throughput:
            throughput_values_tcp.append(tcp_throughput)

    # Calculate averages and standard deviations
    avg_throughput_values_tcp = np.mean(throughput_values_tcp, axis=0)
    std_throughput_values_tcp = np.std(throughput_values_tcp, axis=0)

    return avg_throughput_values_tcp, std_throughput_values_tcp, throughput_values_tcp

# Function to plot the mean with error bars and individual test lines for each scheme on the same plot
def plot_comparison_with_error_bars(x_values, schemes_data, ylabel, title, filename):
    plt.figure(figsize=(12, 8))

    for scheme, data in schemes_data.items():
        mean_values = data['mean']
        std_dev = data['std']
        color = data['color']
        individual_results = data['individual_results']

        # Plot individual test results in the background
        for result in individual_results:
            plt.plot(x_values, result, color=color, alpha=0.1)

        # Plot the mean line with error bars for pointwise confidence intervals
        plt.errorbar(x_values, mean_values, yerr=std_dev, fmt='o-', color=color, capsize=5, label=scheme)

    plt.xlabel('Distance from AP (meters)', fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    plt.title(title, fontsize=16)
    plt.grid(True)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend()
    plt.savefig(filename, bbox_inches='tight', format='pdf')
    plt.close()

# Define the colors for each scheme
scheme_colors = {'Baseline (No MAC Randomization)': 'b', 'Kernel Time-Based MAC Re-Randomization': 'g', 'AP-Initiated MAC Re-Randomization': 'r'}

# Load and process data for each scheme
schemes_data = {}

# Load data for each scheme and add it to the dictionary
for scheme_name, subdir in [('Baseline (No MAC Randomization)', 'no_rnd'), 
                            ('Kernel Time-Based MAC Re-Randomization', 'kernel_time'), 
                            ('AP-Initiated MAC Re-Randomization', 'ap_trigger')]:
    scheme_dir = os.path.join(base_dir, subdir, 'mode_n', 'without_wmd')
    avg_throughput, std_throughput, all_throughput = load_and_average_iperf3_results(scheme_dir)
    schemes_data[scheme_name] = {
        'mean': avg_throughput,
        'std': std_throughput,
        'individual_results': all_throughput,
        'color': scheme_colors[scheme_name]
    }

# Plot the comparison for TCP Throughput with Error Bars and Individual Test Lines
plot_comparison_with_error_bars(
    distances,
    schemes_data,
    ylabel='Throughput (Mbps)',
    title='TCP Throughput vs Distance from AP for Different Schemes',
    filename=f"{base_dir}/tcp_throughput_comparison_with_error_bars.pdf"
)
