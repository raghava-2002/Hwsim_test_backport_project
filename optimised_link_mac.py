import pyshark


# Function to analyze the first 20 packets and capture AP MAC addresses
def identify_ap_mac_addresses(pcap_file, num_packets=20):
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


# Function to identify packets where SN = 0 or get the first packet
def extract_mac_sn_zero_or_first(pcap_file, ap_mac_addresses):
    capture = pyshark.FileCapture(pcap_file, display_filter="wlan.seq == 0")
    station_mac_transitions = {}

    for packet in capture:
        try:
            if 'wlan' in packet:
                src_mac = packet.wlan.sa  # Source MAC address
                seq_num = int(packet.wlan.seq)  # Sequence number
                timestamp = float(packet.sniff_timestamp)

                # Ignore AP MAC addresses
                if src_mac not in ap_mac_addresses:
                    # Store the first packet (SN=0 or least SN)
                    if src_mac not in station_mac_transitions:
                        station_mac_transitions[src_mac] = {'first': (seq_num, timestamp)}

        except AttributeError:
            pass  # Skip packets without required attributes

    capture.close()
    return station_mac_transitions

# Function to find the last packet for each MAC
def find_last_packet_for_mac(pcap_file, station_mac_transitions):
    capture = pyshark.FileCapture(pcap_file)

    for packet in capture:
        try:
            if 'wlan' in packet:
                src_mac = packet.wlan.sa  # Source MAC address
                seq_num = int(packet.wlan.seq)  # Sequence number
                timestamp = float(packet.sniff_timestamp)

                # Track the highest sequence number (last packet) for each MAC
                if src_mac in station_mac_transitions:
                    if 'last' not in station_mac_transitions[src_mac] or seq_num > station_mac_transitions[src_mac]['last'][0]:
                        station_mac_transitions[src_mac]['last'] = (seq_num, timestamp)

        except AttributeError:
            pass  # Skip packets without required attributes

    capture.close()

# Function to print the first and last packet timestamps for each MAC
def print_first_last_packets(station_mac_transitions):
    print("\nFirst and last packet details for each MAC address:")
    for mac, packet_info in station_mac_transitions.items():
        first_seq, first_time = packet_info['first']
        last_seq, last_time = packet_info.get('last', ('N/A', 'N/A'))  # 'N/A' if last packet not found
        print(f"MAC: {mac} | First packet: Seq {first_seq}, Time {first_time} | Last packet: Seq {last_seq}, Time {last_time}")

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

                # Only link if time difference is less than the threshold (1 second)
                if time_diff < max_time_diff and time_diff < smallest_time_diff:
                    smallest_time_diff = time_diff
                    best_match = new_mac

        if best_match:
            linked_macs.append((old_mac, best_match, smallest_time_diff))
            print(f"Linked Old MAC: {old_mac} -> New MAC: {best_match} with time diff: {smallest_time_diff:.6f} seconds")

    return linked_macs

# Main function to run the analysis
def main(pcap_file, max_time_diff=1.0):

    # Step 1: Identify AP MAC addresses from the first 20 packets
    ap_mac_addresses = identify_ap_mac_addresses(pcap_file)
    print(f"Identified AP MAC addresses: {ap_mac_addresses}")

    # Step 2: Extract station MAC transitions (with SN=0 or least SN)
    station_mac_transitions = extract_mac_sn_zero_or_first(pcap_file, ap_mac_addresses)

    # Step 3: Find the last packet for each MAC address
    find_last_packet_for_mac(pcap_file, station_mac_transitions)

    # Step 4: Print the first and last packet for each MAC address
    print_first_last_packets(station_mac_transitions)

    # Step 5: Link MAC addresses based on closest timestamps with a time difference less than 1 second
    linked_macs = link_mac_addresses(station_mac_transitions, max_time_diff=max_time_diff)

if __name__ == "__main__":
    # Provide the path to the .pcap file
    pcap_file = '/home/rathan/Downloads/pcap_files/time_drift_02.pcap'  # Update with your pcap file path
    main(pcap_file)
