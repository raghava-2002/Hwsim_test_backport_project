import os
import json
import numpy as np
import matplotlib.pyplot as plt

# Toggle for plotting all individual tests in light color
plot_all_tests = False  # Set to False to disable

# Enable or disable plotting for each scheme
plot_no_rnd = True
plot_kernel_time = True
plot_ap_trigger = True

# Base directory and settings
working_directory = os.getcwd()
base_dir = os.path.join(working_directory, 'iperf3_results')

# Distance from AP for each station
distances = [1, 8.14, 15.32, 22.517, 29.70, 36.87, 44.06, 51.24, 58.24, 65.62, 72.79]

# Function to load iperf3 results from a scheme directory for a specific test
def load_iperf3_results(test_path):
    tcp_retransmissions = []
    throughput_values_tcp = []
    udp_packet_loss_values = []
    udp_jitter_values = []
    throughput_values_udp = []

    # Load TCP results
    for i in range(1, 12):
        try:
            with open(f"{test_path}/tcp/sta{i}_iperf3.json", "r") as f:
                data = json.load(f)
                retransmit_count = data['end']['sum_sent']['retransmits']
                throughput_tcp = data['end']['sum_received']['bits_per_second'] / 1e6
                tcp_retransmissions.append(retransmit_count)
                throughput_values_tcp.append(throughput_tcp)
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass

    # Load UDP results
    for i in range(1, 12):
        try:
            with open(f"{test_path}/udp/sta{i}_iperf3.json", "r") as f:
                data = json.load(f)
                packet_loss = data['end']['sum']['lost_percent']
                jitter = data['end']['sum']['jitter_ms']
                throughput_udp = data['end']['sum']['bits_per_second'] / 1e6
                udp_packet_loss_values.append(packet_loss)
                udp_jitter_values.append(jitter)
                throughput_values_udp.append(throughput_udp)
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass

    return tcp_retransmissions, throughput_values_tcp, udp_packet_loss_values, udp_jitter_values, throughput_values_udp

# Function to load and average iperf3 results from multiple test directories in a scheme
def load_and_average_iperf3_results(scheme_dir):
    tcp_retransmissions = []
    throughput_values_tcp = []
    udp_packet_loss_values = []
    udp_jitter_values = []
    throughput_values_udp = []

    # Loop through each test directory
    test_dirs = [d for d in os.listdir(scheme_dir) if d.startswith('test_')]
    for test_dir in test_dirs:
        test_path = os.path.join(scheme_dir, test_dir)
        tcp_retrans, tcp_throughput, udp_loss, udp_jitter, udp_throughput = load_iperf3_results(test_path)

        if tcp_throughput:
            tcp_retransmissions.append(tcp_retrans)
            throughput_values_tcp.append(tcp_throughput)
            udp_packet_loss_values.append(udp_loss)
            udp_jitter_values.append(udp_jitter)
            throughput_values_udp.append(udp_throughput)

    # Calculate averages and standard deviations
    avg_tcp_retransmissions = np.mean(tcp_retransmissions, axis=0)
    avg_throughput_values_tcp = np.mean(throughput_values_tcp, axis=0)
    avg_udp_packet_loss_values = np.mean(udp_packet_loss_values, axis=0)
    avg_udp_jitter_values = np.mean(udp_jitter_values, axis=0)
    avg_throughput_values_udp = np.mean(throughput_values_udp, axis=0)

    std_tcp_retransmissions = np.std(tcp_retransmissions, axis=0)
    std_throughput_values_tcp = np.std(throughput_values_tcp, axis=0)
    std_udp_packet_loss_values = np.std(udp_packet_loss_values, axis=0)
    std_udp_jitter_values = np.std(udp_jitter_values, axis=0)
    std_throughput_values_udp = np.std(throughput_values_udp, axis=0)

    return (avg_tcp_retransmissions, avg_throughput_values_tcp, avg_udp_packet_loss_values, avg_udp_jitter_values, avg_throughput_values_udp, 
            std_tcp_retransmissions, std_throughput_values_tcp, std_udp_packet_loss_values, std_udp_jitter_values, std_throughput_values_udp)

