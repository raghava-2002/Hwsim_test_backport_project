import pyshark
from concurrent.futures import ProcessPoolExecutor

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

                # Capture AP MAC from beacon frames (type=0, subtype=8)
                if frame_type == 0 and frame_subtype == 8:
                    ap_mac_addresses.add(src_mac)

                packet_count += 1
                if packet_count >= num_packets:
                    break
        except AttributeError:
            pass

    capture.close()
    return ap_mac_addresses

# Function to extract MAC transitions and track sequence number resets
def extract_station_mac_transitions(pcap_file, ap_mac_addresses):
    capture = pyshark.FileCapture(pcap_file)  # Filter for management frames
    station_mac_transitions = {}

    for packet in capture:
        try:
            if 'wlan' in packet:
                src_mac = packet.wlan.sa
                seq_num = int(packet.wlan.seq)
                timestamp = float(packet.sniff_timestamp)

                # Ignore AP MAC addresses
                if src_mac not in ap_mac_addresses:
                    if src_mac not in station_mac_transitions:
                        station_mac_transitions[src_mac] = {'first': (seq_num, timestamp), 'last': (seq_num, timestamp)}
                    else:
                        # Update last packet with the highest sequence number
                        station_mac_transitions[src_mac]['last'] = (seq_num, timestamp)

        except AttributeError:
            pass

    capture.close()
    return station_mac_transitions

# Function to print the first and last packet timestamps for each MAC
def print_first_last_packets(station_mac_transitions):
    results = []
    for mac, packet_info in station_mac_transitions.items():
        first_seq, first_time = packet_info['first']
        last_seq, last_time = packet_info['last']
        results.append(f"MAC: {mac} | First packet: Seq {first_seq}, Time {first_time} | Last packet: Seq {last_seq}, Time {last_time}")
    return results

# Function to link MAC addresses based on time differences with granular sequence tracking
def link_mac_addresses(station_mac_transitions, max_time_diff=1.0):
    linked_macs = []
    used_sequences = {}

    mac_list = list(station_mac_transitions.keys())

    for i in range(len(mac_list)):
        old_mac = mac_list[i]
        old_last_seq, old_last_time = station_mac_transitions[old_mac]['last']
        
        if old_mac not in used_sequences:
            used_sequences[old_mac] = set()
        
        if old_last_seq in used_sequences[old_mac]:
            continue

        best_match = None
        smallest_time_diff = float('inf')

        for j in range(len(mac_list)):
            if i != j:
                new_mac = mac_list[j]
                new_first_seq, new_first_time = station_mac_transitions[new_mac]['first']
                
                if new_mac not in used_sequences:
                    used_sequences[new_mac] = set()
                
                if new_first_seq in used_sequences[new_mac]:
                    continue

                time_diff = abs(new_first_time - old_last_time)

                if time_diff < max_time_diff and time_diff < smallest_time_diff:
                    smallest_time_diff = time_diff
                    best_match = new_mac

        if best_match:
            linked_macs.append((old_mac, best_match, smallest_time_diff))
            used_sequences[old_mac].add(old_last_seq)
            used_sequences[best_match].add(station_mac_transitions[best_match]['first'][0])

    return linked_macs




def imp_link_mac_addresses(station_mac_transitions, max_time_diff=1.0):
    linked_macs = []
    used_sequences = {}
    potential_links = []

    mac_list = list(station_mac_transitions.keys())

    for i in range(len(mac_list)):
        old_mac = mac_list[i]
        old_last_seq, old_last_time = station_mac_transitions[old_mac]['last']
        
        if old_mac not in used_sequences:
            used_sequences[old_mac] = set()
        
        if old_last_seq in used_sequences[old_mac]:
            continue

        for j in range(len(mac_list)):
            if i != j:
                new_mac = mac_list[j]
                new_first_seq, new_first_time = station_mac_transitions[new_mac]['first']
                
                if new_mac not in used_sequences:
                    used_sequences[new_mac] = set()
                
                if new_first_seq in used_sequences[new_mac]:
                    continue

                time_diff = abs(new_first_time - old_last_time)

                if time_diff < max_time_diff:
                    potential_links.append((old_mac, new_mac, time_diff))

    # Sort potential links by time difference (smallest first)
    potential_links.sort(key=lambda x: x[2])

    # Process potential links in order of smallest time difference
    for old_mac, new_mac, time_diff in potential_links:
        if old_mac not in used_sequences or new_mac not in used_sequences or \
           (station_mac_transitions[old_mac]['last'][0] not in used_sequences[old_mac] and 
            station_mac_transitions[new_mac]['first'][0] not in used_sequences[new_mac]):
            
            linked_macs.append((old_mac, new_mac, time_diff))
            used_sequences[old_mac].add(station_mac_transitions[old_mac]['last'][0])
            used_sequences[new_mac].add(station_mac_transitions[new_mac]['first'][0])

    return linked_macs


# Function to process each pcap file
def process_pcap_file(pcap_file):
    print(f"\nProcessing file: {pcap_file}")
    
    # Step 1: Identify AP MAC addresses
    ap_mac_addresses = identify_ap_mac_addresses(pcap_file)
    print(f"Identified AP MAC addresses in {pcap_file}: {ap_mac_addresses}")

    # Step 2: Extract station MAC transitions
    station_mac_transitions = extract_station_mac_transitions(pcap_file, ap_mac_addresses)

    # Step 3: Print the first and last packet for each MAC address
    #first_last_packets = print_first_last_packets(station_mac_transitions)
    #print(f"\nFirst and last packet details for each MAC address:{pcap_file}")
    #for line in first_last_packets:
        #print(line)

    # Step 4: Link MAC addresses based on closest timestamps
    #linked_macs = link_mac_addresses(station_mac_transitions, max_time_diff=1.0)
    #print(f"\nLinked MACs based on time differences: Processing file: {pcap_file}")
    #for old_mac, new_mac, time_diff in linked_macs:
        #print(f"Linked Old MAC: {old_mac} -> New MAC: {new_mac} with time diff: {time_diff:.6f} seconds")


    # Step 5: Improved Linking MAC addresses based on closest timestamps
    linked_macs = imp_link_mac_addresses(station_mac_transitions, max_time_diff=1.0)
    print(f"\nImproved Linked MACs based on time differences: Processing file: {pcap_file}")
    for old_mac, new_mac, time_diff in linked_macs:
        print(f"Linked Old MAC: {old_mac} -> New MAC: {new_mac} with time diff: {time_diff:.6f} seconds")

# Main function to execute the analysis on multiple pcap files
def main():
    pcap_files = [
        '/media/sf_rathan-dataset/pcap_files/linking/kernel_time/anonimity_set_9_1.pcap',
        '/media/sf_rathan-dataset/pcap_files/linking/kernel_time/anonimity_set_9_2.pcap',
        '/media/sf_rathan-dataset/pcap_files/linking/kernel_time/anonimity_set_9_3.pcap',
        '/media/sf_rathan-dataset/pcap_files/linking/kernel_time/anonimity_set_9_4.pcap',
        '/media/sf_rathan-dataset/pcap_files/linking/kernel_time/anonimity_set_9_5.pcap'
    ]

    # Use ProcessPoolExecutor to process files in parallel
    with ProcessPoolExecutor(max_workers=10) as executor:
        executor.map(process_pcap_file, pcap_files)

if __name__ == "__main__":
    main()
