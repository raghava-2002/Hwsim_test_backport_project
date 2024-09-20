import os
import json
import pandas as pd
import matplotlib.pyplot as plt

# Function to load a single JSON file and extract relevant data
def load_json_file(filepath):
    data = []
    with open(filepath, 'r') as f:
        json_data = json.load(f)
        # Extract bandwidth and retransmissions
        intervals = json_data['intervals']
        for interval in intervals:
            sum_data = interval['sum']
            data.append({
                'seconds': sum_data['end'],
                'bits_per_second': sum_data['bits_per_second'],
                'retransmits': sum_data['retransmits']
            })
    return pd.DataFrame(data)

# Provide the directory paths for each scheme
scheme_directories = {
    'Scheme 1': 'scheme_1/tcp',
    'Scheme 2': 'scheme_2/tcp',
    'Scheme 3': 'scheme_3/tcp'
}

# Function to format y-axis labels in Mbps or Gbps
def format_bandwidth(y, pos):
    if y >= 1e9:
        return f'{y / 1e9:.4f} Gbps'
    else:
        return f'{y / 1e6:.4f} Mbps'

# Plot separate graphs for each scheme
for scheme_name, directory in scheme_directories.items():
    scheme_data = []

    # Collect and store data from each station
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            station_data = load_json_file(filepath)
            scheme_data.append(station_data)
            plt.plot(station_data['seconds'], station_data['bits_per_second'], alpha=0.3, label=f'{filename}')

    # Convert list of DataFrames to a single DataFrame
    combined_data = pd.concat(scheme_data)
    
    # Group by time intervals and calculate the mean
    avg_data = combined_data.groupby('seconds').mean().reset_index()

    # Increase the figure size
    plt.figure(figsize=(12, 8))  # Larger figure size for better x-axis spacing

    # Plot the average line
    plt.plot(avg_data['seconds'], avg_data['bits_per_second'], color='black', linewidth=2, label='Average')

    plt.title(f'TCP Bandwidth over Time - {scheme_name}')
    plt.xlabel('Time (s)')
    plt.ylabel('Bandwidth')
    plt.xticks(ticks=range(0, int(avg_data['seconds'].max()) + 1, 4))  # Set x-ticks every 4 seconds
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_bandwidth))  # Format y-axis labels
    plt.legend()
    plt.grid(True)
    plt.savefig(f'plots/tcp/{scheme_name}_tcp_bandwidth.png')
    plt.clf()  # Clear the plot for the next scheme

    # Plot Retransmissions over Time for the scheme
    plt.figure(figsize=(12, 8))  # Larger figure size for better x-axis spacing

    for station_data in scheme_data:
        plt.plot(station_data['seconds'], station_data['retransmits'].cumsum(), alpha=0.3)

    # Plot the average retransmissions
    plt.plot(avg_data['seconds'], avg_data['retransmits'].cumsum(), color='black', linewidth=2, label='Average')

    plt.title(f'TCP Retransmissions over Time - {scheme_name}')
    plt.xlabel('Time (s)')
    plt.ylabel('Cumulative Retransmissions')
    plt.xticks(ticks=range(0, int(avg_data['seconds'].max()) + 1, 5))  # Set x-ticks every 5 seconds
    plt.legend()
    plt.grid(True)
    plt.savefig(f'plots/tcp/{scheme_name}_tcp_retransmissions.png')
    plt.clf()  # Clear the plot for the next scheme


