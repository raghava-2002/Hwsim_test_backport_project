from scapy.all import *

# Create a custom management frame
pkt = RadioTap() / \
      Dot11(type=0, subtype=15, addr1="ff:ff:ff:ff:ff:ff", addr2="02:00:00:00:00:00", addr3="02:00:00:00:00:00") / \
      Dot11Beacon(cap="ESS+privacy") / \
      Dot11Elt(ID='SSID', info='testrun') / \
      Raw(load="Custom Payload Data")

# Send the packet
sendp(pkt, iface="wlan0", count=1)
