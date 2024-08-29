import os
import json

# Function to analyze a single JSON file and extract relevant data
def analyze_json_file(filepath):
    with open(filepath, 'r') as f:
        json_data = json.load(f)
        sum_sent = json_data['end']['sum_sent']
        
        bytes_sent = sum_sent['bytes']
        retransmits = sum_sent['retransmits']
        
        # Calculate total packets sent (assuming each packet is 1500 bytes)
        total_packets_sent = bytes_sent / 1500
        
        # Calculate retransmission percentage
        if total_packets_sent > 0:
            retransmission_percentage = (retransmits / total_packets_sent) * 100
        else:
            retransmission_percentage = 0
        
        # Return the analysis as a dictionary
        return {
            'station': os.path.basename(filepath),
            'total_bytes_sent': bytes_sent,
            'total_packets_sent': total_packets_sent,
            'retransmits': retransmits,
            'retransmission_percentage': retransmission_percentage
        }

# Function to analyze a scheme
def analyze_scheme(scheme_name, directory, description):
    results = []
    total_packets_sent = 0
    total_retransmits = 0
    total_bytes_sent = 0
    
    # Analyze each JSON file in the scheme directory
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            result = analyze_json_file(filepath)
            results.append(result)
            total_packets_sent += result['total_packets_sent']
            total_retransmits += result['retransmits']
            total_bytes_sent += result['total_bytes_sent']
    
    # Calculate combined retransmission percentage
    if total_packets_sent > 0:
        combined_retransmission_percentage = (total_retransmits / total_packets_sent) * 100
    else:
        combined_retransmission_percentage = 0
    
    # Convert total bytes to gigabytes
    total_gigabytes_sent = total_bytes_sent / (1024 ** 3)
    
    # Write the analysis to a file
    output_filename = f'{scheme_name}_analysis.txt'
    with open(output_filename, 'w') as f:
        f.write(f'Analysis for {scheme_name}\n')
        f.write(f'Description: {description}\n')
        f.write('This analysis is done over 60 seconds with iperf3 at full power bandwidth.\n\n')
        f.write('=================================\n\n')
        
        for result in results:
            f.write(f"Station: {result['station']}\n")
            f.write(f"Total Bytes Sent: {result['total_bytes_sent']} bytes\n")
            f.write(f"Total Packets Sent: {result['total_packets_sent']}\n")
            f.write(f"Retransmits: {result['retransmits']}\n")
            f.write(f"Retransmission Percentage: {result['retransmission_percentage']:.2f}%\n")
            f.write('---------------------------------\n')
        
        f.write('\nCombined Analysis:\n')
        f.write(f"Total Bytes Sent: {total_bytes_sent} bytes ({total_gigabytes_sent:.2f} GB)\n")
        f.write(f"Total Packets Sent: {total_packets_sent}\n")
        f.write(f"Total Retransmits: {total_retransmits}\n")
        f.write(f"Combined Retransmission Percentage: {combined_retransmission_percentage:.2f}%\n")
    
    print(f'Analysis for {scheme_name} saved to {output_filename}')

# Provide the directory paths for each scheme with descriptions
scheme_directories = {
    'Scheme 1': ('scheme_1/tcp', 'Mac randomization by the AP initiated triggers'),
    'Scheme 2': ('scheme_2/tcp', 'Mac randomization by internal kernel time'),
    'Scheme 3': ('scheme_3/tcp', 'Without Mac randomization')
}

# Analyze each scheme
for scheme_name, (directory, description) in scheme_directories.items():
    analyze_scheme(scheme_name, directory, description)
