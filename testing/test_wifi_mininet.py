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

    info("*** Creating nodes\n")
    # mode a = 5GHz, channel 36 (Internal signal range is 35mts)
    # mode b = 2.4GHz channel 1
    # modes are a, b, g, n
    # rts_threshold=2347 means that the RTS/CTS mechanism will be used for frames larger than 2347 bytes
    ap1 = net.addAccessPoint('ap1', ssid='new-ssid', mode='a', channel='36',
                             position='60,60,0',passwd='123456789a', encrypt='wpa3', rsn_pairwise='CCMP', failMode="standalone", datapath='user', rts_threshold=500, txpower=13)
    sta1 = net.addStation('sta1', ip='192.168.42.2/24', position='62,60,0', passwd='123456789a', encrypt='wpa3', range=35) #2 meters away from AP
    sta2 = net.addStation('sta2', ip='192.168.42.3/24', position='64.95,64.95,0', passwd='123456789a', encrypt='wpa3', range=35) #7 meters away from AP
    sta3 = net.addStation('sta3', ip='192.168.42.4/24', position='60,75,0', passwd='123456789a', encrypt='wpa3', range=35) #15 meters away from AP
    sta4 = net.addStation('sta4', ip='192.168.42.5/24', position='42.68,77.32,0', passwd='123456789a', encrypt='wpa3', range=35) #25 meters away from AP
    sta5 = net.addStation('sta5', ip='192.168.42.6/24', position='25,60,0', passwd='123456789a', encrypt='wpa3', range=35) #35 meters away from AP
    #net.addStation('sta2', mac='00:00:00:00:00:03', ip='10.0.0.2/8',
    #               position='20,50,0', passwd='123456789a', encrypt='wpa2')
    #net.addStation('sta3', mac='00:00:00:00:00:04', ip='10.0.0.3/8',
    #               position='20,60,10', passwd='123456789a', encrypt='wpa2')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=4)
    #LF: floor penetration loss factor
    # nFLOORS: number of floors
    #net.setPropagationModel(model="ITU", nFLOORS=2, LF=20, pL=5) 

    info("*** Configuring nodes\n")
    net.configureNodes()
    info("*** Associating Stations\n")
    net.addLink(sta1, ap1)
    net.addLink(sta2, ap1)
    net.addLink(sta3, ap1)
    net.addLink(sta4, ap1)
    net.addLink(sta5, ap1)

    ap1.setIP('192.168.42.1/24', intf='ap1-wlan1')

    if '-p' not in args:
        net.plotGraph(max_x=120, max_y=120)
        

    info("*** Starting network\n")
    net.build()
    ap1.start([])
    info("*** Plotting network graph\n")
    # Save the plot as a PNG file
    plt.savefig('/home/rathan/Downloads/hwsim_test/testing/mininet_wifi_topology.png', bbox_inches='tight')  # Save the figure to a file

    info("*** plotting heat map\n")
    # Extract the coordinates of AP and stations for plotting
    #ap1_pos = parse_position(ap1.params['position'])
    #station_positions = {sta: parse_position(pos) for sta, pos in stations.items()}

    # Call the plotting function
    #plot_heat_map_and_stations(ap1_pos, station_positions)

    #time.sleep(3)
    # Collect RSSI values and plot the signal strength map
    # Example usage in the topology function
    rssi_values = get_rssi_values(net, [sta1, sta2, sta3, sta4, sta5])
    #plot_rssi([sta1, sta2, sta3, sta4, sta5], rssi_values)

    dump_node_info(net)

    ap1.cmd('ifconfig ap1-wlan1 -promisc')

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()






