from scapy.all import *

# Craft an ICMP echo request packet with destination IP address
packet = IP(dst="192.168.42.5") / ICMP()

# Send one packet per second for a total of 10 packets
for _ in range(10):
    send(packet, iface="wlan0", verbose=True)
    time.sleep(1)  # Wait for 1 second before sending the next packet
