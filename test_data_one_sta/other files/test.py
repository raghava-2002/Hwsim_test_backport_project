import json
import os
import matplotlib.pyplot as plt

# Define the directory where your JSON files are located
data_dir = '/home/rathan/Downloads/hwsim_test/test_data'

# Function to load JSON data
def load_json(file_name):
    with open(os.path.join(data_dir, file_name), 'r') as file:
        return json.load(file)

# File names
files = {
    'without_randomization_tcp': 'without_randomization_tcp.json',
    'kernel_time_randomization_tcp': 'kernel_time_randomization_tcp.json',
    'ap_triggered_randomization_tcp': 'ap_triggered_randomization_tcp.json',
    'without_randomization_udp': 'without_randomization_udp.json',
    'kernel_time_randomization_udp': 'kernel_time_randomization_udp.json',
    'ap_triggered_randomization_udp': 'ap_triggered_randomization_udp.json'
}

# Load data from files
data = {name: load_json(file_name) for name, file_name in files.items()}

# Function to extract TCP metrics
def extract_tcp_metrics(data):
    times = []
    bandwidths = []
    retransmissions = []
    for interval in data['intervals']:
        times.append(interval['sum']['end'])
        bandwidths.append(interval['sum']['bits_per_second'])
        retransmissions.append(interval['sum']['retransmits'])
    return times, bandwidths, retransmissions

# Function to extract UDP metrics
def extract_udp_metrics(data):
    times = []
    bandwidths = []
    jitter = []
    packet_loss = data['end']['sum']['lost_percent']
    for interval in data['intervals']:
        times.append(interval['sum']['end'])
        bandwidths.append(interval['sum']['bits_per_second'])
        jitter.append(interval['sum'].get('jitter_ms', 0))
    return times, bandwidths, jitter, packet_loss

# Extract metrics
tcp_metrics = {name: extract_tcp_metrics(data[name]) for name in ['without_randomization_tcp', 'kernel_time_randomization_tcp', 'ap_triggered_randomization_tcp']}
udp_metrics = {name: extract_udp_metrics(data[name]) for name in ['without_randomization_udp', 'kernel_time_randomization_udp', 'ap_triggered_randomization_udp']}

# Plot TCP Bandwidth Over Time
plt.figure(figsize=(10, 6))
for name, (times, bandwidths, _) in tcp_metrics.items():
    plt.plot(times, bandwidths, label=name.replace('_', ' ').title())
plt.title('TCP Bandwidth Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Bandwidth (bits per second)')
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(data_dir, 'tcp_bandwidth_comparison.png'))
plt.show()

# Plot TCP Retransmissions Over Time
plt.figure(figsize=(10, 6))
for name, (times, _, retransmissions) in tcp_metrics.items():
    plt.plot(times, retransmissions, label=name.replace('_', ' ').title())
plt.title('TCP Retransmissions Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Retransmissions')
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(data_dir, 'tcp_retransmissions_comparison.png'))
plt.show()

# Plot UDP Bandwidth Over Time
plt.figure(figsize=(10, 6))
for name, (times, bandwidths, _, _) in udp_metrics.items():
    plt.plot(times, bandwidths, label=name.replace('_', ' ').title())
plt.title('UDP Bandwidth Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Bandwidth (bits per second)')
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(data_dir, 'udp_bandwidth_comparison.png'))
plt.show()

# Plot UDP Jitter Over Time
plt.figure(figsize=(10, 6))
for name, (times, _, jitter, _) in udp_metrics.items():
    plt.plot(times, jitter, label=name.replace('_', ' ').title())
plt.title('UDP Jitter Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Jitter (ms)')
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(data_dir, 'udp_jitter_comparison.png'))
plt.show()

# Plot UDP Packet Loss Comparison
plt.figure(figsize=(10, 6))
packet_loss_values = [udp_metrics[name][3] for name in udp_metrics]
scheme_labels = [name.replace('_', ' ').title() for name in udp_metrics]
plt.bar(scheme_labels, packet_loss_values)
plt.title('UDP Packet Loss Comparison')
plt.ylabel('Packet Loss (%)')
plt.grid(True)
plt.savefig(os.path.join(data_dir, 'udp_packet_loss_comparison.png'))
plt.show()
