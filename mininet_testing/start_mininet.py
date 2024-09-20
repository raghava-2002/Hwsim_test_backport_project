#!/usr/bin/env python

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

def dump_node_info(net):
    "Dump station information (IP and PID) to a file"
    output_file = "/home/rathan/Downloads/hwsim_test/mininet_testing/nodes.txt"

    with open(output_file, "w") as f:
        # Iterate over all nodes (stations and AP)
        for node in net.stations:
            info = f"<Station {node.name}: {node.name}-wlan0:{node.IP()} pid={node.pid}>"
            f.write(info + "\n")
        ap = net.get('ap1')
        ap_info = f"<AP {ap.name}: {ap.name}-wlan1:{ap.IP()} pid={ap.pid}>"
        f.write(ap_info + "\n")

    print(f"Node info written to {output_file}")

def topology():
    "Create a network without using a loop."
    net = Mininet_wifi()

    info("*** Creating nodes\n")
    
    ap1 = net.addAccessPoint('ap1', ssid="simplewifi", mode="g", channel="1",
                             passwd='123456789a', encrypt='wpa2',
                             failMode="standalone", datapath='user', ip='192.168.42.1/24')

    # Manually creating and associating stations
    sta1 = net.addStation('sta1', passwd='123456789a', encrypt='wpa2', ip='192.168.42.2/24')
    sta2 = net.addStation('sta2', passwd='123456789a', encrypt='wpa2', ip='192.168.42.3/24')
    sta3 = net.addStation('sta3', passwd='123456789a', encrypt='wpa2', ip='192.168.42.4/24')
    sta4 = net.addStation('sta4', passwd='123456789a', encrypt='wpa2', ip='192.168.42.5/24')
    sta5 = net.addStation('sta5', passwd='123456789a', encrypt='wpa2', ip='192.168.42.6/24')
    sta6 = net.addStation('sta6', passwd='123456789a', encrypt='wpa2', ip='192.168.42.7/24')
    sta7 = net.addStation('sta7', passwd='123456789a', encrypt='wpa2', ip='192.168.42.8/24')
    sta8 = net.addStation('sta8', passwd='123456789a', encrypt='wpa2', ip='192.168.42.9/24')
    sta9 = net.addStation('sta9', passwd='123456789a', encrypt='wpa2', ip='192.168.42.10/24')
    sta10 = net.addStation('sta10', passwd='123456789a', encrypt='wpa2', ip='192.168.42.11/24')

    info("*** Configuring nodes\n")
    net.configureNodes()

    info("*** Associating Stations\n")
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

    ap1.setIP('192.168.42.1/24', intf='ap1-wlan1')

    info("*** Starting network\n")
    net.build()
    ap1.start([])

    dump_node_info(net)



    info("*** Plotting network graph\n")
    fig = plt.figure()  # Create a new figure
    net.plotGraph(max_x=300, max_y=300)  # Plot the network

    plt.draw()  # Ensure the plot is rendered
    plt.savefig('/home/rathan/Downloads/hwsim_test/mininet_testing/mininet_network_topology.png')
    plt.close(fig)

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()
