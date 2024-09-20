import os
import json

# Function to analyze a single JSON file and extract relevant data for UDP
def analyze_udp_json_file(filepath):
    with open(filepath, 'r') as f:
        json_data = json.load(f)
        udp_summary = json_data['end']['sum']
        
        bytes_sent = udp_summary['bytes']
        packets_sent = udp_summary['packets']
        lost_packets = udp_summary['lost_packets']
        lost_percent = udp_summary['lost_percent']
        jitter_ms = udp_summary['jitter_ms']
        
        # Calculate average bandwidth in bits per second
        average_bandwidth_bps = (bytes_sent * 8) / udp_summary['seconds']  # Convert bytes to bits and divide by duration
        average_bandwidth_mbps = average_bandwidth_bps / 1e6  # Convert to Mbps

        # Return the analysis as a dictionary
        return {
            'station': os.path.basename(filepath),
            'total_bytes_sent': bytes_sent,
            'packets_sent': packets_sent,
            'lost_packets': lost_packets,
            'lost_percent': lost_percent,
            'jitter_ms': jitter_ms,
            'average_bandwidth_mbps': average_bandwidth_mbps  # Added average bandwidth for each station
        }

# Function to analyze a scheme for UDP
def analyze_udp_scheme(scheme_name, directory, description):
    results = []
    total_packets_sent = 0
    total_lost_packets = 0
    total_bytes_sent = 0
    test_duration = 60  # Duration of the test in seconds
    
    # Analyze each JSON file in the scheme directory
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            result = analyze_udp_json_file(filepath)
            results.append(result)
            total_packets_sent += result['packets_sent']
            total_lost_packets += result['lost_packets']
            total_bytes_sent += result['total_bytes_sent']
    
    # Calculate combined loss percentage
    if total_packets_sent > 0:
        combined_loss_percent = (total_lost_packets / total_packets_sent) * 100
    else:
        combined_loss_percent = 0
    
    # Convert total bytes to gigabytes
    total_gigabytes_sent = total_bytes_sent / (1024 ** 3)
    
    # Calculate average bandwidth in bits per second for the scheme
    average_bandwidth_bps = (total_bytes_sent * 8) / test_duration  # Convert bytes to bits and divide by time
    average_bandwidth_mbps = average_bandwidth_bps / 1e6  # Convert to Mbps
    
    # Write the analysis to a file
    output_filename = f'analysis/udp/{scheme_name}_analysis.txt'
    with open(output_filename, 'w') as f:
        f.write(f'UDP Analysis for {scheme_name}\n')
        f.write(f'Description: {description}\n')
        f.write('This analysis is done over 60 seconds with iperf3 at full power bandwidth.\n\n')
        f.write('=================================\n\n')
        
        for result in results:
            f.write(f"Station: {result['station']}\n")
            f.write(f"Total Bytes Sent: {result['total_bytes_sent']} bytes\n")
            f.write(f"Total Packets Sent: {result['packets_sent']}\n")
            f.write(f"Lost Packets: {result['lost_packets']}\n")
            f.write(f"Packet Loss Percentage: {result['lost_percent']:.4f}%\n")
            f.write(f"Jitter: {result['jitter_ms']:.3f} ms\n")
            f.write(f"Average Bandwidth: {result['average_bandwidth_mbps']:.4f} Mbps\n")  # Output average bandwidth
            f.write('---------------------------------\n')
        
        f.write('\nCombined Analysis:\n')
        f.write(f"Total Bytes Sent: {total_bytes_sent} bytes ({total_gigabytes_sent:.4f} GB)\n")
        f.write(f"Total Packets Sent: {total_packets_sent}\n")
        f.write(f"Total Lost Packets: {total_lost_packets}\n")
        f.write(f"Combined Packet Loss Percentage: {combined_loss_percent:.4f}%\n")
        f.write(f"Average Bandwidth for Scheme: {average_bandwidth_mbps:.4f} Mbps\n")
    
    print(f'UDP Analysis for {scheme_name} saved to {output_filename}')


# Provide the directory paths for each scheme with descriptions
scheme_directories = {
    'Scheme 1': ('scheme_1/udp', 'Mac randomization by the AP initiated triggers'),
    'Scheme 2': ('scheme_2/udp', 'Mac randomization by internal kernel time'),
    'Scheme 3': ('scheme_3/udp', 'Without Mac randomization')
}

# Analyze each scheme
for scheme_name, (directory, description) in scheme_directories.items():
    analyze_udp_scheme(scheme_name, directory, description)
