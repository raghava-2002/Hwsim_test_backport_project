import json
import matplotlib.pyplot as plt

# Distance from AP for each station
distances = [5, 10, 15, 20, 25]
station_labels = ['5(sta1)', '10(sta2)', '15(sta3)', '20(sta4)', '25(sta5)']  # Custom station labels

# Lists to store values for each station
tcp_retransmissions = []
udp_packet_loss_values = []
udp_jitter_values = []
throughput_values_tcp = []
throughput_values_udp = []

# Load iperf3 JSON results for TCP (throughput and retransmissions)
for i in range(1, 6):
    with open(f"/home/rathan/Downloads/hwsim_test/testing/iperf3_results/scheme_2/test_1/tcp/sta{i}_iperf3.json", "r") as f:
        data = json.load(f)
        # Extract TCP retransmissions and throughput
        retransmit_count = data['end']['sum_sent']['retransmits']  # TCP retransmits field
        throughput_tcp = data['end']['sum_received']['bits_per_second'] / 1e6  # Convert from bits/sec to Mbps
        tcp_retransmissions.append(retransmit_count)
        throughput_values_tcp.append(throughput_tcp)

# Load iperf3 JSON results for UDP (throughput, packet loss, and jitter)
for i in range(1, 6):
    with open(f"/home/rathan/Downloads/hwsim_test/testing/iperf3_results/scheme_1/test_1/udp/sta{i}_iperf3.json", "r") as f:
        data = json.load(f)
        # Extract UDP packet loss, jitter, and throughput
        packet_loss = data['end']['sum']['lost_percent']  # Packet loss percentage
        jitter = data['end']['sum']['jitter_ms']  # Jitter in milliseconds
        throughput_udp = data['end']['sum']['bits_per_second'] / 1e6  # Convert from bits/sec to Mbps
        udp_packet_loss_values.append(packet_loss)
        udp_jitter_values.append(jitter)
        throughput_values_udp.append(throughput_udp)

# Function to plot graphs with customized x-axis labels and limits
def plot_graph(x_values, y_values, ylabel, title, filename, color, label):
    plt.figure(figsize=(8, 6))
    plt.plot(x_values, y_values, marker='o', linestyle='-', color=color, label=label)
    plt.xlabel('Distance from AP (meters)')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x_values, station_labels)  # Use station labels for x-axis
    plt.xlim(0, 30)  # Start x-axis from 0 and limit to 30 (optional)
    plt.ylim(0)  # Start y-axis from 0
    plt.grid(True)
    plt.legend()
    plt.savefig(filename)


# Plotting TCP Throughput vs Distance from AP
plot_graph(distances, throughput_values_tcp, 'Throughput (Mbps)', 'TCP Throughput vs Distance from AP', 
           '/home/rathan/Downloads/hwsim_test/testing/tcp_throughput_vs_distance.png', 'b', 'TCP Throughput')

# Plotting TCP Retransmissions vs Distance from AP
plot_graph(distances, tcp_retransmissions, 'Retransmissions', 'TCP Retransmissions vs Distance from AP', 
           '/home/rathan/Downloads/hwsim_test/testing/tcp_retransmissions_vs_distance.png', 'r', 'TCP Retransmissions')

# Plotting UDP Throughput vs Distance from AP
plot_graph(distances, throughput_values_udp, 'Throughput (Mbps)', 'UDP Throughput vs Distance from AP', 
           '/home/rathan/Downloads/hwsim_test/testing/udp_throughput_vs_distance.png', 'c', 'UDP Throughput')

# Plotting UDP Packet Loss vs Distance from AP
plot_graph(distances, udp_packet_loss_values, 'Packet Loss (%)', 'UDP Packet Loss vs Distance from AP', 
           '/home/rathan/Downloads/hwsim_test/testing/udp_packet_loss_vs_distance.png', 'g', 'UDP Packet Loss (%)')

# Plotting UDP Jitter vs Distance from AP
plot_graph(distances, udp_jitter_values, 'Jitter (ms)', 'UDP Jitter vs Distance from AP', 
           '/home/rathan/Downloads/hwsim_test/testing/udp_jitter_vs_distance.png', 'm', 'UDP Jitter (ms)')
