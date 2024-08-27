
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
def extract_metrics(data, is_tcp=True):
    intervals = data['intervals']
    times = []
    bandwidths = []
    retransmissions = []  # Only for TCP
    packet_loss = None  # Only for UDP
    jitter = []  # Only for UDP

    if is_tcp:
        for interval in intervals:
            times.append(interval['sum']['end'])
            bandwidths.append(interval['sum']['bits_per_second'])
            retransmissions.append(interval['sum']['retransmits'])  # Retransmissions for TCP
    else:
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

    return times, bandwidths, retransmissions, packet_loss, jitter

# Load data
tcp_with_mac_randomization = load_json(tcp_with_mac_randomization_path)
udp_with_mac_randomization = load_json(udp_with_mac_randomization_path)
tcp_without_mac_randomization = load_json(tcp_without_mac_randomization_path)
udp_without_mac_randomization = load_json(udp_without_mac_randomization_path)

# Extract metrics
tcp_times_with, tcp_bw_with, tcp_retrans_with, _, _ = extract_metrics(tcp_with_mac_randomization, is_tcp=True)
tcp_times_without, tcp_bw_without, tcp_retrans_without, _, _ = extract_metrics(tcp_without_mac_randomization, is_tcp=True)

udp_times_with, udp_bw_with, _, udp_packet_loss_with, udp_jitter_with = extract_metrics(udp_with_mac_randomization, is_tcp=False)
udp_times_without, udp_bw_without, _, udp_packet_loss_without, udp_jitter_without = extract_metrics(udp_without_mac_randomization, is_tcp=False)

# Plot TCP Retransmissions Comparison
plt.figure(figsize=(12, 8))
plt.subplot(2, 1, 1)
plt.plot(tcp_times_with, tcp_retrans_with, marker='o', linestyle='-', color='r', label='TCP Retransmissions with MAC Randomization')
plt.plot(tcp_times_without, tcp_retrans_without, marker='o', linestyle='-', color='g', label='TCP Retransmissions without MAC Randomization')
plt.title('TCP Retransmissions Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Retransmissions')
plt.legend()
plt.grid(True)

# Plot UDP Packet Loss Comparison
#plt.subplot(3, 1, 2)
#plt.bar(['UDP with MAC Randomization', 'UDP without MAC Randomization'], [udp_packet_loss_with, udp_packet_loss_without], color=['r', 'g'])
#plt.title('UDP Packet Loss')
#plt.ylabel('Loss Percentage (%)')
#plt.grid(True)

# Plot UDP Jitter Comparison
plt.subplot(2, 1, 2)
plt.plot(udp_times_with, [udp_jitter_with] * len(udp_times_with), marker='o', linestyle='-', color='r', label='UDP Jitter with MAC Randomization')
plt.plot(udp_times_without, [udp_jitter_without] * len(udp_times_without), marker='o', linestyle='-', color='g', label='UDP Jitter without MAC Randomization')
plt.title('UDP Jitter Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Jitter (ms)')
plt.legend()
plt.grid(True)

plt.tight_layout()

# Save the plot as a PNG file
plt.savefig('/home/rathan/Downloads/hwsim_test/pics/tcp_udp_metrics_comparison.png')
plt.show()
