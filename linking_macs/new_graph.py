import re
from collections import defaultdict
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.colors as mcolors

# Sample data as a multi-line string
data = """
[ 9846.846642] Ap: random MAC: be:b9:6f:68:7a:ce base mac: 02:00:00:00:00:00
[ 9846.846646] Ap: random MAC: 4a:d3:ce:ba:ac:4e base mac: 02:00:00:00:01:00
[ 9846.846648] Ap: random MAC: 86:02:1b:6c:28:50 base mac: 02:00:00:00:02:00
[ 9861.846323] Ap: random MAC: 56:ea:f4:60:bd:94 base mac: 02:00:00:00:00:00
[ 9861.846325] Ap: random MAC: de:64:c1:35:5e:96 base mac: 02:00:00:00:01:00
[ 9861.846326] Ap: random MAC: 22:5c:76:c0:1e:f8 base mac: 02:00:00:00:02:00
[ 9876.853205] Ap: random MAC: 72:10:01:86:c5:2c base mac: 02:00:00:00:00:00
[ 9876.853208] Ap: random MAC: 4e:8c:be:cf:a2:62 base mac: 02:00:00:00:01:00
[ 9876.853209] Ap: random MAC: 8a:d1:ef:ae:48:0e base mac: 02:00:00:00:02:00
[ 9891.883882] Ap: random MAC: ea:f0:6c:67:fc:5d base mac: 02:00:00:00:00:00
[ 9891.883890] Ap: random MAC: c2:52:09:f0:e7:62 base mac: 02:00:00:00:01:00
[ 9891.883891] Ap: random MAC: 36:59:14:c3:e4:b3 base mac: 02:00:00:00:02:00
[ 9906.857282] Ap: random MAC: 72:7a:b7:04:61:24 base mac: 02:00:00:00:00:00
[ 9906.857284] Ap: random MAC: 02:d9:1f:18:b0:c4 base mac: 02:00:00:00:01:00
[ 9906.857287] Ap: random MAC: 12:32:c9:da:9a:3c base mac: 02:00:00:00:02:00
[ 9921.846419] Ap: random MAC: 92:08:e8:42:13:d2 base mac: 02:00:00:00:00:00
[ 9921.846422] Ap: random MAC: 2e:51:49:a8:fd:0f base mac: 02:00:00:00:01:00
[ 9921.846424] Ap: random MAC: 4e:04:6c:27:e4:e9 base mac: 02:00:00:00:02:00
[ 9936.846309] Ap: random MAC: 9e:af:4c:5a:0b:9f base mac: 02:00:00:00:00:00
[ 9936.846311] Ap: random MAC: b2:d9:10:d6:6c:8c base mac: 02:00:00:00:01:00
[ 9936.846313] Ap: random MAC: fa:9e:08:5b:a8:40 base mac: 02:00:00:00:02:00
[ 9951.847251] Ap: random MAC: d6:8b:86:23:3c:19 base mac: 02:00:00:00:00:00
[ 9951.847254] Ap: random MAC: 5e:c7:d4:7d:29:6f base mac: 02:00:00:00:01:00
[ 9951.847256] Ap: random MAC: 4a:52:67:4c:f6:8a base mac: 02:00:00:00:02:00
[ 9966.883691] Ap: random MAC: da:22:56:05:33:ab base mac: 02:00:00:00:00:00
[ 9966.883694] Ap: random MAC: 26:71:68:b6:0a:18 base mac: 02:00:00:00:01:00
[ 9966.883695] Ap: random MAC: 7e:1a:a5:25:48:89 base mac: 02:00:00:00:02:00
"""

# Dictionary to store sets of MAC address transitions for each base MAC
mac_sets = defaultdict(set)

# Regex pattern to extract random and base MAC addresses
pattern = re.compile(r"random MAC: ([\da-f:]+) base mac: ([\da-f:]+)")

# Parse the data and populate mac_sets
#for line in data.strip().splitlines():
#    match = pattern.search(line)
#    if match:
#         random_mac, base_mac = match.groups()
#        mac_sets[base_mac].add(random_mac)
#
# Parse the data and populate mac_sets while maintaining order
for line in data.strip().splitlines():
    match = pattern.search(line)
    if match:
        random_mac, base_mac = match.groups()
        if base_mac not in mac_sets:
            mac_sets[base_mac] = []  # Initialize as a list to preserve order
        mac_sets[base_mac].append(random_mac)


