import json
import matplotlib.pyplot as plt

# Distance from AP for each station
distances = [2, 7, 15, 25, 35]
station_labels = ['sta1', 'sta2', 'sta3', 'sta4', 'sta5']

# Base directory for scheme_3
base_dir = "/home/rathan/Downloads/hwsim_test/testing/iperf3_results"
scheme_dir = f"{base_dir}/scheme_3"

# Function to load iperf3 results from a scheme directory for a specific test folder
def load_iperf3_results(scheme_dir, test_folder):
    tcp_retransmissions = []
    throughput_values_tcp = []
    udp_packet_loss_values = []
    udp_jitter_values = []
    throughput_values_udp = []

    # Load TCP and UDP results for each station
    for i in range(1, 6):
        try:
            with open(f"{scheme_dir}/{test_folder}/tcp/sta{i}_iperf3.json", "r") as f:
                data = json.load(f)
                retransmit_count = data['end']['sum_sent']['retransmits']
                throughput_tcp = data['end']['sum_received']['bits_per_second'] / 1e6
                tcp_retransmissions.append(retransmit_count)
                throughput_values_tcp.append(throughput_tcp)
        except FileNotFoundError:
            print(f"File not found: {scheme_dir}/{test_folder}/tcp/sta{i}_iperf3.json")

        try:
            with open(f"{scheme_dir}/{test_folder}/udp/sta{i}_iperf3.json", "r") as f:
                data = json.load(f)
                packet_loss = data['end']['sum']['lost_percent']
                jitter = data['end']['sum']['jitter_ms']
                throughput_udp = data['end']['sum']['bits_per_second'] / 1e6
                udp_packet_loss_values.append(packet_loss)
                udp_jitter_values.append(jitter)
                throughput_values_udp.append(throughput_udp)
        except FileNotFoundError:
            print(f"File not found: {scheme_dir}/{test_folder}/udp/sta{i}_iperf3.json")

    return tcp_retransmissions, throughput_values_tcp, udp_packet_loss_values, udp_jitter_values, throughput_values_udp

# Function to plot graphs for TCP throughput and UDP metrics
def plot_graph(x_values, y_values_dict, ylabel, title, filename):
    plt.figure(figsize=(10, 8))
    for test_num, values in y_values_dict.items():
        label = f"{test_num}"
        plt.plot(x_values, values['y'], marker='o', linestyle='-', label=label)
    plt.xlabel('Distance from AP (meters)')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xlim(0, 40)
    plt.ylim(0)
    plt.grid(True)
    plt.legend()
    plt.savefig(filename)


# Load data for scheme_3's test_1 and test_2
data_to_plot = {}
for test in ["test_1", "test_2"]:
    tcp_retrans, tcp_throughput, udp_loss, udp_jitter, udp_throughput = load_iperf3_results(scheme_dir, test)
    data_to_plot[test] = {
        'tcp_throughput': tcp_throughput,
        'tcp_retrans': tcp_retrans,
        'udp_throughput': udp_throughput,
        'udp_loss': udp_loss,
        'udp_jitter': udp_jitter
    }

# Plot TCP Throughput Comparison for scheme_3 across test_1 and test_2
plot_graph(distances, {test: {'y': data['tcp_throughput']} for test, data in data_to_plot.items()},
           'Throughput (Mbps)', 'TCP Throughput Comparison for Scheme 3', f"{base_dir}/tcp_throughput_comparison_scheme_3.png")

# Plot additional metrics as needed
# Example for UDP Throughput Comparison
plot_graph(distances, {test: {'y': data['udp_throughput']} for test, data in data_to_plot.items()},
           'Throughput (Mbps)', 'UDP Throughput Comparison for Scheme 3', f"{base_dir}/udp_throughput_comparison_scheme_3.png")

# Similarly, add plot functions for other metrics like TCP Retransmissions, UDP Packet Loss, and UDP Jitter.
