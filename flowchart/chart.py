import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey

def create_ap_station_initialization():
    plt.figure()
    # AP Initialization and Station Initialization
    Sankey(flows=[1.0, -1.0],
           labels=['AP Initialization', 'Station Initialization'],
           orientations=[-1, 1]).finish()
    plt.title('AP and Station Initialization')
    plt.savefig('ap_station_initialization.png')

def create_time_period_update():
    plt.figure()
    # Time Period Update for AP and Station
    Sankey(flows=[0.5, -0.5],
           labels=['Time Period Update (AP)', 'Time Period Update (Station)'],
           orientations=[0, 0]).finish()
    plt.title('Time Period Update')
    plt.savefig('time_period_update.png')

def create_packet_flow():
    plt.figure()
    # Packet Transmission and Packet Processing
    Sankey(flows=[0.5, -0.5],
           labels=['Packet Transmission', 'Packet Processing'],
           orientations=[1, -1]).finish()
    plt.title('Packet Transmission and Processing')
    plt.savefig('packet_flow.png')

def create_station_association():
    plt.figure()
    # New Station Association and Table Update
    Sankey(flows=[0.5, -0.5],
           labels=['New Station Association', 'Table Update'],
           orientations=[1, -1]).finish()
    plt.title('New Station Association and Table Update')
    plt.savefig('station_association.png')

if __name__ == '__main__':
    create_ap_station_initialization()
    create_time_period_update()
    create_packet_flow()
    create_station_association()
