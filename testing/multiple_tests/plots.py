import json
import matplotlib.pyplot as plt
import glob
import os
import numpy as np

# Distance from AP for each station
distances = [2, 7, 15, 25, 35]
station_labels = ['sta1', 'sta2', 'sta3', 'sta4', 'sta5']

# Base directory for the scheme
base_dir = "/home/rathan/Downloads/hwsim_test/testing/multiple_tests/iperf3_results/ap_trigger"
# Define the scheme directory explicitly
scheme_dir = "/home/rathan/Downloads/hwsim_test/testing/multiple_tests/iperf3_results/ap_trigger"


def load_all_iperf3_results(scheme_dir):
    all_tcp_throughput = []
    all_udp_throughput = []

    # Find all test directories that match the pattern 'test_*'
    test_dirs = glob.glob(f"{scheme_dir}/test_*")
    
    # Loop over each found test directory
    for test_dir in test_dirs:
        tcp_throughput = []
        udp_throughput = []

        # Load TCP results
        for i in range(1, 6):
            tcp_file = f"{test_dir}/tcp/sta{i}_iperf3.json"
            if os.path.exists(tcp_file):
                if os.path.getsize(tcp_file) > 0:  # Ensure file is not empty
                    try:
                        with open(tcp_file, "r") as f:
                            data = json.load(f)
                            throughput_tcp = data['end']['sum_received']['bits_per_second'] / 1e6
                            tcp_throughput.append(throughput_tcp)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON from file: {tcp_file}. File may be corrupted.")
                        tcp_throughput.append(0)
                else:
                    print(f"TCP file is empty: {tcp_file}")
                    tcp_throughput.append(0)
            else:
                print(f"TCP file not found: {tcp_file}")
                tcp_throughput.append(0)

        # Load UDP results
        for i in range(1, 6):
            udp_file = f"{test_dir}/udp/sta{i}_iperf3.json"
            if os.path.exists(udp_file):
                if os.path.getsize(udp_file) > 0:  # Ensure file is not empty
                    try:
                        with open(udp_file, "r") as f:
                            data = json.load(f)
                            throughput_udp = data['end']['sum']['bits_per_second'] / 1e6
                            udp_throughput.append(throughput_udp)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON from file: {udp_file}. File may be corrupted.")
                        udp_throughput.append(0)
                else:
                    print(f"UDP file is empty: {udp_file}")
                    udp_throughput.append(0)
            else:
                print(f"UDP file not found: {udp_file}")
                udp_throughput.append(0)

        # Append this test's results to the aggregate lists
        all_tcp_throughput.append(tcp_throughput)
        all_udp_throughput.append(udp_throughput)

    return all_tcp_throughput, all_udp_throughput


# Function to plot graphs with multiple tests and the average line
def plot_graph_with_average(x_values, all_y_values, ylabel, title, filename):
    if not all_y_values:  # Check if there are any test results
        print("No data available to plot.")
        return

    plt.figure(figsize=(10, 8))
    
    # Plot all test lines in light color
    for y_values in all_y_values:
        if y_values:  # Check if y_values has data
            plt.plot(x_values, y_values, marker='o', linestyle='-', color='lightgray', alpha=0.6)
    
    # Calculate the average only if there is valid data
    avg_y_values = np.mean(all_y_values, axis=0) if all_y_values else np.zeros(len(x_values))
    
    # Check if avg_y_values has the correct shape
    if avg_y_values.shape[0] != len(x_values):
        print("Mismatch in data dimensions; skipping average plot.")
        return

    # Plot the average line in dark color if data is valid
    plt.plot(x_values, avg_y_values, marker='o', linestyle='-', color='black', label='Average')
    
    plt.xlabel('Distance from AP (meters)')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xlim(0, 40)
    plt.ylim(0)
    plt.grid(True)
    plt.legend()
    plt.savefig(filename)
 

# Load data for the scheme and plot
tcp_throughput_all, udp_throughput_all = load_all_iperf3_results(base_dir)

# Plot TCP Throughput for Scheme
plot_graph_with_average(distances, tcp_throughput_all, 'Throughput (Mbps)', 'TCP Throughput for Scheme', f"{base_dir}/tcp_throughput_average.png")

# Plot UDP Throughput for Scheme
plot_graph_with_average(distances, udp_throughput_all, 'Throughput (Mbps)', 'UDP Throughput for Scheme', f"{base_dir}/udp_throughput_average.png")
