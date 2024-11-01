import pyshark
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

# Function to parse packet capture time
def parse_capture_time(packet) -> float:
    return float(packet.sniff_time.timestamp())

# Function to link MAC addresses by looking at resets and maximum SN values
def link_mac_addresses(mac_packets: Dict[str, List[Tuple[int, float]]], ap_mac: str, threshold=20):
    linked_pairs = []
    # For each station MAC, check for transitions (SN=0) and link to previous period MAC
    for mac, packets in mac_packets.items():
        if mac == ap_mac:
            continue  # Skip AP's MAC
        for idx, (seq_num, capture_time) in enumerate(packets):
            if seq_num == 0:
                # Find MAC with maximum SN just before the current MAC's SN=0 packet
                min_time_diff = float('inf')
                best_pair = None
                for old_mac, old_packets in mac_packets.items():
                    if old_mac == mac or old_mac == ap_mac:
                        continue
                    last_sn, last_time = old_packets[-1]
                    time_diff = capture_time - last_time
                    if 0 < time_diff < min_time_diff and last_sn >= threshold:
                        min_time_diff = time_diff
                        best_pair = (old_mac, mac)
                if best_pair:
                    linked_pairs.append(best_pair)
                    print(f"Linked MAC {best_pair[0]} -> {best_pair[1]} with time diff: {min_time_diff:.4f} seconds")
    return linked_pairs

# Capture packets for a specified duration and store only SN=0 and max SN for each MAC
def capture_and_analyze(interface='wlan0', capture_duration=120, ap_mac=None):
    capture = pyshark.LiveCapture(interface=interface)
    mac_packets = defaultdict(list)  # Track MAC addresses and key packets (SN=0 and max SN)

    print(f"Capturing packets for {capture_duration // 60} minutes to monitor MAC transitions...")

    end_time = datetime.now() + timedelta(seconds=capture_duration)
    for packet in capture.sniff_continuously():
        try:
            if datetime.now() >= end_time:
                break
            src_mac = packet.wlan.sa
            seq_num = int(packet.wlan.seq)
            capture_time = parse_capture_time(packet)
            
            # Record packets with SN=0 or max SN
            if src_mac == ap_mac or seq_num == 0 or (mac_packets[src_mac] and seq_num > mac_packets[src_mac][-1][0]):
                mac_packets[src_mac].append((seq_num, capture_time))
                print(f"Captured packet from MAC: {src_mac}, Seq: {seq_num}, Time: {datetime.fromtimestamp(capture_time)}")

        except AttributeError:
            # Skip packet if attributes are missing
            continue

    # After capture, analyze the stored packets to link MAC addresses
    print("Analyzing captured data for MAC address linking...")
    linked_macs = link_mac_addresses(mac_packets, ap_mac)
    if linked_macs:
        print("MAC address linking completed. Linked pairs:")
        for old_mac, new_mac in linked_macs:
            print(f"{old_mac} -> {new_mac}")
    else:
        print("No linked MAC addresses found within the capture period.")

# Run the capture and analysis with specified AP MAC address
if __name__ == "__main__":
    # Define your AP MAC address here for distinguishing AP and station packets
    ap_mac_address = '02:00:00:00:00:00'
    capture_and_analyze(interface='hwsim0', capture_duration=120, ap_mac=ap_mac_address)
