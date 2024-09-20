#!/usr/bin/env python

"Setting the position of Nodes with wmediumd to calculate the interference"

import sys

from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference


def topology(args):
    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference,
                       noise_th=-91, fading_cof=3)

    info("*** Creating nodes\n")
    ap1 = net.addAccessPoint('ap1', ssid='new-ssid', mode='a', channel='36',
                             position='15,30,0',passwd='123456789a', encrypt='wpa2', rsn_pairwise='CCMP', failMode="standalone", datapath='user')
    sta1 = net.addStation('sta1', ip='192.168.42.2/24',
                   position='10,20,0', passwd='123456789a', encrypt='wpa2')
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

    if '-p' not in args:
        net.plotGraph(max_x=100, max_y=100)

    info("*** Starting network\n")
    net.build()
    ap1.start([])
    
    # Disable promiscuous mode on the AP interface
    ap1.cmd('ifconfig ap1-wlan1 -promisc')

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)