# Print the sets
for base_mac, random_macs in mac_sets.items():
    print(f"Base MAC: {base_mac}")
    print("Random MACs:")
    for random_mac in random_macs:
        print(f"  - {random_mac}")
    print()


# Example linking log
linking_log = """
Linked Old MAC: 02:00:00:00:01:00 -> New MAC: 4a:d3:ce:ba:ac:4e with time diff: 0.003876 seconds
Linked Old MAC: 02:00:00:00:02:00 -> New MAC: 86:02:1b:6c:28:50 with time diff: 0.005459 seconds
Linked Old MAC: 02:00:00:00:00:00 -> New MAC: be:b9:6f:68:7a:ce with time diff: 0.005658 seconds
Linked Old MAC: 4a:d3:ce:ba:ac:4e -> New MAC: de:64:c1:35:5e:96 with time diff: 0.006600 seconds
Linked Old MAC: 86:02:1b:6c:28:50 -> New MAC: 22:5c:76:c0:1e:f8 with time diff: 0.002322 seconds
Linked Old MAC: be:b9:6f:68:7a:ce -> New MAC: 56:ea:f4:60:bd:94 with time diff: 0.004542 seconds
Linked Old MAC: de:64:c1:35:5e:96 -> New MAC: 8a:d1:ef:ae:48:0e with time diff: 0.013759 seconds
Linked Old MAC: 22:5c:76:c0:1e:f8 -> New MAC: 72:10:01:86:c5:2c with time diff: 0.014658 seconds
Linked Old MAC: 56:ea:f4:60:bd:94 -> New MAC: 4e:8c:be:cf:a2:62 with time diff: 0.014798 seconds
Linked Old MAC: 8a:d1:ef:ae:48:0e -> New MAC: c2:52:09:f0:e7:62 with time diff: 0.000176 seconds
Linked Old MAC: 72:10:01:86:c5:2c -> New MAC: 36:59:14:c3:e4:b3 with time diff: 0.039985 seconds
Linked Old MAC: 4e:8c:be:cf:a2:62 -> New MAC: ea:f0:6c:67:fc:5d with time diff: 0.046301 seconds
Linked Old MAC: c2:52:09:f0:e7:62 -> New MAC: 02:d9:1f:18:b0:c4 with time diff: 0.035737 seconds
Linked Old MAC: 36:59:14:c3:e4:b3 -> New MAC: 12:32:c9:da:9a:3c with time diff: 0.017077 seconds
Linked Old MAC: ea:f0:6c:67:fc:5d -> New MAC: 72:7a:b7:04:61:24 with time diff: 0.017091 seconds
Linked Old MAC: 02:d9:1f:18:b0:c4 -> New MAC: 2e:51:49:a8:fd:0f with time diff: 0.015178 seconds
Linked Old MAC: 12:32:c9:da:9a:3c -> New MAC: 4e:04:6c:27:e4:e9 with time diff: 0.002825 seconds
Linked Old MAC: 72:7a:b7:04:61:24 -> New MAC: 92:08:e8:42:13:d2 with time diff: 0.010342 seconds
Linked Old MAC: 2e:51:49:a8:fd:0f -> New MAC: b2:d9:10:d6:6c:8c with time diff: 0.024130 seconds
Linked Old MAC: 4e:04:6c:27:e4:e9 -> New MAC: fa:9e:08:5b:a8:40 with time diff: 0.025062 seconds
Linked Old MAC: 92:08:e8:42:13:d2 -> New MAC: 9e:af:4c:5a:0b:9f with time diff: 0.015429 seconds
Linked Old MAC: b2:d9:10:d6:6c:8c -> New MAC: 5e:c7:d4:7d:29:6f with time diff: 0.024220 seconds
Linked Old MAC: fa:9e:08:5b:a8:40 -> New MAC: 4a:52:67:4c:f6:8a with time diff: 0.020144 seconds
Linked Old MAC: 9e:af:4c:5a:0b:9f -> New MAC: d6:8b:86:23:3c:19 with time diff: 0.020820 seconds
Linked Old MAC: 5e:c7:d4:7d:29:6f -> New MAC: 26:71:68:b6:0a:18 with time diff: 0.042865 seconds
Linked Old MAC: 4a:52:67:4c:f6:8a -> New MAC: 7e:1a:a5:25:48:89 with time diff: 0.042806 seconds
Linked Old MAC: d6:8b:86:23:3c:19 -> New MAC: da:22:56:05:33:ab with time diff: 0.456441 seconds

"""



# Create a graph without edges
G = nx.Graph()

