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

    ap1 = net.addAccessPoint('ap1', ssid='new-ssid', mode='n2', channel='1', ip='192.168.42.1/24',
                             position='70,70,0', passwd='123456789a', encrypt='wpa2', rsn_pairwise='CCMP',
                             ieee80211w='2', failMode="standalone", datapath='kernel',
                             rts_threshold=500, ieee80211n='1', ht_capab='[SHORT-GI-40][HT40+][HT40-][DSSS_CCK-40]',
                             require_ht='1', country_code='US', ieee80211d='1', ieee80211h='1',
                             wmm_enabled='1', wme_enabled='1')

    # Stations setup
    sta1 = net.addStation('sta1', ip='192.168.42.2/24', position='71.00,70.00,0', passwd='123456789a', encrypt='wpa2')
    sta2 = net.addStation('sta2', ip='192.168.42.3/24', position='64.18,75.34,2', passwd='123456789a', encrypt='wpa2')
    sta3 = net.addStation('sta3', ip='192.168.42.4/24', position='71.29,55.26,4', passwd='123456789a', encrypt='wpa2')
    sta4 = net.addStation('sta4', ip='192.168.42.5/24', position='83.21,87.22,6', passwd='123456789a', encrypt='wpa2')
    sta5 = net.addStation('sta5', ip='192.168.42.6/24', position='41.83,65.03,8', passwd='123456789a', encrypt='wpa2')
    sta6 = net.addStation('sta6', ip='192.168.42.7/24', position='99.94,50.93,10', passwd='123456789a', encrypt='wpa2')
    sta7 = net.addStation('sta7', ip='192.168.42.8/24', position='59.03,110.96,12', passwd='123456789a', encrypt='wpa2')
    sta8 = net.addStation('sta8', ip='192.168.42.9/24', position='47.24,26.27,14', passwd='123456789a', encrypt='wpa2')
    sta9 = net.addStation('sta9', ip='192.168.42.10/24', position='122.81,89.22,16', passwd='123456789a', encrypt='wpa2')
    sta10 = net.addStation('sta10', ip='192.168.42.11/24', position='11.70,94.15,18', passwd='123456789a', encrypt='wpa2')
    sta11 = net.addStation('sta11', ip='192.168.42.12/24', position='99.58,6.56,20', passwd='123456789a', encrypt='wpa2')

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
