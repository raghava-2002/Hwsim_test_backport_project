from mininet.net import Mininet
from mn_wifi.cli import CLI
import os
import time
import multiprocessing

def run_iperf_client(station, ap_ip, port, duration, output_file):
    "Run iperf3 test between a station and the AP on a specific port."
    print(f"Running iperf3 test for {station.name} on port {port}")
    result = station.cmd(f'iperf3 -c {ap_ip} -p {port} -t {duration} -J > {output_file}')
    print(f"Test for {station.name} on port {port} saved to {output_file}")

def start_iperf_servers(ap):
    "Start iperf3 servers on AP across 10 ports."
    for i in range(10):
        port = 5201 + i
        ap.cmd(f'iperf3 -s -p {port} -D')
    print("iperf3 servers started on AP")

def run_parallel_tests(net):
    "Run iperf3 clients in parallel for all stations."
    
    # Get the AP and stations
    ap = net.get('ap1')
    stations = [net.get(f'sta{i+1}') for i in range(10)]
    ap_ip = ap.IP()

    # Start iperf3 servers on AP
    start_iperf_servers(ap)

    # Create directory for storing results
    output_dir = "/home/rathan/Downloads/hwsim_test/mininet_testing/test_data/parallel_tests"
    os.makedirs(output_dir, exist_ok=True)

    # List to hold processes for running parallel iperf3 tests
    processes = []

    # Launch parallel iperf3 tests for each station
    for i, sta in enumerate(stations):
        port = 5201 + i
        output_file = f'{output_dir}/sta{i+1}_iperf3.json'
        p = multiprocessing.Process(target=run_iperf_client, args=(sta, ap_ip, port, 60, output_file))
        p.start()  # Start the iperf3 test in parallel
        processes.append(p)

    # Wait for all processes to complete
    for p in processes:
        p.join()

    print("All iperf3 tests completed.")

def setup_network():
    "Create the network with AP and 10 stations, and run iperf3 tests in parallel."

    net = Mininet()

    # Set up AP and Stations (assuming IPs are already configured)
    ap1 = net.addAccessPoint('ap1', ssid="simplewifi", mode="g", channel="1",
                             passwd='123456789a', encrypt='wpa2', ip='192.168.42.1/24')

    stations = []
    for i in range(10):
        sta = net.addStation(f'sta{i+1}', passwd='123456789a', encrypt='wpa2', ip=f'192.168.42.{i+2}/24')
        stations.append(sta)

    # Configure and build the network
    net.configureNodes()
    net.build()
    ap1.start([])

    # Run the iperf3 tests in parallel
    run_parallel_tests(net)

    # Start CLI to interact with the network
    CLI(net)

    # Stop the network
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    setup_network()
