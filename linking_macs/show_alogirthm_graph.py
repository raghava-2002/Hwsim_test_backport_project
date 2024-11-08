import matplotlib.pyplot as plt

# Data for MAC addresses with specific timestamps
mac_data = [
    {"mac": "66:84:3d:4f:b0:96", "last_time": 87992.472389},
    {"mac": "f6:84:3b:c8:47:1b", "last_time": 87992.469078},
    {"mac": "36:79:67:62:22:ab", "last_time": 87992.469141},
    {"mac": "12:50:a6:e0:b4:d4", "first_time": 87992.47288},
    {"mac": "aa:20:02:cc:6a:7b", "first_time": 87992.472971},
    {"mac": "da:4a:de:44:73:f9", "first_time": 87992.476824}
]

# Calculate the min and max timestamps for setting x-axis limits and ticks
min_time = min(mac["last_time"] if "last_time" in mac else mac["first_time"] for mac in mac_data)
max_time = max(mac["last_time"] if "last_time" in mac else mac["first_time"] for mac in mac_data)

# Plot the focused timeline
fig, ax = plt.subplots(figsize=(12, 6))

# Plot only the last packets of the first three MACs
for i in range(3):
    ax.plot(mac_data[i]["last_time"], i, marker='o', markersize=12, color="blue", label="Last Packet" if i == 0 else "")

# Plot only the first packets of the next three MACs
for i in range(3, 6):
    ax.plot(mac_data[i]["first_time"], i, marker='o', markersize=12, color="green", label="First Packet" if i == 3 else "")

# Draw arrows from the last packets of the first group to the first packets of the next group
for i in range(3):
    ax.annotate("",
                xy=(mac_data[i + 3]["first_time"], i + 3),
                xytext=(mac_data[i]["last_time"], i),
                arrowprops=dict(arrowstyle="->", color="purple", lw=2))

# Set labels and title
ax.set_yticks(range(len(mac_data)))
ax.set_yticklabels([mac["mac"] for mac in mac_data])
ax.set_xlabel("Timestamp")
ax.set_title("MAC Address Linking Transition Visualization")

# Set x-axis limits and ticks based on min and max times in the data
ax.set_xlim(min_time - 0.001, max_time + 0.001)
ax.set_xticks([min_time + i * 0.0005 for i in range(int((max_time - min_time) * 2000) + 1)])  # Granular ticks every 0.0005 seconds
ax.set_xticklabels([f"{tick:.6f}" for tick in ax.get_xticks()], rotation=45)

plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.tight_layout()
plt.show()


plt.savefig("algorithm_graph.png")
