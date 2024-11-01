import re

# Function to check linking accuracy based on prepared kernel log mappings
def check_linking_accuracy(linked_macs, kernel_mac_mapping):
    """
    Checks if each linked MAC pair has the same base MAC in the kernel log mapping.
    """
    correct_links = 0
    incorrect_links = []

    for old_mac, new_mac, _ in linked_macs:  # We ignore the time difference here
        found_match = False

        # Check if both old_mac and new_mac are within the same list in the kernel_mac_mapping dictionary
        for base_mac, random_macs in kernel_mac_mapping.items():
            if old_mac in random_macs and new_mac in random_macs:
                correct_links += 1
                found_match = True
                break

        # If no matching base MAC found for both linked MACs, mark as incorrect
        if not found_match:
            incorrect_links.append((old_mac, new_mac))

    # Print results
    print(f"Total Correct Links: {correct_links}")
    print(f"Total Incorrect Links: {len(incorrect_links)}\n")

    # Display incorrect links if any
    #if incorrect_links:
    #    print("Incorrect Links:")
    #    for old_mac, new_mac in incorrect_links:
    #        print(f"Linked Old MAC: {old_mac} -> New MAC: {new_mac}")

    return correct_links, incorrect_links



# Parse the kernel log to create the kernel_mac_mapping dictionary
kernel_log = """
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



# Initialize the dictionary
kernel_mac_mapping = {}

# Regular expression to match the log lines
log_pattern = re.compile(r'Ap: random MAC: ([0-9a-f:]+) base mac: ([0-9a-f:]+)')

# Process each line in the kernel log
for line in kernel_log.strip().split('\n'):
    match = log_pattern.search(line)
    if match:
        random_mac, base_mac = match.groups()
        if base_mac not in kernel_mac_mapping:
            kernel_mac_mapping[base_mac] = []
        kernel_mac_mapping[base_mac].append(random_mac)

# Example dictionary for kernel log (base MAC as key, list of random MACs as value)
#print(kernel_mac_mapping)

# Function to extract linked MAC pairs from the linking log
def extract_linked_macs(log):
    """
    Extracts linked MAC pairs from the given log.
    """
    linking_pattern = re.compile(r'Linked Old MAC: ([0-9a-f:]+) -> New MAC: ([0-9a-f:]+) with time diff: ([0-9.]+) seconds')
    linked_macs = []

    for line in log.strip().split('\n'):
        match = linking_pattern.search(line)
        if match:
            old_mac, new_mac, time_diff = match.groups()
            linked_macs.append((old_mac, new_mac, float(time_diff)))

    return linked_macs

# Example linking log
linking_log = """
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

# Extract linked MAC pairs from the linking log
linked_macs = extract_linked_macs(linking_log)

# Example list of linked MAC pairs (modify as needed)
#print(linked_macs)

# Run the check
correct_links, incorrect_links = check_linking_accuracy(linked_macs, kernel_mac_mapping)