def plot_rssi(stations, rssi_values):
    positions = [(62,70,0), (40,50,0), (80,75,0), (30,80,0), (100,40,0)]
    info("*** Plotting rssi graph with heatmap\n")
    
    x_vals = [pos[0] for pos in positions]
    y_vals = [pos[1] for pos in positions]

    # Create grid for interpolation
    grid_x, grid_y = np.mgrid[0:125:200j, 0:125:200j]

    # Interpolate the RSSI values onto the grid
    grid_z = griddata((x_vals, y_vals), rssi_values, (grid_x, grid_y), method='cubic')

    # Plot the heatmap
    plt.figure(figsize=(10, 8))  # Increase figure size
    plt.imshow(grid_z.T, extent=(0, 125, 0, 125), origin='lower', cmap='Blues', alpha=0.7)
    plt.colorbar(label='RSSI (dBm)')
    
    # Plot station positions and RSSI values
    plt.scatter(x_vals, y_vals, c=rssi_values, cmap='Blues', s=150, edgecolor='black')
    
    for i, sta in enumerate(stations):
        plt.text(x_vals[i] + 1, y_vals[i] + 1, f'{sta.name}: {rssi_values[i]:.1f}', fontsize=9, ha='center')

    # Plot AP position
    plt.scatter(60, 60, c='red', s=200, label='AP (60, 60, 0)', edgecolor='black')
    plt.text(60, 60, 'AP', fontsize=12, fontweight='bold', color='black', ha='center')

    plt.xlabel('X Position (meters)')
    plt.ylabel('Y Position (meters)')
    plt.xlim(0, 125)  # Extend the x-limit to prevent labels from being cut off
    plt.ylim(0, 125)  # Extend the y-limit similarly
    plt.title('RSSI Heatmap')
    plt.grid(True)
    plt.savefig('/home/rathan/Downloads/hwsim_test/testing/rssi_improved.png')  # Save the figure to a file

def dump_node_info(net):
    "Dump station information (IP and PID) to a file"
    output_file = "/home/rathan/Downloads/hwsim_test/testing/nodes.txt"

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

def parse_position(pos_str):
    """Parse the position string 'x,y,z' and return a tuple of floats (x, y, z)."""
    return tuple(map(float, pos_str.split(',')))

def calculate_signal_strength(ap_pos, x, y, tx_power=10, path_loss_exp=4.5):
    """Calculate signal strength at a point (x, y) based on distance from AP."""
    distance = np.sqrt((x - ap_pos[0])**2 + (y - ap_pos[1])**2)
    
    # Simple log-distance path loss model
    if distance == 0:
        return tx_power  # No loss at the AP's exact position
    else:
        return tx_power - (10 * path_loss_exp * np.log10(distance))

def create_heat_map(ap_pos, tx_power=10, path_loss_exp=4.5, grid_size=(120, 120), resolution=1):
    """Create a heat map grid showing signal strength from the AP."""
    x_range = np.arange(0, grid_size[0], resolution)
    y_range = np.arange(0, grid_size[1], resolution)
    
    # Create grid for heat map
    heat_map = np.zeros((len(y_range), len(x_range)))
    
    for i, x in enumerate(x_range):
        for j, y in enumerate(y_range):
            heat_map[j, i] = calculate_signal_strength(ap_pos, x, y, tx_power, path_loss_exp)
    
    return heat_map, x_range, y_range

def plot_heat_map_and_stations(ap1_pos, station_positions):
    """Function to plot heat map and station positions with different colors and symbols."""
    # Create the heat map
    heat_map, x_range, y_range = create_heat_map(ap1_pos, tx_power=10, path_loss_exp=4.5)

    # Define station colors and markers for the plot
    station_colors = ['blue', 'green', 'orange', 'purple', 'pink']
    station_symbols = ['o', 's', '^', 'D', '*']
    
    # Plot the heat map
    plt.figure(figsize=(10, 10))
    plt.title("AP Heat Map with Station Positions")
    plt.xlabel("X Position (meters)")
    plt.ylabel("Y Position (meters)")
    plt.grid(True)

    # Display heat map using imshow with color scale
    im = plt.imshow(heat_map, extent=(0, 120, 0, 120), origin='lower', cmap='hot', alpha=0.6)
    
    # Add color bar to show signal strength scale
    cbar = plt.colorbar(im)
    cbar.set_label('Signal Strength (dBm)')

    # Plot the AP as a red triangle
    plt.scatter(ap1_pos[0], ap1_pos[1], s=300, c='red', marker='^', label='AP1')

    # Plot the STAs with different colors and markers
    for i, (sta_name, sta_pos) in enumerate(station_positions.items()):
        color = station_colors[i % len(station_colors)]
        symbol = station_symbols[i % len(station_symbols)]
        plt.scatter(sta_pos[0], sta_pos[1], s=150, c=color, marker=symbol, label=sta_name.upper())
        plt.text(sta_pos[0], sta_pos[1]+1.5, sta_name.upper(), fontsize=10, ha='center', va='bottom')

    # Add the legend in the upper corner
    plt.legend(loc='upper right')

    # Save the plot as a PNG file
    plt.savefig('/home/rathan/Downloads/hwsim_test/testing/heat_map.png', bbox_inches='tight')  # Save the figure to a file


if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
