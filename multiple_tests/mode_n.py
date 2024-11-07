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
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference, noise_th=-91, fading_cof=3)
    #net = Mininet_wifi()

    info("*** Creating nodes\n")
    # mode a = 5GHz, channel 36 (Internal signal range is 35mts)
    # mode b = 2.4GHz channel 1
    # modes are a, b, g, n
    # rts_threshold=2347 means that the RTS/CTS mechanism will be used for frames larger than 2347 bytes


    ap1 = net.addAccessPoint('ap1', ssid='new-ssid', mode='n2', channel='1', ip='192.168.42.1/24',
                             position='70,70,0',passwd='123456789a', encrypt='wpa2', rsn_pairwise='CCMP', ieee80211w='2', failMode="standalone", datapath='kernel', rts_threshold=500, txpower=13, ieee80211n='1', ht_capab='[SHORT-GI-40][HT40+][HT40-][DSSS_CCK-40]',require_ht='1', country_code='US', ieee80211d= '1', ieee80211h='1', wmm_enabled='1', wme_enabled='1')
    #sta1 = net.addStation('sta1', ip='192.168.42.2/24', position='100,120,0', wpa_supplicant_file='/media/sf_rathan-dataset/msc_thesis/hwsim_test/confs/wpa_supplicant.conf') txpower=20
    sta1 = net.addStation('sta1', ip='192.168.42.2/24', position='71.00, 70.00, 0', passwd='123456789a', encrypt='wpa2', ieee80211w='2', ieee80211r='1', ieee80211k='1', ieee80211v='1', ieee80211r_ft_psk='1', ieee80211r_ft_sae='1', ieee80211r_ft='1')
    sta2 = net.addStation('sta2', ip='192.168.42.3/24', position='64.18, 75.34, 2',passwd='123456789a', encrypt='wpa2', ieee80211w='2', ieee80211r='1', ieee80211k='1', ieee80211v='1', ieee80211r_ft_psk='1', ieee80211r_ft_sae='1', ieee80211r_ft='1')
    sta3 = net.addStation('sta3', ip='192.168.42.4/24', position='71.29, 55.26, 4', passwd='123456789a', encrypt='wpa2', ieee80211w='2', ieee80211r='1', ieee80211k='1', ieee80211v='1', ieee80211r_ft_psk='1', ieee80211r_ft_sae='1', ieee80211r_ft='1')
    sta4 = net.addStation('sta4', ip='192.168.42.5/24', position='83.21, 87.22, 6', passwd='123456789a', encrypt='wpa2', ieee80211w='2', ieee80211r='1', ieee80211k='1', ieee80211v='1', ieee80211r_ft_psk='1', ieee80211r_ft_sae='1', ieee80211r_ft='1')
    sta5 = net.addStation('sta5', ip='192.168.42.6/24', position='41.83, 65.03, 8', passwd='123456789a', encrypt='wpa2', ieee80211w='2', ieee80211r='1', ieee80211k='1', ieee80211v='1', ieee80211r_ft_psk='1', ieee80211r_ft_sae='1', ieee80211r_ft='1')
    sta6 = net.addStation('sta6', ip='192.168.42.7/24', position='99.94, 50.93, 10', passwd='123456789a', encrypt='wpa2', ieee80211w='2', ieee80211r='1', ieee80211k='1', ieee80211v='1', ieee80211r_ft_psk='1', ieee80211r_ft_sae='1', ieee80211r_ft='1')
    sta7 = net.addStation('sta7', ip='192.168.42.8/24', position='59.03, 110.96, 12', passwd='123456789a', encrypt='wpa2', ieee80211w='2', ieee80211r='1', ieee80211k='1', ieee80211v='1', ieee80211r_ft_psk='1', ieee80211r_ft_sae='1', ieee80211r_ft='1')
    sta8 = net.addStation('sta8', ip='192.168.42.9/24', position='47.24, 26.27, 14', passwd='123456789a', encrypt='wpa2', ieee80211w='2', ieee80211r='1', ieee80211k='1', ieee80211v='1', ieee80211r_ft_psk='1', ieee80211r_ft_sae='1', ieee80211r_ft='1')
    sta9 = net.addStation('sta9', ip='192.168.42.10/24', position='122.81, 89.22, 16', passwd='123456789a', encrypt='wpa2', ieee80211w='2', ieee80211r='1', ieee80211k='1', ieee80211v='1', ieee80211r_ft_psk='1', ieee80211r_ft_sae='1', ieee80211r_ft='1')
    sta10 = net.addStation('sta10', ip='192.168.42.11/24', position='11.70, 94.15, 18', passwd='123456789a', encrypt='wpa2', ieee80211w='2', ieee80211r='1', ieee80211k='1', ieee80211v='1', ieee80211r_ft_psk='1', ieee80211r_ft_sae='1', ieee80211r_ft='1')
    # Adjusted position for sta10 at 35 meters to target an RSSI of -89 dBm
    sta11 = net.addStation('sta11', ip='192.168.42.12/24', position='99.58, 6.56, 20', passwd='123456789a', encrypt='wpa2', ieee80211w='2', ieee80211r='1', ieee80211k='1', ieee80211v='1', ieee80211r_ft_psk='1', ieee80211r_ft_sae='1', ieee80211r_ft='1')

    #net.addStation('sta2', mac='00:00:00:00:00:03', ip='10.0.0.2/8',
    #               position='20,50,0', passwd='123456789a', encrypt='wpa2')
    #net.addStation('sta3', mac='00:00:00:00:00:04', ip='10.0.0.3/8',
    #               position='20,60,10', passwd='123456789a', encrypt='wpa2')

    info("*** Configuring Propagation Model\n")
    #net.setPropagationModel(model="logDistance", exp=4.1)
    #LF: floor penetration loss factor
    # nFLOORS: number of floors
    net.setPropagationModel(model="ITU", nFLOORS=1, LF=10) 

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
        net.plotGraph(max_x=150, max_y=150)
        

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
