import matplotlib.pyplot as plt
import numpy as np
import math

# Parameters based on Mininet ITU model configuration
TX_POWER = 14        # Transmission power (in dBm)
FREQUENCY = 2.4e3     # Frequency in MHz for 2.4 GHz band (converted to kHz)
FLOOR_LOSS_FACTOR = 1  # Floor penetration loss factor (based on Mininet setup)
N_FLOORS = 1          # Number of floors
DIST_THRESHOLD = 35   # Distance threshold for switching path loss coefficient
PATH_LOSS_EXP_CLOSE = 22
PATH_LOSS_EXP_FAR = 32
X_RANGE = 120         # Range of X-axis in meters
Y_RANGE = 120         # Range of Y-axis in meters

def calculate_path_loss_itu(dist, n_floors=N_FLOORS, floor_loss=FLOOR_LOSS_FACTOR):
    """Calculate path loss using a refined ITU-based model to simulate Mininet."""
    if dist < 1:
        dist = 1  # Avoid log(0) error
    N = PATH_LOSS_EXP_CLOSE if dist <= DIST_THRESHOLD else PATH_LOSS_EXP_FAR
    # Path loss calculation based on frequency, distance, and floor loss factors
    pldb = 20 * math.log10(FREQUENCY) + N * math.log10(dist) + floor_loss * n_floors - 28
    return pldb

def calculate_rssi(tx_power, path_loss):
    """Calculate RSSI based on TX power and path loss."""
    return tx_power - path_loss

def create_heat_map(ap_pos, grid_size=(X_RANGE, Y_RANGE), resolution=1):  # Use resolution=0.5 for finer detail
    """Create a heat map grid showing signal strength from the AP."""
    x_range = np.arange(0, grid_size[0], resolution)
    y_range = np.arange(0, grid_size[1], resolution)
    
    # Create grid for heat map
    heat_map = np.zeros((len(y_range), len(x_range)))
    
    for i, x in enumerate(x_range):
        for j, y in enumerate(y_range):
            distance = np.sqrt((x - ap_pos[0])**2 + (y - ap_pos[1])**2)
            path_loss = calculate_path_loss_itu(distance)
            heat_map[j, i] = calculate_rssi(TX_POWER, path_loss)
    
    return heat_map, x_range, y_range

def plot_heat_map_and_stations(ap1_pos, station_positions, fixed_rssi_values=None):
    """Function to plot heat map and station positions with RSSI values based on refined ITU model."""
    # Create the heat map
    heat_map, x_range, y_range = create_heat_map(ap1_pos, resolution=0.5)

    # Plot the heat map
    plt.figure(figsize=(10, 10))
    plt.title("AP Heat Map with Station Positions (ITU Model, Refined for Mininet)")
    plt.xlabel("X Position (meters)")
    plt.ylabel("Y Position (meters)")
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.6)

    # Display heat map using imshow with 'jet' color scale
    im = plt.imshow(heat_map, extent=(0, X_RANGE, 0, Y_RANGE), origin='lower', cmap='jet', alpha=0.6)
    
    # Add color bar to show signal strength scale
    cbar = plt.colorbar(im)
    cbar.set_label('Signal Strength (dBm)')

    # Plot the AP as a red triangle
    plt.scatter(ap1_pos[0], ap1_pos[1], s=50, c='red', marker='^', label='AP TX Power: 14 dBm')

    # Print RSSI at each station and plot them
    for i, (sta_name, sta_pos) in enumerate(station_positions.items()):
        distance = np.sqrt((sta_pos[0] - ap1_pos[0])**2 + (sta_pos[1] - ap1_pos[1])**2)
        path_loss = calculate_path_loss_itu(distance)
        rssi = calculate_rssi(TX_POWER, path_loss)
        print(f"RSSI at {sta_name} (distance: {distance:.2f} m): {rssi:.2f} dBm")

        # Plot the station
        plt.scatter(sta_pos[0], sta_pos[1], s=100, c='blue', marker='o', label=f'{sta_name.upper()} (RSSI: {rssi:.2f} dBm)')
        plt.text(sta_pos[0], sta_pos[1]+1.5, f'{sta_name.upper()} ({rssi:.2f} dBm)', fontsize=9, ha='center', va='bottom')

    # Add the legend in the upper corner
    plt.legend(loc='upper right')
    plt.xlim(0, X_RANGE)  # Set limits based on the defined grid range
    plt.ylim(0, Y_RANGE)

    # Show the plot and save it
    plt.savefig('heat_map_mininet_itu_refined.png', bbox_inches='tight')
    plt.show()

# Main code to run the plotting function with manual positions
if __name__ == '__main__':
    # Set AP at (70, 70)
    ap1_pos = (70, 70)

    # Define station positions as per Mininet example
    station_positions = {
        'sta1': (71.0, 70.0),
        'sta2': (64.18, 75.34),
        'sta3': (71.29, 55.26),
        'sta4': (83.21, 87.22),
        'sta5': (41.83, 65.03),
        'sta6': (99.94, 50.93),
        'sta7': (59.03, 110.96),
        'sta8': (47.24, 26.27),
        'sta9': (122.81, 89.22),
        'sta10': (11.70, 94.15),
        'sta11': (99.58, 6.56)
    }

    # Define fixed RSSI values from Mininet measurements for reference
    fixed_rssi_values = {
        'sta1': -15.0,
        'sta2': -30.0,
        'sta3': -39.0,
        'sta4': -42.0,
        'sta5': -48.0,
        'sta6': -63.0,
        'sta7': -64.0,
        'sta8': -66.0,
        'sta9': -68.0,
        'sta10': -70.0,
        'sta11': -85.0
    }

    # Call the plotting function
    plot_heat_map_and_stations(ap1_pos, station_positions, fixed_rssi_values)
