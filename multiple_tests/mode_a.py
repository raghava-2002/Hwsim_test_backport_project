#!/usr/bin/env python

"Setting the position of Nodes with wmediumd to calculate the interference"

import sys
import os
from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import time as time

def topology(args):
    "Create a network." 
    #, noise_th=-91, fading_cof=3
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)
    #net = Mininet_wifi()

    info("*** Creating nodes\n")
    # mode a = 5GHz, channel 36 (Internal signal range is 35mts)
    # mode b = 2.4GHz channel 1
    # modes are a, b, g, n
    # rts_threshold=2347 means that the RTS/CTS mechanism will be used for frames larger than 2347 bytes
    ap1 = net.addAccessPoint('ap1', ssid='new-ssid', mode='a', channel='36', ip='192.168.42.1/24',
                             position='60,60,0',passwd='123456789a', encrypt='wpa3', rsn_pairwise='CCMP', ieee80211w='2', failMode="standalone", datapath='kernel', rts_threshold=500, txpower=13)
    # Stations configuration with increasing distance and height from the AP
    sta1 = net.addStation('sta1', ip='192.168.42.2/24', position='62,60,0.5', passwd='123456789a', encrypt='wpa3', range=35)  # 2 meters east, 0.5 meters up
    sta2 = net.addStation('sta2', ip='192.168.42.3/24', position='60,64,1', passwd='123456789a', encrypt='wpa3', range=35)  # 4 meters north, 1 meter up
    sta3 = net.addStation('sta3', ip='192.168.42.4/24', position='66.3,66.3,1.5', passwd='123456789a', encrypt='wpa3', range=35)  # 7 meters northeast, 1.5 meters up
    sta4 = net.addStation('sta4', ip='192.168.42.5/24', position='70,60,2', passwd='123456789a', encrypt='wpa3', range=35)  # 10 meters east, 2 meters up
    sta5 = net.addStation('sta5', ip='192.168.42.6/24', position='60,73,2.5', passwd='123456789a', encrypt='wpa3', range=35)  # 13 meters north, 2.5 meters up
    sta6 = net.addStation('sta6', ip='192.168.42.7/24', position='78,60,3', passwd='123456789a', encrypt='wpa3', range=35)  # 18 meters east, 3 meters up
    sta7 = net.addStation('sta7', ip='192.168.42.8/24', position='60,81,3.5', passwd='123456789a', encrypt='wpa3', range=35)  # 21 meters north, 3.5 meters up
    sta8 = net.addStation('sta8', ip='192.168.42.9/24', position='85,60,4', passwd='123456789a', encrypt='wpa3', range=35)  # 25 meters east, 4 meters up
    sta9 = net.addStation('sta9', ip='192.168.42.10/24', position='60,88,4.5', passwd='123456789a', encrypt='wpa3', range=35)  # 28 meters north, 4.5 meters up
    sta10 = net.addStation('sta10', ip='192.168.42.11/24', position='91,60,5', passwd='123456789a', encrypt='wpa3', range=35)  # 31 meters east, 5 meters up
    # Adjusted position for sta10 at 35 meters to target an RSSI of -89 dBm
    sta11 = net.addStation('sta11', ip='192.168.42.12/24', position='95,60,5.5', passwd='123456789a', encrypt='wpa3', range=35)  # 35 meters east, 5.5 meters up

    #net.addStation('sta2', mac='00:00:00:00:00:03', ip='10.0.0.2/8',
    #               position='20,50,0', passwd='123456789a', encrypt='wpa2')
    #net.addStation('sta3', mac='00:00:00:00:00:04', ip='10.0.0.3/8',
    #               position='20,60,10', passwd='123456789a', encrypt='wpa2')

    info("*** Configuring Propagation Model\n")
    #net.setPropagationModel(model="logDistance", exp=4.1)
    #LF: floor penetration loss factor
    # nFLOORS: number of floors
    net.setPropagationModel(model="ITU", nFLOORS=1, LF=20) 

    info("*** Configuring nodes\n")
    net.configureNodes()
    info("*** Associating Stations\n")
    ap1.setIP('192.168.42.1/24', intf='ap1-wlan1')
        # Add the following commands after creating the AP and configuring the IPs
    ap1.cmd('brctl addbr br0')  # Create the bridge
    ap1.cmd('brctl addif br0 ap1-wlan1')  # Add the wireless interface to the bridge
    ap1.cmd('ifconfig br0 192.168.42.1 netmask 255.255.255.0 up')  # Assign IP to the bridge
    ap1.cmd('ifconfig ap1-wlan1 0.0.0.0')  # Clear the IP from the wireless interface
    ap1.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')  # Enable IP forwarding

    net.addLink(sta1, ap1)
    net.addLink(sta2, ap1)
    net.addLink(sta3, ap1)
    net.addLink(sta4, ap1)
    net.addLink(sta5, ap1)
    net.addLink(sta6, ap1)
    net.addLink(sta7, ap1)
    net.addLink(sta8, ap1)
    net.addLink(sta9, ap1)
    net.addLink(sta10, ap1)
    net.addLink(sta11, ap1)

  

    if '-p' not in args:
        net.plotGraph(max_x=120, max_y=120)
        

    # Get the current working directory
    output_path = os.path.join(os.getcwd(), 'wifi_topology.png')
    info("*** Starting network\n")
    net.build()
    ap1.start([])
    info("*** Plotting network graph\n")
    # Save the plot as a PNG file
    plt.savefig(output_path, bbox_inches='tight')  # Save the figure to a file

    rssi_values = get_rssi_values(net, [sta1, sta2, sta3, sta4, sta5, sta6, sta7, sta8, sta9, sta10, sta11])

    dump_node_info(net)

    ap1.cmd('ifconfig ap1-wlan1 -promisc')

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


def dump_node_info(net):
    "Dump station information (IP and PID) to a file"
    output_file = os.path.join(os.getcwd(), "nodes.txt")

    with open(output_file, "w") as f:
        # Iterate over all nodes (stations and AP)
        for node in net.stations:
            info = f"<Station {node.name}: {node.name}-wlan0:{node.IP()} pid={node.pid}>"
            f.write(info + "\n")
        ap = net.get('ap1')
        ap_info = f"<AP {ap.name}: {ap.name}-wlan1:{ap.IP()} pid={ap.pid}>"
        f.write(ap_info + "\n")

    print(f"Node info written to {output_file}")

def get_rssi_values(net, stations):
    rssi_values = []
    for sta in stations:
        rssi = sta.wintfs[0].rssi
        rssi_values.append(rssi)
        print(f"RSSI for {sta.name}: {rssi}")
    return rssi_values

#heat map

if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
