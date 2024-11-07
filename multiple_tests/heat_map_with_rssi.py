import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import Rbf

# Parameters
X_RANGE = 140
Y_RANGE = 120
RESOLUTION = 0.5  # Fine resolution for smoothness

# AP position
ap1_pos = (70, 70)

# Provided Mininet RSSI values for each station
mininet_rssi_values = {
    'sta1': -15.0,
    'sta2': -41.0,
    'sta3': -48.0,
    'sta4': -67.0,
    'sta5': -71.0,
    'sta6': -75.0,
    'sta7': -78.0,
    'sta8': -80.0,
    'sta9': -82.0,
    'sta10': -84.0,
    'sta11': -86.0
}

# Station positions as per your Mininet setup
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

# Convert station positions and RSSI values into arrays for RBF interpolation
station_coords = np.array([station_positions[sta] for sta in mininet_rssi_values.keys()])
rssi_values = np.array([mininet_rssi_values[sta] for sta in mininet_rssi_values.keys()])
x_coords = station_coords[:, 0]
y_coords = station_coords[:, 1]

# Create grid for interpolation
x_range = np.arange(0, X_RANGE, RESOLUTION)
y_range = np.arange(0, Y_RANGE, RESOLUTION)
X, Y = np.meshgrid(x_range, y_range)

# Apply RBF interpolation to create a smooth RSSI spread
rbf_interpolator = Rbf(x_coords, y_coords, rssi_values, function='multiquadric', smooth=1)
Z = rbf_interpolator(X, Y)

# Plot the heat map
plt.figure(figsize=(10, 10))
plt.title("RSSI Heat Map Based on Mininet Observed Values (Focused Range)")
plt.xlabel("X Position (meters)")
plt.ylabel("Y Position (meters)")
plt.grid(True)

# Display heat map with restricted color scale from -90 to -110 dBm
im = plt.imshow(Z, extent=(0, X_RANGE, 0, Y_RANGE), origin='lower', cmap='jet', alpha=0.7, vmin=-110, vmax=-90)
cbar = plt.colorbar(im)
cbar.set_label('Signal Strength (dBm)')

# Plot the AP as a transmitter icon
plt.scatter(ap1_pos[0], ap1_pos[1], s=300, c='black', marker='P', label='AP (Transmitter)')

# Plot each station with the Mininet RSSI values for reference
for sta_name, sta_pos in station_positions.items():
    rssi = mininet_rssi_values[sta_name]
    plt.scatter(sta_pos[0], sta_pos[1], s=100, c='blue', marker='o', label=f'{sta_name.upper()} (RSSI: {rssi} dBm)')
    plt.text(sta_pos[0], sta_pos[1]+1.5, f'{sta_name.upper()} ({rssi} dBm)', fontsize=9, ha='center', va='bottom')

# Add legend and save the plot
#plt.legend(loc='upper right')
plt.savefig('rssi_heat_map_mininet_rbf_truncated.png', bbox_inches='tight')
plt.show()
