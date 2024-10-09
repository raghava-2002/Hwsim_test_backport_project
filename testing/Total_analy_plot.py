import os
import json
import pandas as pd

# Function to analyze a single TCP JSON file
def analyze_tcp_json_file(filepath):
    with open(filepath, 'r') as f:
        json_data = json.load(f)
        
        # Extracting the final throughput and retransmission data from the "end" section
        sum_sent = json_data['end']['sum_sent']

        bytes_sent = sum_sent['bytes']  # Total bytes sent
        retransmits = sum_sent['retransmits']  # Total retransmits
        bits_per_second = sum_sent['bits_per_second']  # Throughput in bits per second

        # Convert bits per second to Mbps
        average_bandwidth_mbps = bits_per_second / 1e6

        # Calculate total packets sent (assuming each packet is 1500 bytes)
        total_packets_sent = bytes_sent / 1500

        # Calculate retransmission percentage
        retransmission_percentage = (retransmits / total_packets_sent) * 100 if total_packets_sent > 0 else 0

        # Return the analysis as a dictionary
        return {
            'station': os.path.basename(filepath),
            'total_bytes_sent': bytes_sent,
            'total_packets_sent': total_packets_sent,
            'retransmits': retransmits,
            'retransmission_percentage': retransmission_percentage,
            'average_bandwidth_mbps': average_bandwidth_mbps
        }

# Function to analyze a single UDP JSON file
def analyze_udp_json_file(filepath):
    with open(filepath, 'r') as f:
        json_data = json.load(f)
        
        # Extracting the final UDP results from the "end" section
        sum_received = json_data['end']['sum']

        bits_per_second = sum_received['bits_per_second']  # Throughput in bits per second
        jitter_ms = sum_received.get('jitter_ms', 0)  # Jitter in milliseconds
        lost_percent = sum_received.get('lost_percent', 0)  # Packet loss percentage

        # Convert bits per second to Mbps
        average_bandwidth_mbps = bits_per_second / 1e6

        # Return the analysis as a dictionary
        return {
            'station': os.path.basename(filepath),
            'average_bandwidth_mbps': average_bandwidth_mbps,
            'jitter_ms': jitter_ms,
            'packet_loss_percent': lost_percent
        }

# Function to analyze all TCP and UDP results for each station
def analyze_schemes(output_file, scheme_directories):
    with open(output_file, 'w') as f:
        f.write("Comprehensive Analysis for All Stations and Schemes\n")
        f.write("==============================================\n\n")
        
        for scheme_name, (tcp_dir, udp_dir) in scheme_directories.items():
            f.write(f"Scheme: {scheme_name}\n")
            f.write("---------------------------------\n\n")

            # Analyze TCP results
            f.write("TCP Analysis (Per Station)\n")
            f.write("---------------------------\n")
            
            for filename in sorted(os.listdir(tcp_dir)):
                if filename.endswith('.json'):
                    filepath = os.path.join(tcp_dir, filename)
                    result = analyze_tcp_json_file(filepath)

                    f.write(f"Station: {result['station']}\n")
                    f.write(f"  Total Bytes Sent: {result['total_bytes_sent']} bytes\n")
                    f.write(f"  Total Packets Sent: {result['total_packets_sent']}\n")
                    f.write(f"  Retransmits: {result['retransmits']}\n")
                    f.write(f"  Retransmission Percentage: {result['retransmission_percentage']:.4f}%\n")
                    f.write(f"  Average Bandwidth: {result['average_bandwidth_mbps']:.4f} Mbps\n")
                    f.write('---------------------------------\n')

            # Analyze UDP results
            f.write("\nUDP Analysis (Per Station)\n")
            f.write("----------------------------\n")
            
            for filename in sorted(os.listdir(udp_dir)):
                if filename.endswith('.json'):
                    filepath = os.path.join(udp_dir, filename)
                    result = analyze_udp_json_file(filepath)

                    f.write(f"Station: {result['station']}\n")
                    f.write(f"  Average Bandwidth: {result['average_bandwidth_mbps']:.4f} Mbps\n")
                    f.write(f"  Jitter: {result['jitter_ms']:.4f} ms\n")
                    f.write(f"  Packet Loss: {result['packet_loss_percent']:.4f}%\n")
                    f.write('---------------------------------\n')

    print(f'Comprehensive analysis saved to {output_file}')

# Scheme directories for TCP and UDP results
scheme_directories = {
    'Scheme 1': (
        '/home/rathan/Downloads/hwsim_test/testing/iperf3_results/scheme_1/test_1/tcp', 
        '/home/rathan/Downloads/hwsim_test/testing/iperf3_results/scheme_1/test_1/udp'
    ),
    'Scheme 2': (
        '/home/rathan/Downloads/hwsim_test/testing/iperf3_results/scheme_2/test_1/tcp', 
        '/home/rathan/Downloads/hwsim_test/testing/iperf3_results/scheme_2/test_1/udp'
    ),
    'Scheme 3': (
        '/home/rathan/Downloads/hwsim_test/testing/iperf3_results/scheme_3/test_1/tcp', 
        '/home/rathan/Downloads/hwsim_test/testing/iperf3_results/scheme_3/test_1/udp'
    )
}





# Output file for the analysis results
output_file = '/home/rathan/Downloads/hwsim_test/testing/iperf3_results/comprehensive_analysis.txt'

# Run the analysis
analyze_schemes(output_file, scheme_directories)

