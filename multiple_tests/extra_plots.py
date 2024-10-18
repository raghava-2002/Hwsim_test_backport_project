import os
import json
import numpy as np
import matplotlib.pyplot as plt

# Base directory for test results
working_directory = os.getcwd()
base_dir = os.path.join(working_directory, 'iperf3_results')

# Enable or disable plotting for each scheme
plot_no_rnd = True
plot_kernel_time = True
plot_ap_trigger = True

# Function to load throughput results for all stations in a specific test directory
def load_test_results(test_path):
    throughputs = []
    for i in range(1, 12):  # Assuming stations are named sta1, sta2, ..., sta11
        try:
            with open(f"{test_path}/tcp/sta{i}_iperf3.json", "r") as f:
                data = json.load(f)
                throughput = data['end']['sum_received']['bits_per_second'] / 1e6  # Convert to Mbps
                throughputs.append(throughput)
        except FileNotFoundError:
            throughputs.append(None)  # Append None for missing files to maintain consistent station count
    return throughputs

# Function to gather throughput data for each station across all tests for a given scheme
def gather_data_by_station(scheme_dir):
    test_dirs = [d for d in os.listdir(scheme_dir) if d.startswith('test_')]
    station_data = {i: [] for i in range(1, 12)}  # Initialize empty lists for each station

    for test_dir in test_dirs:
        test_path = os.path.join(scheme_dir, test_dir)
        throughput_results = load_test_results(test_path)

        for i, throughput in enumerate(throughput_results):
            if throughput is not None:
                station_data[i+1].append(throughput)  # Organize data by station

    return station_data

# Function to plot throughput variability for each station as a box plot
def plot_station_box_plot(station_data, ylabel, title, filename):
    plt.figure(figsize=(12, 6))
    station_labels = [f'sta{i}' for i in range(1, 12)]  # X-axis labels
    box_data = [station_data[i] for i in range(1, 12)]  # Box plot data for each station

    plt.boxplot(box_data, labels=station_labels, showfliers=True)
    plt.xlabel('Stations')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.savefig(filename)
    plt.close()

# Load and plot data for each scheme
scheme_dirs = {'No MAC Randomization': 'no_rnd', 
               'Kernel Time-Based Randomization': 'kernel_time', 
               'AP Trigger Randomization': 'ap_trigger'}

for scheme_name, scheme_folder in scheme_dirs.items():
    if (scheme_name == 'No MAC Randomization' and plot_no_rnd) or \
       (scheme_name == 'Kernel Time-Based Randomization' and plot_kernel_time) or \
       (scheme_name == 'AP Trigger Randomization' and plot_ap_trigger):
        
        scheme_dir = os.path.join(base_dir, scheme_folder)
        station_data = gather_data_by_station(scheme_dir)

        # Plot the data with each station as a separate box in the plot
        plot_station_box_plot(
            station_data,
            'Throughput (Mbps)',
            f'Throughput Variability per Station - {scheme_name}',
            os.path.join(base_dir, f'{scheme_folder}_throughput_boxplot.png')
        )
