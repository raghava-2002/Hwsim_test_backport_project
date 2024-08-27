import json
import matplotlib.pyplot as plt

# Define file paths (Update these paths to where your JSON files are stored)
tcp_with_mac_randomization_path = '/home/rathan/Downloads/hwsim_test/with_mac_randomisaion/tcp_test_results.json'
udp_with_mac_randomization_path = '/home/rathan/Downloads/hwsim_test/with_mac_randomisaion/udp_test_results.json'
tcp_without_mac_randomization_path = '/home/rathan/Downloads/hwsim_test/without_mac_randomizattion/tcp_test_results.json'
udp_without_mac_randomization_path = '/home/rathan/Downloads/hwsim_test/without_mac_randomizattion/udp_test_results.json'

# Function to load JSON data
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to extract metrics
def extract_metrics(data):
    intervals = data['intervals']
    times = []
    bandwidths = []
    packet_loss = None
    jitter = []

    if 'end' in data:
        summary = data['end']
        if 'sum' in summary:
            if 'lost_percent' in summary['sum']:
                packet_loss = summary['sum']['lost_percent']
            if 'jitter_ms' in summary['sum']:
                jitter = summary['sum']['jitter_ms']

    for interval in intervals:
        times.append(interval['sum']['end'])
        bandwidths.append(interval['sum']['bits_per_second'])

    return times, bandwidths, packet_loss, jitter

# Load data
tcp_with_mac_randomization = load_json(tcp_with_mac_randomization_path)
udp_with_mac_randomization = load_json(udp_with_mac_randomization_path)
tcp_without_mac_randomization = load_json(tcp_without_mac_randomization_path)
udp_without_mac_randomization = load_json(udp_without_mac_randomization_path)

# Extract metrics
tcp_times_with, tcp_bw_with, tcp_packet_loss_with, tcp_jitter_with = extract_metrics(tcp_with_mac_randomization)
tcp_times_without, tcp_bw_without, tcp_packet_loss_without, tcp_jitter_without = extract_metrics(tcp_without_mac_randomization)

udp_times_with, udp_bw_with, udp_packet_loss_with, udp_jitter_with = extract_metrics(udp_with_mac_randomization)
udp_times_without, udp_bw_without, udp_packet_loss_without, udp_jitter_without = extract_metrics(udp_without_mac_randomization)

# Plot Bandwidth Comparison for TCP
plt.figure(figsize=(12, 8))
plt.subplot(2, 1, 1)
plt.plot(tcp_times_with, tcp_bw_with, marker='o', linestyle='-', color='r', label='TCP with MAC Randomization')
plt.plot(tcp_times_without, tcp_bw_without, marker='o', linestyle='-', color='g', label='TCP without MAC Randomization')
plt.title('TCP Bandwidth Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Throughput (bits per second)')
plt.legend()
plt.grid(True)

# Plot Bandwidth Comparison for UDP
plt.subplot(2, 1, 2)
plt.plot(udp_times_with, udp_bw_with, marker='o', linestyle='-', color='r', label='UDP with MAC Randomization')
plt.plot(udp_times_without, udp_bw_without, marker='o', linestyle='-', color='g', label='UDP without MAC Randomization')
plt.title('UDP Bandwidth Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Throughput (bits per second)')
plt.legend()
plt.grid(True)

plt.tight_layout()

# Save the plot as a PNG file
plt.savefig('/home/rathan/Downloads/hwsim_test/pics/bandwidth_comparison.png')
plt.show()
