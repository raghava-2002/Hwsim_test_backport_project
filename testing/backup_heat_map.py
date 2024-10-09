#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np

# Centralized Parameters
TX_POWER = 14      # Transmission power (in dBm)
PL_D0 = 36.513         # Reference path loss at distance d0 (as of now 36.513 is matching with the mininet simulation)
PATH_LOSS_EXP = 4  # Path loss exponent (n)
X_RANGE = 120       # Range of X-axis in meters
Y_RANGE = 120       # Range of Y-axis in meters

def calculate_path_loss(d, d0=1, pl_d0=PL_D0, n=PATH_LOSS_EXP):
    """Calculate path loss based on log-distance path loss model."""
    if d < d0:
        d = d0  # Ensure d is not smaller than d0 to avoid negative log values
    return pl_d0 + 10 * n * np.log10(d / d0)

def calculate_rssi(tx_power, path_loss):
    """Calculate RSSI based on TX power and path loss."""
    return tx_power - path_loss  # RSSI is TX power minus path loss

def create_heat_map(ap_pos, grid_size=(X_RANGE, Y_RANGE), resolution=1): # change resolution to 0.1 for the sommoth heat map but take more time to plot
    """Create a heat map grid showing signal strength from the AP."""
    x_range = np.arange(0, grid_size[0], resolution)
    y_range = np.arange(0, grid_size[1], resolution)
    
    # Create grid for heat map
    heat_map = np.zeros((len(y_range), len(x_range)))
    
    for i, x in enumerate(x_range):
        for j, y in enumerate(y_range):
            distance = np.sqrt((x - ap_pos[0])**2 + (y - ap_pos[1])**2)
            path_loss = calculate_path_loss(distance)
            heat_map[j, i] = calculate_rssi(TX_POWER, path_loss)
    
    return heat_map, x_range, y_range

def plot_heat_map_and_stations(ap1_pos, station_positions):
    """Function to plot heat map and station positions with RSSI values."""
    # Create the heat map
    heat_map, x_range, y_range = create_heat_map(ap1_pos)

    # Define station colors and markers for the plot
    station_colors = ['blue', 'green', 'orange', 'purple', 'pink']
    station_symbols = ['o', 's', '^', 'D', '*']
    
    # Plot the heat map
    plt.figure(figsize=(10, 10))
    plt.title("AP Heat Map with Station Positions (Path Loss EXP: 4)")
    plt.xlabel("X Position (meters)")
    plt.ylabel("Y Position (meters)")
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.6)

    # Display heat map using imshow with 'Blues' color scale
    im = plt.imshow(heat_map, extent=(0, 120, 0, 120), origin='lower', cmap='jet', alpha=0.6)
    
    # Add color bar to show signal strength scale
    cbar = plt.colorbar(im)
    cbar.set_label('Signal Strength (dBm)')

    # Plot the AP as a red triangle
    plt.scatter(ap1_pos[0], ap1_pos[1], s=50, c='red', marker='^', label='AP TX Power: 14 dBm')

    # Print RSSI at each station and plot them
    for i, (sta_name, sta_pos) in enumerate(station_positions.items()):
        color = station_colors[i % len(station_colors)]
        symbol = station_symbols[i % len(station_symbols)]
        distance = np.sqrt((sta_pos[0] - ap1_pos[0])**2 + (sta_pos[1] - ap1_pos[1])**2)
        path_loss = calculate_path_loss(distance)
        rssi = calculate_rssi(TX_POWER, path_loss)
        print(f"RSSI at {sta_name} (distance: {distance:.2f} m): {rssi:.2f} dBm")

        # Plot the station
        plt.scatter(sta_pos[0], sta_pos[1], s=50, c=color, marker=symbol, label=f'{sta_name.upper()} (RSSI: {rssi:.2f} dBm)')
        plt.text(sta_pos[0], sta_pos[1]+1.5, sta_name.upper(), fontsize=10, ha='center', va='bottom')

    # Add the legend in the upper corner
    plt.legend(loc='upper right')
    plt.xlim(10, 100)  # Zoom in from x=10 to x=120
    plt.ylim(30, 100)  # Zoom in from y=10 to y=120

    # Show the plot and save it
    plt.savefig('/home/rathan/Downloads/hwsim_test/testing/heat_map_with_stations.png', bbox_inches='tight')  # Save the figure to a file

# Main code to run the plotting function with manual positions
if __name__ == '__main__':
    # Manually define the AP and STA positions
    ap1_pos = (60, 60)  # AP at (60, 60)
    station_positions = {
        'sta1': (62, 60),  # Station 1 at (62, 60)
        'sta2': (64.95, 64.95),  # Station 2 at (64.95, 64.95)
        'sta3': (60, 75),  # Station 3 at (60, 75)
        'sta4': (42.68, 77.32),  # Station 4 at (42.68, 77.32)
        'sta5': (25, 60)   # Station 5 at (25, 60)
    }

    # Call the plotting function
    plot_heat_map_and_stations(ap1_pos, station_positions)
