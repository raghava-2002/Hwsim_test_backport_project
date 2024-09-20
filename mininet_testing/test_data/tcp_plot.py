import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import numpy as np

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

# Function to clean data and apply spline interpolation for smoother curves
def smooth_curve(x, y):
    # Remove NaN and Inf values from the data
    mask = np.isfinite(x) & np.isfinite(y)  # Only take finite (non-NaN and non-Inf) values
    x_clean = x[mask]
    y_clean = y[mask]
    
    # Use the same number of points as in x_clean for interpolation
    num_points = len(x_clean)
    
    # Ensure there are enough points to apply spline interpolation
    if len(x_clean) > 2:  # At least 3 points are needed for cubic spline
        x_new = np.linspace(x_clean.min(), x_clean.max(), num_points)
        spline = make_interp_spline(x_clean, y_clean, k=3)  # Cubic spline
        y_smooth = spline(x_new)
        return x_new, y_smooth
    else:
        # Return the original data if there are not enough points for spline
        return x, y

# Provide the directory paths for each scheme
scheme_directories = {
    'AP Initiated': 'scheme_1/tcp',
    'Kernel Time': 'scheme_2/tcp',
    'No Randomization': 'scheme_3/tcp'
}

# Function to format y-axis labels in Mbps or Gbps
def format_bandwidth(y, pos):
    if y >= 1e9:
        return f'{y / 1e9:.4f} Gbps'
    else:
        return f'{y / 1e6:.4f} Mbps'

# Collect all data for comparison plots
comparison_bandwidth_data = {}
comparison_retransmissions_data = {}
seconds_data = None

# Plot separate graphs for each scheme and prepare comparison data
for scheme_name, directory in scheme_directories.items():
    scheme_data = []

    # Collect and store data from each station
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            station_data = load_json_file(filepath)
            scheme_data.append(station_data)

    # Convert list of DataFrames to a single DataFrame
    combined_data = pd.concat(scheme_data)
    
    # Group by time intervals and calculate the mean
    avg_data = combined_data.groupby('seconds').mean().reset_index()

    # Store seconds data for alignment (use it from the first scheme)
    if seconds_data is None:
        seconds_data = avg_data['seconds']
    
    # Align data by interpolating to match the 'seconds' index
    avg_data = avg_data.set_index('seconds').reindex(seconds_data).interpolate().reset_index()

    # Smooth the data using spline interpolation
    x_smooth, y_bandwidth_smooth = smooth_curve(avg_data['seconds'], avg_data['bits_per_second'])
    x_smooth, y_retrans_smooth = smooth_curve(avg_data['seconds'], avg_data['retransmits'].cumsum())

    # Store data for comparison plots
    comparison_bandwidth_data[scheme_name] = y_bandwidth_smooth
    comparison_retransmissions_data[scheme_name] = y_retrans_smooth

    # Increase the figure size
    plt.figure(figsize=(12, 8))  # Larger figure size for better x-axis spacing

    # Plot the average line with smooth curve
    plt.plot(x_smooth, y_bandwidth_smooth, color='black', linewidth=2, label='Average')

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
        x_smooth_station, y_smooth_station = smooth_curve(station_data['seconds'], station_data['retransmits'].cumsum())
        plt.plot(x_smooth_station, y_smooth_station, alpha=0.3)

    # Plot the average retransmissions with smooth curve
    plt.plot(x_smooth, y_retrans_smooth, color='black', linewidth=2, label='Average')

    plt.title(f'TCP Retransmissions over Time - {scheme_name}')
    plt.xlabel('Time (s)')
    plt.ylabel('Cumulative Retransmissions')
    plt.xticks(ticks=range(0, int(avg_data['seconds'].max()) + 1, 5))  # Set x-ticks every 5 seconds
    plt.legend()
    plt.grid(True)
    plt.savefig(f'plots/tcp/{scheme_name}_tcp_retransmissions.png')
    plt.clf()  # Clear the plot for the next scheme

# Create comparison plots

# Bandwidth comparison plot
plt.figure(figsize=(12, 8))
for scheme_name, bandwidth_data in comparison_bandwidth_data.items():
    x_smooth, y_bandwidth_smooth = smooth_curve(seconds_data, bandwidth_data)
    plt.plot(x_smooth, y_bandwidth_smooth, label=scheme_name)

plt.title('TCP Bandwidth Comparison Across Schemes')
plt.xlabel('Time (s)')
plt.ylabel('Bandwidth')
plt.xticks(ticks=range(0, int(seconds_data.max()) + 1, 4))  # Set x-ticks every 4 seconds
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_bandwidth))  # Format y-axis labels
plt.legend()
plt.grid(True)
plt.savefig('plots/tcp/comparison_tcp_bandwidth.png')
plt.clf()  # Clear the plot

# Retransmissions comparison plot
plt.figure(figsize=(12, 8))
for scheme_name, retransmissions_data in comparison_retransmissions_data.items():
    x_smooth, y_retrans_smooth = smooth_curve(seconds_data, retransmissions_data)
    plt.plot(x_smooth, y_retrans_smooth, label=scheme_name)

plt.title('TCP Retransmissions Comparison Across Schemes')
plt.xlabel('Time (s)')
plt.ylabel('Cumulative Retransmissions')
plt.xticks(ticks=range(0, int(seconds_data.max()) + 1, 5))  # Set x-ticks every 5 seconds
plt.legend()
plt.grid(True)
plt.savefig('plots/tcp/comparison_tcp_retransmissions.png')
plt.clf()  # Clear the plot
