import json
import matplotlib.pyplot as plt

# Distance from AP for each station
distances = [2, 7, 15, 25, 35]
station_labels = ['sta1', 'sta2', 'sta3', 'sta4', 'sta5']  # Custom station labels

# Enable or disable plotting for each scheme
plot_scheme_1 = True
plot_scheme_2 = True
plot_scheme_3 = True

# Base directories for different schemes
base_dir = "/home/rathan/Downloads/hwsim_test/testing/iperf3_results"

# Function to load iperf3 results from a scheme directory
def load_iperf3_results(scheme_dir, test_num):
    tcp_retransmissions = []
    throughput_values_tcp = []
    udp_packet_loss_values = []
    udp_jitter_values = []
    throughput_values_udp = []

    # Load TCP results
    for i in range(1, 6):
        try:
            with open(f"{scheme_dir}/test_{test_num}/tcp/sta{i}_iperf3.json", "r") as f:
                data = json.load(f)
                retransmit_count = data['end']['sum_sent']['retransmits']  # TCP retransmits field
                throughput_tcp = data['end']['sum_received']['bits_per_second'] / 1e6  # Convert to Mbps
                tcp_retransmissions.append(retransmit_count)
                throughput_values_tcp.append(throughput_tcp)
        except FileNotFoundError:
            print(f"File not found: {scheme_dir}/test_{test_num}/tcp/sta{i}_iperf3.json")
    
    # Load UDP results
    for i in range(1, 6):
        try:
            with open(f"{scheme_dir}/test_{test_num}/udp/sta{i}_iperf3.json", "r") as f:
                data = json.load(f)
                packet_loss = data['end']['sum']['lost_percent']  # Packet loss percentage
                jitter = data['end']['sum']['jitter_ms']  # Jitter in milliseconds
                throughput_udp = data['end']['sum']['bits_per_second'] / 1e6  # Convert to Mbps
                udp_packet_loss_values.append(packet_loss)
                udp_jitter_values.append(jitter)
                throughput_values_udp.append(throughput_udp)
        except FileNotFoundError:
            print(f"File not found: {scheme_dir}/test_{test_num}/udp/sta{i}_iperf3.json")

    return tcp_retransmissions, throughput_values_tcp, udp_packet_loss_values, udp_jitter_values, throughput_values_udp

# Function to plot graphs with customized x-axis labels and limits
def plot_graph(x_values, y_values_dict, ylabel, title, filename):
    plt.figure(figsize=(10, 8))
    for scheme, values in y_values_dict.items():
        plt.plot(x_values, values['y'], marker='o', linestyle='-', color=values['color'], label=scheme)
    plt.xlabel('Distance from AP (meters)')
    plt.ylabel(ylabel)
    plt.title(title)
    # Set the x-ticks with combined labels
    #plt.xticks(x_values, tick_labels)
    #plt.xticks(x_values, station_labels)  # Use station labels for x-axis
    plt.xlim(0, 40)  # Start x-axis from 0 and limit to 30 (optional)
    plt.ylim(0)  # Start y-axis from 0
    plt.grid(True)
    plt.legend()
    plt.savefig(filename)

# Load and plot data for each scheme
data_to_plot = {}

if plot_scheme_1:
    scheme_1_dir = f"{base_dir}/scheme_1"
    tcp_retrans_1, tcp_throughput_1, udp_loss_1, udp_jitter_1, udp_throughput_1 = load_iperf3_results(scheme_1_dir, 1)
    data_to_plot['Baseline (No MAC Randomization)'] = {'tcp_throughput': tcp_throughput_1, 'tcp_retrans': tcp_retrans_1, 
                                                      'udp_throughput': udp_throughput_1, 'udp_loss': udp_loss_1, 'udp_jitter': udp_jitter_1, 
                                                      'color': 'b'}

if plot_scheme_2:
    scheme_2_dir = f"{base_dir}/scheme_2"
    tcp_retrans_2, tcp_throughput_2, udp_loss_2, udp_jitter_2, udp_throughput_2 = load_iperf3_results(scheme_2_dir, 1)
    data_to_plot['Kernel Time-Based MAC Randomization'] = {'tcp_throughput': tcp_throughput_2, 'tcp_retrans': tcp_retrans_2, 
                                                           'udp_throughput': udp_throughput_2, 'udp_loss': udp_loss_2, 'udp_jitter': udp_jitter_2, 
                                                           'color': 'g'}

if plot_scheme_3:
    scheme_3_dir = f"{base_dir}/scheme_3"
    tcp_retrans_3, tcp_throughput_3, udp_loss_3, udp_jitter_3, udp_throughput_3 = load_iperf3_results(scheme_3_dir, 1)
    data_to_plot['AP-Initiated MAC Randomization'] = {'tcp_throughput': tcp_throughput_3, 'tcp_retrans': tcp_retrans_3, 
                                                     'udp_throughput': udp_throughput_3, 'udp_loss': udp_loss_3, 'udp_jitter': udp_jitter_3, 
                                                     'color': 'r'}

# Plot TCP Throughput vs Distance from AP (for all schemes)
plot_graph(distances, {scheme: {'y': data['tcp_throughput'], 'color': data['color']} for scheme, data in data_to_plot.items()},
           'Throughput (Mbps)', 'TCP Throughput vs Distance from AP', f"{base_dir}/tcp_throughput_comparison.png")

# Plot TCP Retransmissions vs Distance from AP (for all schemes)
plot_graph(distances, {scheme: {'y': data['tcp_retrans'], 'color': data['color']} for scheme, data in data_to_plot.items()},
           'Retransmissions', 'TCP Retransmissions vs Distance from AP', f"{base_dir}/tcp_retransmissions_comparison.png")

# Plot UDP Throughput vs Distance from AP (for all schemes)
plot_graph(distances, {scheme: {'y': data['udp_throughput'], 'color': data['color']} for scheme, data in data_to_plot.items()},
           'Throughput (Mbps)', 'UDP Throughput vs Distance from AP', f"{base_dir}/udp_throughput_comparison.png")

# Plot UDP Packet Loss vs Distance from AP (for all schemes)
plot_graph(distances, {scheme: {'y': data['udp_loss'], 'color': data['color']} for scheme, data in data_to_plot.items()},
           'Packet Loss (%)', 'UDP Packet Loss vs Distance from AP', f"{base_dir}/udp_packet_loss_comparison.png")

# Plot UDP Jitter vs Distance from AP (for all schemes)
plot_graph(distances, {scheme: {'y': data['udp_jitter'], 'color': data['color']} for scheme, data in data_to_plot.items()},
           'Jitter (ms)', 'UDP Jitter vs Distance from AP', f"{base_dir}/udp_jitter_comparison.png")

