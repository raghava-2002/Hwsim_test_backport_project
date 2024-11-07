import matplotlib.pyplot as plt

# Sample data
data = [
    {'base_mac': '02:00:00:00:00:00', 'random_mac': '66:84:3d:4f:b0:96', 'transition': 1, 'correct': False},
    {'base_mac': '02:00:00:00:02:00', 'random_mac': 'f6:84:3b:c8:47:1b', 'transition': 1, 'correct': True},
    {'base_mac': '02:00:00:00:01:00', 'random_mac': '36:79:67:62:22:ab', 'transition': 1, 'correct': True},
    # Add more data as needed
]

# Extract unique base MAC addresses for y-axis
base_macs = sorted(set(item['base_mac'] for item in data))
base_mac_indices = {mac: idx for idx, mac in enumerate(base_macs)}

# Plotting
plt.figure(figsize=(10, 6))

for item in data:
    y = base_mac_indices[item['base_mac']]
    x = item['transition']
    color = 'green' if item['correct'] else 'red'
    plt.plot([x, x + 1], [y, y], marker='o', color=color)

# Formatting
plt.yticks(range(len(base_macs)), base_macs)
plt.xlabel('Transition Number')
plt.ylabel('Base MAC Address')
plt.title('Linking of Re-randomized MAC Addresses')
plt.grid(True)
plt.savefig('linking_macs.pdf', bbox_inches='tight', format='pdf')
