import pyshark


# Function to analyze the first 20 packets and capture AP MAC addresses
def identify_ap_mac_addresses(pcap_file,  num_packets=20):
    capture = pyshark.FileCapture(pcap_file)
    ap_mac_addresses = set()

    packet_count = 0
    for packet in capture:
        try:
            if 'wlan' in packet:
                src_mac = packet.wlan.sa  # Source MAC address
                frame_type = int(packet.wlan.fc_type)  # Frame type
                frame_subtype = int(packet.wlan.fc_type_subtype)  # Frame subtype

                # Capture AP MAC from beacon frames (type=0, subtype=8) and common management frames
                if frame_type == 0 and frame_subtype == 8:  # Beacon frame
                    ap_mac_addresses.add(src_mac)

                packet_count += 1
                if packet_count >= num_packets:
                    break  # Stop after processing the first 20 packets

        except AttributeError:
            pass  # Skip packets without required attributes

    capture.close()
    return ap_mac_addresses


# Function to extract MAC transitions and track sequence number resets
def extract_station_mac_transitions(pcap_file, ap_mac_addresses, time_threshold):
    capture = pyshark.FileCapture(pcap_file)
    #ap_mac_addresses = set()  # To store AP MAC addresses from beacon frames
    station_mac_transitions = []

    for packet in capture:
        try:
            if 'wlan' in packet:
                src_mac = packet.wlan.sa  # Source MAC address
                seq_num = int(packet.wlan.seq)  # Sequence number
                frame_type = int(packet.wlan.fc_type)  # Frame type
                frame_subtype = int(packet.wlan.fc_type_subtype)  # Frame subtype
                timestamp = float(packet.sniff_timestamp)

                # Identify AP MAC from beacon frames (type=0, subtype=8)
                if frame_type == 0 and frame_subtype == 8:  # Beacon frame
                    ap_mac_addresses.add(src_mac)
                
                # Ignore AP MAC addresses and filter duplicates
                if src_mac not in ap_mac_addresses:
                    # Capture non-AP MAC addresses with sequence number 0
                    if seq_num == 0:
                        if not any(mac[0] == src_mac for mac in station_mac_transitions):
                            station_mac_transitions.append((src_mac, seq_num, timestamp))

        except AttributeError:
            pass  # Skip packets without required attributes

    return station_mac_transitions

# Function to group MAC addresses by time periods based on time gaps
def group_by_time_period(station_mac_transitions, time_threshold):
    time_periods = []
    current_period = []
    previous_timestamp = None

    for mac, seq, timestamp in station_mac_transitions:
        # Start new period if time gap exceeds threshold
        if previous_timestamp is None or (timestamp - previous_timestamp) > time_threshold:
            if current_period:
                time_periods.append(current_period)
            current_period = []  # Start new period
        
        current_period.append((mac, seq, timestamp))
        previous_timestamp = timestamp

    if current_period:
        time_periods.append(current_period)

    return time_periods

# Function to link MAC addresses across adjacent time periods
def link_mac_addresses_across_periods(time_periods):
    linked_chains = {}  # Dictionary to store linked chains for each MAC

    # Iterate over consecutive time periods
    for i in range(1, len(time_periods)):
        prev_period = time_periods[i-1]
        curr_period = time_periods[i]

        print(f"\nLinking between Time Period {i} and Time Period {i+1}:")

        # Track which MACs from the current period have already been linked
        used_curr_macs = set()

        # Link each MAC in previous period with the closest MAC in the current period
        for prev_mac, prev_seq, prev_time in prev_period:
            best_match = None
            smallest_time_diff = float('inf')

            for curr_mac, curr_seq, curr_time in curr_period:
                if curr_mac in used_curr_macs:
                    continue  # Skip already linked MACs

                time_diff = abs(curr_time - prev_time)
                if time_diff < smallest_time_diff:
                    smallest_time_diff = time_diff
                    best_match = (prev_mac, curr_mac)

            if best_match:
                prev_mac, curr_mac = best_match
                print(f"Linked {prev_mac} -> {curr_mac} with time diff: {smallest_time_diff:.6f} seconds")
                
                # Add this to linked chain
                if prev_mac in linked_chains:
                    linked_chains[prev_mac].append(curr_mac)
                else:
                    linked_chains[prev_mac] = [curr_mac]

                used_curr_macs.add(curr_mac)  # Mark this MAC as used

    return linked_chains

# Function to print linked MAC address chains
def print_mac_chains(linked_chains):
    print("\nMAC address chains:")
    printed_macs = set()  # To track MACs that have already been printed

    for start_mac, chain in linked_chains.items():
        if start_mac in printed_macs:
            continue  # Skip MACs that have already been printed in a chain

        chain_str = f"{start_mac}"
        current_mac = start_mac
        while current_mac in linked_chains and linked_chains[current_mac]:
            next_mac = linked_chains[current_mac].pop(0)
            chain_str += f" -> {next_mac}"
            printed_macs.add(current_mac)
            current_mac = next_mac

        print(chain_str)
        printed_macs.add(current_mac)  # Mark the last MAC in the chain as printed

# Main function to run the analysis
def main(pcap_file, time_threshold=7):

    # Step 1: Identify AP MAC addresses from the first 20 packets
    ap_mac_addresses = identify_ap_mac_addresses(pcap_file)
    print(f"Identified AP MAC addresses: {ap_mac_addresses}")
    # Extract station MAC transitions (ignoring AP MACs)
    station_mac_transitions = extract_station_mac_transitions(pcap_file, ap_mac_addresses, time_threshold)

    # Group MACs by time period based on time gaps
    time_periods = group_by_time_period(station_mac_transitions, time_threshold)

    # below loop for the time periods and the mac address in each time period
    # Print MAC addresses grouped by time periods
    
    print("\nMAC addresses grouped by time periods:")
    for i, period in enumerate(time_periods, start=1):
        print(f"\nTime Period {i}:")
        for mac, seq, time in period:
            print(f"Station MAC: {mac}, Seq: {seq}, Time: {time}")
    
    # Link MAC addresses across consecutive time periods based on the closest time
    linked_chains = link_mac_addresses_across_periods(time_periods)

    # Print MAC address chains
    #print_mac_chains(linked_chains)

if __name__ == "__main__":
    # Provide the path to the .pcap file
    pcap_file = '/media/sf_rathan-dataset/pcap_files/linking/test_1.pcap'  # Update with your pcap file path
    main(pcap_file)
