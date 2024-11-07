#!/usr/bin/env python

"Setting the position of Nodes without wmediumd for interference calculations"

import sys
import os
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import time as time

def topology(args):
    "Create a network." 
    net = Mininet_wifi()  # Removed wmediumd and interference mode

    info("*** Creating nodes\n")

    ap1 = net.addAccessPoint('ap1', ssid='new-ssid', mode='a', channel='36', ip='192.168.42.1/24',
                             position='60,60,0',passwd='123456789a', encrypt='wpa2', rsn_pairwise='CCMP', ieee80211w='2', failMode="standalone", datapath='kernel', rts_threshold=500, txpower=13)
    # Stations configuration with increasing distance and height from the AP
    sta1 = net.addStation('sta1', ip='192.168.42.2/24', position='62,60,0.5', passwd='123456789a', encrypt='wpa2')  # 2 meters east, 0.5 meters up
    sta2 = net.addStation('sta2', ip='192.168.42.3/24', position='60,64,1', passwd='123456789a', encrypt='wpa2')  # 4 meters north, 1 meter up
    sta3 = net.addStation('sta3', ip='192.168.42.4/24', position='66.3,66.3,1.5', passwd='123456789a', encrypt='wpa2')  # 7 meters northeast, 1.5 meters up
    sta4 = net.addStation('sta4', ip='192.168.42.5/24', position='70,60,2', passwd='123456789a', encrypt='wpa2')  # 10 meters east, 2 meters up
    sta5 = net.addStation('sta5', ip='192.168.42.6/24', position='60,73,2.5', passwd='123456789a', encrypt='wpa2')  # 13 meters north, 2.5 meters up
    sta6 = net.addStation('sta6', ip='192.168.42.7/24', position='78,60,3', passwd='123456789a', encrypt='wpa2')  # 18 meters east, 3 meters up
    sta7 = net.addStation('sta7', ip='192.168.42.8/24', position='60,81,3.5', passwd='123456789a', encrypt='wpa2')  # 21 meters north, 3.5 meters up
    sta8 = net.addStation('sta8', ip='192.168.42.9/24', position='85,60,4', passwd='123456789a', encrypt='wpa2')  # 25 meters east, 4 meters up
    sta9 = net.addStation('sta9', ip='192.168.42.10/24', position='60,88,4.5', passwd='123456789a', encrypt='wpa2')  # 28 meters north, 4.5 meters up
    sta10 = net.addStation('sta10', ip='192.168.42.11/24', position='91,60,5', passwd='123456789a', encrypt='wpa2')  # 31 meters east, 5 meters up
    # Adjusted position for sta10 at 35 meters to target an RSSI of -89 dBm
    sta11 = net.addStation('sta11', ip='192.168.42.12/24', position='95,60,5.5', passwd='123456789a', encrypt='wpa2')  # 35 meters east, 5.5 meters up

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="ITU", nFLOORS=1, LF=10) 

    info("*** Configuring nodes\n")
    net.configureNodes()

    info("*** Associating Stations\n")
    ap1.setIP('192.168.42.1/24', intf='ap1-wlan1')
    ap1.cmd('brctl addbr br0')
    ap1.cmd('brctl addif br0 ap1-wlan1')
    ap1.cmd('ifconfig br0 192.168.42.1 netmask 255.255.255.0 up')
    ap1.cmd('ifconfig ap1-wlan1 0.0.0.0')
    ap1.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')

    # Add links directly between the AP and each station
    for sta in [sta1, sta2, sta3, sta4, sta5, sta6, sta7, sta8, sta9, sta10, sta11]:
        net.addLink(sta, ap1)

    if '-p' not in args:
        net.plotGraph(max_x=150, max_y=150)
        

    output_path = os.path.join(os.getcwd(), 'wifi_topology.png')
    info("*** Starting network\n")
    net.build()
    ap1.start([])
    info("*** Plotting network graph\n")
    plt.savefig(output_path, bbox_inches='tight')

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
        for node in net.stations:
            info = f"<Station {node.name}: {node.name}-wlan0:{node.IP()} pid={node.pid}>"
            f.write(info + "\n")
        ap = net.get('ap1')
        ap_info = f"<AP {ap.name}: {ap.name}-wlan1:{ap.IP()} pid={ap.pid}>"
        f.write(ap_info + "\n")

    print(f"Node info written to {output_file}")

#heat map

if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