# Add nodes to the graph
for base_mac, random_macs in mac_sets.items():
    # Add the base MAC node
    G.add_node(base_mac)
    
    # Add the random MACs as nodes
    for random_mac in random_macs:
        G.add_node(random_mac)
        # For visualization purpose, position the random MAC nodes adjacent to the base MAC
        #G.add_edge(base_mac, random_mac)  # Adding an edge to keep nodes grouped, but it won't be shown


# Parse the linking log and add edges
pattern = re.compile(r"Linked Old MAC: ([0-9a-f:]+) -> New MAC: ([0-9a-f:]+)")
matches = pattern.findall(linking_log)
# Separate edges by color
green_edges = []
red_edges = []
for old_mac, new_mac in matches:
    G.add_edge(old_mac, new_mac)
    # Check if both old_mac and new_mac belong to the same base_mac in mac_sets
    same_set = False
    for base_mac, random_macs in mac_sets.items():
        if old_mac == base_mac or old_mac in random_macs:
            if new_mac == base_mac or new_mac in random_macs:
                same_set = True
                break
    if same_set:
        green_edges.append((old_mac, new_mac))
    else:
        red_edges.append((old_mac, new_mac))


#print no of green and red edges
print(f"Green edges: {len(green_edges)}")
print(f"Red edges: {len(red_edges)}")

# Assign colors to each base_mac and its random_macs
colors = list(mcolors.TABLEAU_COLORS.keys())
node_colors = {}
for i, (base_mac, random_macs) in enumerate(mac_sets.items()):
    color = colors[i % len(colors)]
    node_colors[base_mac] = color
    for random_mac in random_macs:
        node_colors[random_mac] = color


# Position nodes in rows for each base MAC and its random MACs
pos = {}
y = 0  # Initial y-position
x_spacing = 2  # Horizontal spacing between nodes
for base_mac, random_macs in mac_sets.items():
    # Position base MAC node
    pos[base_mac] = (0, y)
    # Position each random MAC node in a row to the right of the base MAC
    for i, random_mac in enumerate(random_macs, 1):
        pos[random_mac] = (i * x_spacing, y)
    y -= 1  # Move down for the next row

# Plot the graph without edges
plt.figure(figsize=(15, 10))
nx.draw_networkx_nodes(G, pos, node_size=1000, node_color=[node_colors[node] for node in G.nodes()], alpha=0.5)
#nx.draw_networkx_labels(G, pos, font_size=6)
#nx.draw_networkx_edges(G, pos, edge_color="red", arrows=True)
nx.draw_networkx_edges(G, pos, edgelist=green_edges, edge_color='green', arrows=True, width=5)
nx.draw_networkx_edges(G, pos, edgelist=red_edges, edge_color='red', arrows=True)

i=1
# Add station names to the left of the first node
for base_mac, random_macs in mac_sets.items():
    plt.text(pos[base_mac][0] - 0.5, pos[base_mac][1], f'STA{i}', horizontalalignment='right', verticalalignment='center', fontsize=10, color='black')
    i += 1


# Add re-randomization event numbers below each column
# Add re-randomization event numbers below each column for the last mac_sets
last_base_mac, last_random_macs = list(mac_sets.items())[-1]
for i, random_mac in enumerate([last_base_mac] + last_random_macs, 1):
    plt.text(pos[random_mac][0], pos[random_mac][1] - 0.4, f'Cycle {i}', horizontalalignment='center', verticalalignment='top', fontsize=10, color='black')

# Print the number of green and red edges on the graph
plt.text(0.95, 0.95, f"Correct links: {len(green_edges)}", horizontalalignment='left', verticalalignment='top', transform=plt.gca().transAxes, fontsize=12, color='green')
plt.text(0.95, 0.90, f"Incorrect links: {len(red_edges)}", horizontalalignment='left', verticalalignment='top', transform=plt.gca().transAxes, fontsize=12, color='red')
plt.text(0.95, 0.85, f"Accuracy: {((len(green_edges) / (len(green_edges) + len(red_edges))) * 100):.3f}%", horizontalalignment='left', verticalalignment='top', transform=plt.gca().transAxes, fontsize=12, color='green')
plt.title("MAC Address Re-randomization and Linking Accuracy Across Stations", fontsize=16)
plt.xlabel("Re-randomization Events")
plt.ylabel("Stations")
plt.axis("off")
plt.savefig("mac_transitions_graph.pdf", bbox_inches="tight", format="pdf")