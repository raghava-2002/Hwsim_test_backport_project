import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# Base directory and settings
working_directory = os.getcwd()
base_dir = os.path.join(working_directory, 'iperf3_results')

# Distance from AP for each station
distances = [1, 8.14, 15.32, 22.517, 29.70, 36.87, 44.06, 51.24, 58.24, 65.62, 72.79]

# Function to load iperf3 results for a specific test path
def load_iperf3_results(test_path):
    tcp_retransmissions = []
    throughput_values_tcp = []
    udp_packet_loss_values = []
    udp_jitter_values = []
    throughput_values_udp = []

    for i in range(1, 12):
        try:
            # Load TCP data
            with open(f"{test_path}/tcp/sta{i}_iperf3.json", "r") as f:
                data = json.load(f)
                tcp_retransmissions.append(data['end']['sum_sent']['retransmits'])
                throughput_values_tcp.append(data['end']['sum_received']['bits_per_second'] / 1e6)  # Convert to Mbps

            # Load UDP data
            with open(f"{test_path}/udp/sta{i}_iperf3.json", "r") as f:
                data = json.load(f)
                udp_packet_loss_values.append(data['end']['sum']['lost_percent'])
                udp_jitter_values.append(data['end']['sum']['jitter_ms'])
                throughput_values_udp.append(data['end']['sum']['bits_per_second'] / 1e6)  # Convert to Mbps

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

    # Calculate averages and standard deviations for each parameter
    return {
        'tcp_retrans': (np.mean(tcp_retransmissions, axis=0), np.std(tcp_retransmissions, axis=0), tcp_retransmissions),
        'tcp_throughput': (np.mean(throughput_values_tcp, axis=0), np.std(throughput_values_tcp, axis=0), throughput_values_tcp),
        'udp_loss': (np.mean(udp_packet_loss_values, axis=0), np.std(udp_packet_loss_values, axis=0), udp_packet_loss_values),
        'udp_jitter': (np.mean(udp_jitter_values, axis=0), np.std(udp_jitter_values, axis=0), udp_jitter_values),
        'udp_throughput': (np.mean(throughput_values_udp, axis=0), np.std(throughput_values_udp, axis=0), throughput_values_udp)
    }

# Function to plot a comparison with error bars and individual test lines
def plot_comparison_with_error_bars(x_values, schemes_data, param, ylabel, title, filename):
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

    plt.xlabel('Distance from AP (meters)', fontsize=16)
    plt.ylabel(ylabel, fontsize=16)
    plt.title(title, fontsize=16)
    plt.grid(True)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=14)
    #if param == 'udp_throughput':
        #plt.ylim(10, 50, 10)  # Example: 0 to 100 Mbps in steps of 10
    # Disable scientific notation on y-axis
    ax = plt.gca()
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.get_major_formatter().set_scientific(False)
    ax.yaxis.get_major_formatter().set_useOffset(False)
    plt.savefig(filename, bbox_inches='tight', format='pdf')
    plt.close()

# Define scheme colors
scheme_colors = {
    'Baseline (No MAC Randomization)': 'b',
    'Kernel Time-Based MAC Randomization': 'g',
    'AP-Initiated MAC Randomization': 'r'
}

# Load and process data for each scheme and parameter
parameters = {
    'tcp_throughput': ('Throughput (Mbps)', 'TCP Throughput vs Distance from AP'),
    'tcp_retrans': ('Retransmissions', 'TCP Retransmissions vs Distance from AP'),
    'udp_throughput': ('Throughput (Mbps)', 'UDP Throughput vs Distance from AP'),
    'udp_loss': ('Packet Loss (%)', 'UDP Packet Loss vs Distance from AP'),
    'udp_jitter': ('Jitter (ms)', 'UDP Jitter vs Distance from AP')
}

for param, (ylabel, title) in parameters.items():
    schemes_data = {}

    for scheme_name, subdir in [('Baseline (No MAC Randomization)', 'no_rnd'),
                                ('Kernel Time-Based MAC Randomization', 'kernel_time'),
                                ('AP-Initiated MAC Randomization', 'ap_trigger')]:
        scheme_dir = os.path.join(base_dir, subdir, 'mode_n', 'with_wmd')
        avg, std, all_results = load_and_average_iperf3_results(scheme_dir)[param]

        schemes_data[scheme_name] = {
            'mean': avg,
            'std': std,
            'individual_results': all_results,
            'color': scheme_colors[scheme_name]
        }

    # Plot the comparison for each parameter with error bars and individual test lines
    plot_comparison_with_error_bars(
        distances,
        schemes_data,
        param,
        ylabel=ylabel,
        title=title,
        filename=f"{base_dir}/{param}_comparison_with_error_bars.pdf"
    )