# Function to plot a single metric with optional confidence intervals
def plot_graph(x_values, y_values_dict, ylabel, title, filename, individual_results=None):
    plt.figure(figsize=(10, 8))
    for scheme, values in y_values_dict.items():
        mean_values = values['y']
        std_dev = values['std']  # Standard deviation for confidence intervals

        # Plot all individual tests in lighter color, if enabled
        if plot_all_tests and individual_results and scheme in individual_results:
            for result in individual_results[scheme]:
                plt.plot(x_values, result, color=values['color'], alpha=0.3, linestyle='--')

        # Plot the averaged line in solid color
        plt.plot(x_values, mean_values, marker='o', linestyle='-', color=values['color'], label=scheme)

        # Add shaded region for confidence interval (mean ± standard deviation)
        plt.fill_between(x_values, mean_values - std_dev, mean_values + std_dev, color=values['color'], alpha=0.2)

    plt.xlabel('Distance from AP (meters)', fontsize=16)
    plt.ylabel(ylabel, fontsize=16)
    plt.title(title, fontsize=16)
    plt.xlim(0, max(x_values) + 5)
    plt.ylim(0, max([max(values['y']) + max(values['std']) for values in y_values_dict.values()]) + 1)
    plt.grid(True)
    plt.xticks(fontsize=14)  # Increase font size for x-axis tick labels
    plt.yticks(fontsize=14)  # Increase font size for y-axis tick labels
    plt.legend()
    plt.savefig(filename, bbox_inches='tight', format='pdf')
    plt.close()

# Load and average data for each scheme
data_to_plot = {}
individual_results = {}

# Define the colors for each scheme
scheme_colors = {'no_rnd': 'b', 'kernel_time': 'g', 'ap_trigger': 'r'}

# Load and process data for each scheme, only if enabled
if plot_no_rnd:
    no_rnd_dir = os.path.join(base_dir, 'no_rnd', 'mode_n', 'with_wmd')
    avg_tcp_retrans_no_rnd, avg_tcp_throughput_no_rnd, avg_udp_loss_no_rnd, avg_udp_jitter_no_rnd, avg_udp_throughput_no_rnd, \
    std_tcp_retrans_no_rnd, std_throughput_tcp_no_rnd, std_udp_loss_no_rnd, std_udp_jitter_no_rnd, std_udp_throughput_no_rnd = load_and_average_iperf3_results(no_rnd_dir)
    
    data_to_plot['Baseline (No MAC Randomization)'] = {
        'tcp_throughput': {'y': avg_tcp_throughput_no_rnd, 'std': std_throughput_tcp_no_rnd, 'color': scheme_colors['no_rnd']}
    }

if plot_kernel_time:
    kernel_time_dir = os.path.join(base_dir, 'kernel_time', 'mode_n', 'with_wmd')
    avg_tcp_retrans_kernel_time, avg_tcp_throughput_kernel_time, avg_udp_loss_kernel_time, avg_udp_jitter_kernel_time, avg_udp_throughput_kernel_time, \
    std_tcp_retrans_kernel_time, std_throughput_tcp_kernel_time, std_udp_loss_kernel_time, std_udp_jitter_kernel_time, std_udp_throughput_kernel_time = load_and_average_iperf3_results(kernel_time_dir)
    
    data_to_plot['Kernel Time-Based MAC Randomization'] = {
        'tcp_throughput': {'y': avg_tcp_throughput_kernel_time, 'std': std_throughput_tcp_kernel_time, 'color': scheme_colors['kernel_time']}
    }

if plot_ap_trigger:
    ap_trigger_dir = os.path.join(base_dir, 'ap_trigger', 'mode_n', 'with_wmd')
    avg_tcp_retrans_ap_trigger, avg_tcp_throughput_ap_trigger, avg_udp_loss_ap_trigger, avg_udp_jitter_ap_trigger, avg_udp_throughput_ap_trigger, \
    std_tcp_retrans_ap_trigger, std_throughput_tcp_ap_trigger, std_udp_loss_ap_trigger, std_udp_jitter_ap_trigger, std_udp_throughput_ap_trigger = load_and_average_iperf3_results(ap_trigger_dir)
    
    data_to_plot['AP-Initiated MAC Randomization'] = {
        'tcp_throughput': {'y': avg_tcp_throughput_ap_trigger, 'std': std_throughput_tcp_ap_trigger, 'color': scheme_colors['ap_trigger']}
    }

# Plot TCP Throughput with Confidence Interval
# Plot TCP Throughput with Confidence Interval
plot_graph(distances, {scheme: data['tcp_throughput'] for scheme, data in data_to_plot.items()},
           'Throughput (Mbps)', 'TCP Throughput vs Distance from AP', f"{base_dir}/tcp_throughput_comparison.pdf")
