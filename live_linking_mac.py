import pyshark

# Function to identify AP MAC addresses from live interface
def identify_ap_mac_addresses_live(interface, num_packets=50):
    capture = pyshark.LiveCapture(interface=interface)  # Removed the filter
    capture.set_debug()  # Enable debug mode for more detailed logging if TShark crashes
    ap_mac_addresses = set()

    packet_count = 0
    for packet in capture.sniff_continuously(packet_count=num_packets):
        try:
            if 'wlan' in packet:
                src_mac = packet.wlan.sa  # Source MAC address
                frame_type = int(packet.wlan.fc_type)  # Frame type
                frame_subtype = int(packet.wlan.fc_type_subtype)  # Frame subtype

                # Capture AP MAC from beacon frames (type=0, subtype=8)
                if frame_type == 0 and frame_subtype == 8:  # Beacon frame
                    ap_mac_addresses.add(src_mac)

                packet_count += 1
                if packet_count >= num_packets:
                    break  # Stop after processing 50 packets or as needed

        except AttributeError:
            pass  # Skip packets without required attributes

    return ap_mac_addresses

# Function to track stations by observing highest and lowest sequence numbers
def track_station_sequence_numbers_live(interface, ap_mac_addresses):
    capture = pyshark.LiveCapture(interface=interface, output_file='live_capture.pcap')  # Save all packets to one file
    capture.set_debug()  # Enable debug mode for more detailed logging if TShark crashes
    station_mac_sequences = {}

    for packet in capture.sniff_continuously():
        try:
            if 'wlan' in packet:
                src_mac = packet.wlan.sa  # Source MAC address
                seq_num = int(packet.wlan.seq)  # Sequence number
                timestamp = float(packet.sniff_timestamp)  # Packet timestamp

                # Ignore AP MAC addresses
                if src_mac not in ap_mac_addresses:
                    # Track the highest and lowest sequence number for each MAC
                    if src_mac not in station_mac_sequences:
                        station_mac_sequences[src_mac] = {'first': (seq_num, timestamp), 'last': (seq_num, timestamp)}
                    else:
                        # Update highest and lowest sequence numbers
                        station_mac_sequences[src_mac]['last'] = (seq_num, timestamp)

        except AttributeError:
            pass  # Skip packets without required attributes

    return station_mac_sequences

# Function to link MAC addresses based on time differences
def link_mac_addresses(station_mac_transitions, max_time_diff=1.0):
    print("\nLinking MAC addresses based on time differences:")
    linked_macs = []

    mac_list = list(station_mac_transitions.keys())

    for i in range(len(mac_list)):
        old_mac = mac_list[i]
        old_last_time = station_mac_transitions[old_mac]['last'][1]
        best_match = None
        smallest_time_diff = float('inf')

        # Compare this MAC's last packet timestamp with other MACs' first packet timestamp
        for j in range(len(mac_list)):
            if i != j:  # Ensure we're not comparing the same MAC
                new_mac = mac_list[j]
                new_first_time = station_mac_transitions[new_mac]['first'][1]
                time_diff = abs(new_first_time - old_last_time)

                # Only link if time difference is less than the threshold (e.g., 1 second)
                if time_diff < max_time_diff and time_diff < smallest_time_diff:
                    smallest_time_diff = time_diff
                    best_match = new_mac

        if best_match:
            linked_macs.append((old_mac, best_match, smallest_time_diff))
            print(f"Linked Old MAC: {old_mac} -> New MAC: {best_match} with time diff: {smallest_time_diff:.6f} seconds")

    return linked_macs

# Main function to run live analysis
def main_live(interface, max_time_diff=1.0):
    # Step 1: Identify AP MAC addresses from the live interface
    ap_mac_addresses = identify_ap_mac_addresses_live(interface)
    print(f"Identified AP MAC addresses: {ap_mac_addresses}")

    # Step 2: Track station MACs by their highest and lowest sequence numbers
    station_mac_transitions = track_station_sequence_numbers_live(interface, ap_mac_addresses)

    # Step 3: Link MAC addresses based on time differences
    linked_macs = link_mac_addresses(station_mac_transitions, max_time_diff)

if __name__ == "__main__":
    # Provide the interface name to capture live packets (e.g., 'hwsim0')
    live_interface = 'hwsim0'  # Update with your network interface
    main_live(live_interface)
