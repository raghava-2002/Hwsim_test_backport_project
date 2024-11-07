import numpy as np
import matplotlib.pyplot as plt

# Original data dictionary
data = {
    "ap1": [[None, 0], [2.97, 15], [2.86, 12], [2.84, 15], [2.84, 56], [2.78, 19], [4.76, 13], [5.41, 22], [2.91, 23], [2.71, 9], [2.74, 21], [2.55, 9]],
    "sta1": [[3.82, 30], [None, 0], [1.57, 65], [1.67, 77], [3.97, 59], [1.98, 37], [1.49, 50], [1.55, 41], [1.44, 66], [1.48, 23], [1.53, 61], [1.45, 74]],
    "sta2": [[3.76, 27], [1.46, 67], [None, 0], [1.69, 68], [4.09, 75], [2.22, 71], [1.49, 89], [1.53, 95], [1.56, 80], [1.54, 70], [1.43, 87], [1.57, 66]],
    "sta3": [[3.66, 37], [1.5, 100], [1.51, 99], [None, 0], [1.59, 116], [2.33, 170], [4.05, 93], [1.83, 39], [1.48, 69], [1.54, 83], [1.46, 53], [1.57, 75]],
    "sta4": [[3.8, 54], [1.53, 130], [1.54, 87], [1.49, 87], [None, 0], [1.6, 86], [1.6, 71], [1.64, 29], [1.74, 87], [1.75, 60], [1.49, 64], [2.1, 55]],
    "sta5": [[4.71, 56], [2.29, 28], [1.42, 71], [1.49, 61], [1.49, 82], [None, 0], [1.57, 73], [1.45, 66], [1.46, 29], [1.69, 59], [3.48, 6], [1.53, 88]],
    "sta6": [[3.18, 18], [1.4, 56], [1.39, 22], [1.45, 46], [1.41, 45], [2.03, 48], [None, 0], [2.53, 4], [1.52, 21], [1.44, 35], [2.61, 18], [1.66, 95]],
    "sta7": [[3.48, 67], [1.58, 81], [1.65, 126], [1.64, 117], [1.54, 57], [1.58, 33], [1.56, 58], [None, 0], [1.63, 71], [1.64, 159], [1.73, 112], [1.56, 99]],
    "sta8": [[2.78, 44], [1.28, 23], [1.27, 5], [1.3, 0], [1.29, 28], [1.34, 4], [1.32, 19], [1.35, 35], [None, 0], [1.27, 1], [1.29, 14], [1.24, 12]],
    "sta9": [[3.45, 101], [1.62, 81], [1.6, 88], [1.76, 150], [1.56, 87], [1.59, 78], [1.64, 118], [1.64, 119], [1.58, 45], [None, 0], [1.73, 96], [1.62, 45]],
    "sta10": [[2.87, 16], [1.29, 15], [1.34, 47], [1.38, 14], [1.3, 57], [1.25, 1], [1.31, 31], [1.35, 33], [1.34, 25], [1.34, 1], [None, 0], [1.3, 4]],
    "sta11": [[3.41, 29], [1.5, 31], [1.55, 77], [1.52, 15], [1.48, 32], [1.56, 12], [1.62, 87], [1.48, 93], [1.48, 69], [1.5, 53], [1.41, 33], [None, 0]]
}

# Separate throughput and retransmissions data, filling None with 0 for self-transfers
stations = list(data.keys())
throughput_data = np.array([[entry[0] if entry[0] is not None else 0 for entry in row] for row in data.values()])
retransmissions_data = np.array([[entry[1] for entry in row] for row in data.values()])

# Convert throughput from Mbps to KBps (1 Mbps = 125 KBps)
throughput_kbps = throughput_data * 125

# Plot throughput heatmap
plt.figure(figsize=(10, 8))
plt.imshow(throughput_kbps, cmap="YlGnBu", aspect="auto")
cbar = plt.colorbar()
cbar.set_label("Throughput (KBps)", fontsize=16)  # Set label with increased font size
cbar.ax.tick_params(labelsize=14)  # Increase font size for color bar ticks
plt.title("Heatmap of Throughput Between Stations (KBps)", fontsize=16)
plt.xticks(ticks=np.arange(len(stations)), labels=stations, rotation=45)
plt.yticks(ticks=np.arange(len(stations)), labels=stations)
plt.xlabel("Receiving Stations", fontsize=16)
plt.ylabel("Transmitting Stations", fontsize=16)
plt.xticks(fontsize=14)  # Increase font size for x-axis tick labels
plt.yticks(fontsize=14)  # Increase font size for y-axis tick labels
plt.savefig("throughput_heatmap_kbps.pdf", format="pdf", bbox_inches="tight")
plt.close()

# Plot retransmissions heatmap
plt.figure(figsize=(10, 8))
plt.imshow(retransmissions_data, cmap="YlOrRd", aspect="auto")
cbar = plt.colorbar()
cbar.set_label("Retransmissions", fontsize=16)
cbar.ax.tick_params(labelsize=14)  # Increase font size for color bar ticks
plt.title("Heatmap of Retransmissions Between Stations", fontsize=16)
plt.xticks(ticks=np.arange(len(stations)), labels=stations, rotation=45)
plt.yticks(ticks=np.arange(len(stations)), labels=stations)
plt.xlabel("Receiving Stations", fontsize=16)
plt.ylabel("Transmitting Stations", fontsize=16)
plt.xticks(fontsize=14)  # Increase font size for x-axis tick labels
plt.yticks(fontsize=14)  # Increase font size for y-axis tick labels
plt.savefig("retransmissions_heatmap.pdf", format="pdf", bbox_inches="tight")
plt.close()
