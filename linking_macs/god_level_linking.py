import pyshark
import heapq  # For priority queue

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

# Function to extract MAC transitions and track sequence number resets
def extract_station_mac_transitions(pcap_file, ap_mac_addresses):
    capture = pyshark.FileCapture(pcap_file)  # Filter for management frames
    station_mac_transitions = {}

    for packet in capture:
        try:
            if 'wlan' in packet:
                src_mac = packet.wlan.sa  # Source MAC address
                seq_num = int(packet.wlan.seq)  # Sequence number
                timestamp = float(packet.sniff_timestamp)

                # Ignore AP MAC addresses
                if src_mac not in ap_mac_addresses:
                    # Track the first and last packet for each MAC
                    if src_mac not in station_mac_transitions:
                        station_mac_transitions[src_mac] = {'first': (seq_num, timestamp), 'last': (seq_num, timestamp)}
                    else:
                        # Update last packet with the highest sequence number
                        station_mac_transitions[src_mac]['last'] = (seq_num, timestamp)

        except AttributeError:
            pass  # Skip packets without required attributes

    capture.close()
    return station_mac_transitions

# Function to print the first and last packet timestamps for each MAC
def print_first_last_packets(station_mac_transitions):
    print("\nFirst and last packet details for each MAC address:")
    for mac, packet_info in station_mac_transitions.items():
        first_seq, first_time = packet_info['first']
        last_seq, last_time = packet_info['last']
        print(f"MAC: {mac} | First packet: Seq {first_seq}, Time {first_time} | Last packet: Seq {last_seq}, Time {last_time}")





def link_mac_addresses(station_mac_transitions, max_time_diff=1.0):
    print("\nLinking MAC addresses based on time differences and sequence tracking:")
    linked_macs = []
    used_macs = set()
    mac_list = list(station_mac_transitions.keys())
    
    # Priority queue to store all possible links by time difference
    link_candidates = []

    # Populate link candidates with all possible (MAC, MAC) pairs and their time differences
    for i in range(len(mac_list)):
        for j in range(i + 1, len(mac_list)):
            old_mac = mac_list[i]
            new_mac = mac_list[j]
            
            old_last_seq, old_last_time = station_mac_transitions[old_mac]['last']
            new_first_seq, new_first_time = station_mac_transitions[new_mac]['first']
            
            # Calculate time difference
            time_diff = abs(new_first_time - old_last_time)
            
            # Only consider links within the time threshold
            if time_diff <= max_time_diff:
                heapq.heappush(link_candidates, (time_diff, old_mac, new_mac, old_last_seq, new_first_seq))

    # Process link candidates from smallest to largest time difference
    while link_candidates:
        time_diff, old_mac, new_mac, old_last_seq, new_first_seq = heapq.heappop(link_candidates)
        
        # Ensure neither MAC has already been linked
        if old_mac in used_macs or new_mac in used_macs:
            continue
        
        # Link MACs and mark as used
        linked_macs.append((old_mac, new_mac, time_diff))
        used_macs.add(old_mac)
        used_macs.add(new_mac)
        
        print(f"Linked Old MAC: {old_mac} -> New MAC: {new_mac} with time diff: {time_diff:.6f} seconds")

    return linked_macs





# Main function to run the analysis
def main(pcap_file, time_threshold=7):

    # Step 1: Identify AP MAC addresses from the first 20 packets
    ap_mac_addresses = identify_ap_mac_addresses(pcap_file)
    print(f"Identified AP MAC addresses: {ap_mac_addresses}")

    # Step 2: Extract station MAC transitions (ignoring AP MACs)
    station_mac_transitions = extract_station_mac_transitions(pcap_file, ap_mac_addresses)

    # Step 3: Print the first and last packet for each MAC address
    print_first_last_packets(station_mac_transitions)

    # Step 4: Link MAC addresses based on closest timestamps with a time difference less than 1 second
    linked_macs = link_mac_addresses(station_mac_transitions)
    print("Linked MAC addresses:", linked_macs)

if __name__ == "__main__":
    # Provide the path to the .pcap file
    pcap_file = '/media/sf_rathan-dataset/pcap_files/linking/kernel_time/anonimity_set_3_1.pcap'  # Update with your pcap file path
    main(pcap_file)
