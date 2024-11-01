import numpy as np
import matplotlib.pyplot as plt

# Function to plot a smoother normal distribution and generate time drifts for specified stations
def generate_smooth_time_drift_distribution(num_samples=50000, mean_drift=0, std_dev_drift=4, drift_range=(-10, 10)):
    # Generate more data points for smoother time drift values within the specified normal distribution and limit to the drift range
    time_drifts = np.random.normal(loc=mean_drift, scale=std_dev_drift, size=num_samples)
    time_drifts = np.clip(time_drifts, drift_range[0], drift_range[1])

    # Plotting the distribution of time drifts with more data points for a smoother curve
    plt.figure(figsize=(10, 6))
    count, bins, ignored = plt.hist(time_drifts, bins=50, color='skyblue', edgecolor='black', density=True)
    plt.plot(bins, 1/(std_dev_drift * np.sqrt(2 * np.pi)) * np.exp(- (bins - mean_drift)**2 / (2 * std_dev_drift**2)), 
             linewidth=2, color='orange')  # Adding smooth distribution curve

    # Labeling the plot
    plt.title(f"Normal Distribution of Time Drift Values ({drift_range[0]} to {drift_range[1]} ms)")
    plt.xlabel("Time Drift (ms)")
    plt.ylabel("Density")
    plt.grid(axis='y', alpha=0.75)
    plt.savefig('time_drift_distribution.png')

    # Function to get specified number of time drifts for stations
    def get_station_drifts(num_stations):
        return np.random.choice(time_drifts, size=num_stations, replace=False)

    return get_station_drifts

# Generate the smoother distribution plot and prepare to retrieve time drift values
get_smooth_station_drifts = generate_smooth_time_drift_distribution()

# Example usage: Retrieve time drift values for 3 stations
smooth_station_drifts = get_smooth_station_drifts(11)
smooth_station_drifts_ns = (smooth_station_drifts * 1e6).astype(int)  # Convert to nanoseconds
print(smooth_station_drifts_ns)
