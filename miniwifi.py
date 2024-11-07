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
    #ap1 = net.addAccessPoint('ap1', hostapd_file='/media/sf_rathan-dataset/msc_thesis/hwsim_test/confs/mininet_ap.apconf', position='105,130,0')
       # Configure the AP with all desired settings inline
    ap1 = net.addAccessPoint('ap1', ssid='new-ssid', mode='n2', channel='1', ip='192.168.42.1/24',
                             position='60,60,0',passwd='123456789a', encrypt='wpa2', rsn_pairwise='CCMP', ieee80211w='2', failMode="standalone", datapath='kernel', rts_threshold=500, txpower=13,ieee80211n='1', ht_capab='[SHORT-GI-40][HT40+][HT40-][DSSS_CCK-40]',require_ht='1', country_code='US', ieee80211d= '1', ieee80211h='1', wmm_enabled='1', wme_enabled='1')
    #sta1 = net.addStation('sta1', ip='192.168.42.2/24', position='100,120,0', wpa_supplicant_file='/media/sf_rathan-dataset/msc_thesis/hwsim_test/confs/wpa_supplicant.conf')
    sta2 = net.addStation('sta2', ip='192.168.42.2/24', position='60,62,1', passwd='123456789a', encrypt='wpa2', ieee80211w='2',ieee80211r='1', ieee80211k='1', ieee80211v='1', ieee80211r_ft_psk='1', ieee80211r_ft_sae='1', ieee80211r_ft='1')
    #net.addStation('sta3', mac='00:00:00:00:00:04', ip='10.0.0.3/8',
    #               position='20,60,10', passwd='123456789a', encrypt='wpa2')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=4)

    info("*** Configuring nodes\n")
    net.configureNodes()
    info("*** Associating Stations\n")
    #net.addLink(sta1, ap1)
    net.addLink(sta2, ap1)

    ap1.setIP('192.168.42.1/24', intf='ap1-wlan1')



    # Add the following commands after creating the AP and configuring the IPs
    ap1.cmd('brctl addbr br0')  # Create the bridge
    ap1.cmd('brctl addif br0 ap1-wlan1')  # Add the wireless interface to the bridge
    ap1.cmd('ifconfig br0 192.168.42.1 netmask 255.255.255.0 up')  # Assign IP to the bridge
    ap1.cmd('ifconfig ap1-wlan1 0.0.0.0')  # Clear the IP from the wireless interface
    ap1.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')  # Enable IP forwarding


    # Start hostapd on AP manually using the provided hostapd.conf file
    #ap1.cmd('hostapd /media/sf_rathan-dataset/msc_thesis/hwsim_test/confs/hostapd.conf &')

    # Start wpa_supplicant on station manually using the provided wpa_supplicant.conf file
    #sta1.cmd('wpa_supplicant -B -i sta1-wlan0 -c /media/sf_rathan-dataset/msc_thesis/hwsim_test/confs/wpa_supplicant.conf')

    # Continue with the rest of your script
    # Apply RTS setting manually
    #sta1.cmd('iwconfig sta1-wlan0 rts 500')
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
