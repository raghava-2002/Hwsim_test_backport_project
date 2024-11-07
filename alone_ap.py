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
    ap1 = net.addAccessPoint('ap1', position='105,130,0')
    sta1 = net.addStation('sta1', ip='192.168.42.2/24', position='100,120,0', wpa_supplicant_file='/media/sf_rathan-dataset/msc_thesis/hwsim_test/confs/wpa_supplicant.conf')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=4)

    info("*** Configuring nodes\n")
    net.configureNodes()
    info("*** Associating Stations\n")
    net.addLink(sta1, ap1)

    # Set AP IP manually if needed
    ap1.setIP('192.168.42.1/24', intf='ap1-wlan1')

    # Disable Mininet's AP management by not calling ap1.start([])
    # Manually start hostapd using the command below

    # Run hostapd manually with the specified configuration file
    ap1.cmd('hostapd /media/sf_rathan-dataset/msc_thesis/hwsim_test/confs/hostapd.conf &')

    # Apply RTS settings
    sta1.cmd('iwconfig sta1-wlan0 rts 500')
    ap1.cmd('iwconfig ap1-wlan1 rts 500')

    if '-p' not in args:
        net.plotGraph(max_x=250, max_y=250)

    info("*** Starting network\n")
    net.build()

    info("*** Plotting network graph\n")
    # Save the plot as a PNG file
    #plt.savefig('/home/rathan/Downloads/hwsim_test/mininet_wifi_topology.png')  # Save the figure to a file
    # Disable promiscuous mode on the AP interface
    ap1.cmd('ifconfig ap1-wlan1 -promisc')

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
