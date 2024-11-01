#!/usr/bin/env python

"Setting the position of Nodes with wmediumd to calculate the interference"

import sys

from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference
import matplotlib.pyplot as plt

def topology(args):
    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference,
                       noise_th=-91, fading_cof=3)

    info("*** Creating nodes\n")
    # mode a = 5GHz, channel 36
    # mode b = 2.4GHz channel 1
    # modes are a, b, g, n
    #ap1 = net.addAccessPoint('ap1', ssid='new-ssid', mode='a', channel='36', ht_cap='HT20', rts='500',
    #                         position='105,130,0',passwd='123456789a', encrypt='wpa3', rsn_pairwise='CCMP', failMode="standalone", datapath='kernel')
    ap1 = net.addAccessPoint('ap1', position='105,130,0', hostapd_file='/media/sf_rathan-dataset/msc_thesis/hwsim_test/confs/hostapd.conf')
    sta1 = net.addStation('sta1', ip='192.168.42.2/24', position='100,120,0', wpa_supplicant_file='/media/sf_rathan-dataset/msc_thesis/hwsim_test/confs/wpa_supplicant.conf')
    #net.addStation('sta2', mac='00:00:00:00:00:03', ip='10.0.0.2/8',
    #               position='20,50,0', passwd='123456789a', encrypt='wpa2')
    #net.addStation('sta3', mac='00:00:00:00:00:04', ip='10.0.0.3/8',
    #               position='20,60,10', passwd='123456789a', encrypt='wpa2')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=4)

    info("*** Configuring nodes\n")
    net.configureNodes()
    info("*** Associating Stations\n")
    net.addLink(sta1, ap1)

    ap1.setIP('192.168.42.1/24', intf='ap1-wlan1')

    # Add the following commands after creating the AP and configuring the IPs
    ap1.cmd('brctl addbr br0')  # Create the bridge
    ap1.cmd('brctl addif br0 ap1-wlan1')  # Add the wireless interface to the bridge
    ap1.cmd('ifconfig br0 192.168.42.1 netmask 255.255.255.0 up')  # Assign IP to the bridge
    ap1.cmd('ifconfig ap1-wlan1 0.0.0.0')  # Clear the IP from the wireless interface
    ap1.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')  # Enable IP forwarding

    # Continue with the rest of your script
    # Apply RTS setting manually
    sta1.cmd('iwconfig sta1-wlan0 rts 500')
    ap1.cmd('iwconfig ap1-wlan1 rts 500')


    if '-p' not in args:
        net.plotGraph(max_x=250, max_y=250)

    info("*** Starting network\n")
    net.build()
    ap1.start([])
    info("*** Plotting network graph\n")
    # Save the plot as a PNG file
    plt.savefig('/home/rathan/Downloads/hwsim_test/mininet_wifi_topology.png')  # Save the figure to a file
    # Disable promiscuous mode on the AP interface
    ap1.cmd('ifconfig ap1-wlan1 -promisc')

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
