import subprocess
import time

# Path to the nodes.txt file
nodes_file = 'nodes.txt'

# Function to get the PID of a specific station from nodes.txt
def get_pid(station_name):
    with open(nodes_file, 'r') as file:
        for line in file:
            if station_name in line:
                # Extract the PID correctly by splitting the line based on 'pid='
                pid = line.split("pid=")[1].split(">")[0].strip()  # Get the PID before the closing '>'
                return pid
    return None

# Function to start iperf3 server on a station
def start_iperf3_server(station_pid):
    try:
        # Start iperf3 server using mnexec
        cmd = ['sudo', 'mnexec', '-a', station_pid, 'iperf3', '-s', '-D']
        print(f"Starting iperf3 server on station with PID {station_pid}: {' '.join(cmd)}")
        subprocess.run(cmd, capture_output=True, text=True)
    except Exception as e:
        print(f"Error starting iperf3 server: {e}")

# Function to run iperf3 between two stations and return the entire result output
def run_iperf3(tx_station, rx_station_ip, tx_pid):
    try:
        # Running iperf3 client on the TX station using mnexec and subprocess
        cmd = ['sudo', 'mnexec', '-a', tx_pid, 'iperf3', '-c', rx_station_ip, '-n', '20M']
        print(f"Running command: {' '.join(cmd)}")  # Print the command for debugging
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("iperf3 stdout:")
        print(result.stdout)  # Print the iperf3 output for debugging
        print("iperf3 stderr:")
        print(result.stderr)  # Print any errors or warnings from iperf3
        
        return result.stdout  # Return the entire stdout as the result
    except Exception as e:
        print(f"Error running iperf3: {e}")
    return None

# Function to log the entire iperf3 output to a file
def log_iperf3_output(tx_station, rx_station, output, log_file='iperf3_log.txt'):
    with open(log_file, 'a') as f:
        f.write(f"Result for {tx_station} -> {rx_station}:\n")
        f.write(output)  # Log the full iperf3 output
        f.write("\n\n")  # Add some spacing between test results

# Main script to perform the throughput test between all station pairs
def test_throughput(stations):
    # Start iperf3 servers on all stations first
    for rx_station in stations:
        rx_pid = get_pid(rx_station)
        if rx_pid:
            start_iperf3_server(rx_pid)
    
    time.sleep(2)  # Give some time for all servers to start

    for tx_station in stations:
        tx_pid = get_pid(tx_station)
        if tx_pid:
            # Get IP of TX station (using iperf3, typically IPs are like 192.168.42.X)
            tx_ip = f"192.168.42.{stations.index(tx_station) + 2}"

            # Run the test from TX station to each RX station
            for rx_station in stations:
                if tx_station != rx_station:  # Avoid self-transfers
                    # Assuming RX IPs follow the same format (192.168.42.X)
                    rx_ip = f"192.168.42.{stations.index(rx_station) + 2}"
                    
                    print(f"Testing {tx_station} -> {rx_station}")
                    iperf_output = run_iperf3(tx_station, rx_ip, tx_pid)
                    if iperf_output:
                        log_iperf3_output(tx_station, rx_station, iperf_output)
                    else:
                        print(f"No iperf3 output for {tx_station} -> {rx_station}")
                    
                    # Pause briefly between tests to avoid overwhelming the network
                    time.sleep(1)

# Define your stations (for example, sta1 to sta11)
stations = ["sta1", "sta2", "sta3", "sta4", "sta5", "sta6", "sta7", "sta8", "sta9", "sta10", "sta11"]

# Run the throughput test
test_throughput(stations)
