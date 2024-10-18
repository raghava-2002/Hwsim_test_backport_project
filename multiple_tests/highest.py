import os
import json
import numpy as np
import matplotlib.pyplot as plt

# Toggle for plotting all individual tests in light color
plot_all_tests = True  # Set to False to disable

# Enable or disable plotting for each scheme
plot_no_rnd = True
plot_kernel_time = True
plot_ap_trigger = True

# Base directory and settings
working_directory = os.getcwd()
base_dir = os.path.join(working_directory, 'iperf3_results')

# Distance from AP for each station
distances = [2, 4, 7, 10, 13, 18, 21, 25, 28, 31, 35]

# Function to load iperf3 results from a scheme directory for a specific test
def load_iperf3_results(test_path):
    max_throughput_values_tcp = []

    # Load TCP results, finding the max throughput over intervals
    for i in range(1, 12):
        max_throughput = 0
        try:
            with open(f"{test_path}/tcp/sta{i}_iperf3.json", "r") as f:
                data = json.load(f)
                # Iterate over intervals to find max throughput
                for interval in data.get("intervals", []):
                    throughput_tcp = interval["sum"]["bits_per_second"] / 1e6  # Convert to Mbps
                    if throughput_tcp > max_throughput:
                        max_throughput = throughput_tcp
                max_throughput_values_tcp.append(max_throughput)
        except FileNotFoundError:
            print(f"File not found: {test_path}/tcp/sta{i}_iperf3.json")
            max_throughput_values_tcp.append(0)  # Append 0 if file not found for consistency

    return max_throughput_values_tcp

# Function to load and find the highest iperf3 result for each station across all test directories in a scheme
def load_and_find_max_iperf3_results(scheme_dir):
    all_throughputs = []
    max_throughputs = []
    
    # Loop through each test directory
    test_dirs = [d for d in os.listdir(scheme_dir) if d.startswith('test_')]
    for test_dir in test_dirs:
        test_path = os.path.join(scheme_dir, test_dir)
        throughput_tcp = load_iperf3_results(test_path)

        if throughput_tcp:
            all_throughputs.append(throughput_tcp)
    
    # Convert to numpy array for easier manipulation
    all_throughputs = np.array(all_throughputs)
    
    # Find the maximum throughput for each station across all tests
    max_throughputs = np.max(all_throughputs, axis=0)
    
    # Calculate the average for plotting a darker line
    avg_throughputs = np.mean(all_throughputs, axis=0)

    return max_throughputs, avg_throughputs, all_throughputs

# Function to plot with highlights on max individual results
def plot_graph(x_values, y_values_dict, ylabel, title, filename, individual_results=None, max_values=None):
    plt.figure(figsize=(10, 8))
    for scheme, values in y_values_dict.items():
        # Plot the highest individual results in lighter color
        if plot_all_tests and individual_results and scheme in individual_results:
            for result in individual_results[scheme]:
                plt.plot(x_values, result, color=values['color'], alpha=0.3, linestyle='--')

        # Plot the highest values in solid light color
        if max_values and scheme in max_values:
            plt.plot(x_values, max_values[scheme], marker='o', linestyle='-', color=values['color'], alpha=0.5, label=f'{scheme} - Max')

        # Plot the average line in a solid darker color
        plt.plot(x_values, values['avg'], marker='o', linestyle='-', color=values['color'], label=f'{scheme} - Avg')
    
    plt.xlabel('Distance from AP (meters)')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xlim(0, 40)
    plt.ylim(0)
    plt.grid(True)
    plt.legend()
    plt.savefig(filename)
    plt.close()

# Load data for each scheme
data_to_plot = {}
individual_results = {}
max_values = {}

# Define the colors for each scheme
scheme_colors = {'no_rnd': 'b', 'kernel_time': 'g', 'ap_trigger': 'r'}

# Process data for each scheme
if plot_no_rnd:
    no_rnd_dir = os.path.join(base_dir, 'no_rnd')
    max_throughput_no_rnd, avg_throughput_no_rnd, all_throughput_no_rnd = load_and_find_max_iperf3_results(no_rnd_dir)
    
    data_to_plot['Baseline (No MAC Randomization)'] = {'avg': avg_throughput_no_rnd, 'color': scheme_colors['no_rnd']}
    max_values['Baseline (No MAC Randomization)'] = max_throughput_no_rnd
    if plot_all_tests:
        individual_results['Baseline (No MAC Randomization)'] = all_throughput_no_rnd

if plot_kernel_time:
    kernel_time_dir = os.path.join(base_dir, 'kernel_time')
    max_throughput_kernel_time, avg_throughput_kernel_time, all_throughput_kernel_time = load_and_find_max_iperf3_results(kernel_time_dir)
    
    data_to_plot['Kernel Time-Based MAC Randomization'] = {'avg': avg_throughput_kernel_time, 'color': scheme_colors['kernel_time']}
    max_values['Kernel Time-Based MAC Randomization'] = max_throughput_kernel_time
    if plot_all_tests:
        individual_results['Kernel Time-Based MAC Randomization'] = all_throughput_kernel_time

if plot_ap_trigger:
    ap_trigger_dir = os.path.join(base_dir, 'ap_trigger')
    max_throughput_ap_trigger, avg_throughput_ap_trigger, all_throughput_ap_trigger = load_and_find_max_iperf3_results(ap_trigger_dir)
    
    data_to_plot['AP-Initiated MAC Randomization'] = {'avg': avg_throughput_ap_trigger, 'color': scheme_colors['ap_trigger']}
    max_values['AP-Initiated MAC Randomization'] = max_throughput_ap_trigger
    if plot_all_tests:
        individual_results['AP-Initiated MAC Randomization'] = all_throughput_ap_trigger

# Plot throughput with both max and average
plot_graph(distances, {scheme: {'avg': data['avg'], 'color': data['color']} for scheme, data in data_to_plot.items()},
           'Throughput (Mbps)', 'TCP Throughput vs Distance from AP', f"{base_dir}/highest_tcp_throughput_comparison.png", 
           individual_results=individual_results, max_values=max_values)
