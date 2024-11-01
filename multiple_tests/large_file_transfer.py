import subprocess
import time

# Path to the nodes.txt file
nodes_file = 'nodes.txt'

# Function to get the PID of a specific station or AP from nodes.txt
def get_pid(node_name):
    with open(nodes_file, 'r') as file:
        for line in file:
            if node_name in line:
                pid = line.split("pid=")[1].split(">")[0].strip()  # Get the PID before the closing '>'
                return pid
    return None

# Function to start iperf3 server on a station or AP
def start_iperf3_server(node_pid):
    try:
        cmd = ['sudo', 'mnexec', '-a', node_pid, 'iperf3', '-s', '-D']
        print(f"Starting iperf3 server on node with PID {node_pid}: {' '.join(cmd)}")
        subprocess.run(cmd, capture_output=True, text=True)
    except Exception as e:
        print(f"Error starting iperf3 server: {e}")

# Function to run iperf3 between two nodes and return filtered output
def run_iperf3(tx_node, rx_node_ip, tx_pid):
    try:
        cmd = ['sudo', 'mnexec', '-a', tx_pid, 'iperf3', '-c', rx_node_ip, '-n', '10M']  # Adjusted for 1GB transfer
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Filter the result to capture only relevant lines
        filtered_output = ""
        for line in result.stdout.splitlines():
            if "sender" in line or "receiver" in line:
                filtered_output += line + "\n"
        
        print("Filtered iperf3 output:")
        print(filtered_output)
        
        return filtered_output  # Return only the filtered lines
    except Exception as e:
        print(f"Error running iperf3: {e}")
    return None

# Function to log the filtered iperf3 output to a file
def log_iperf3_output(tx_node, rx_node, output, log_file='file_transfer_kern_time.txt'):
    with open(log_file, 'a') as f:
        f.write(f"Result for {tx_node} -> {rx_node}:\n")
        f.write(output)
        f.write("\n\n")  # Add some spacing between test results

# Main script to perform the throughput test between all node pairs
def test_throughput(nodes):
    # Start iperf3 servers on all nodes first
    for rx_node in nodes:
        rx_pid = get_pid(rx_node)
        if rx_pid:
            start_iperf3_server(rx_pid)
    
    time.sleep(2)  # Give time for all servers to start

    for tx_node in nodes:
        tx_pid = get_pid(tx_node)
        if tx_pid:
            # Get IP of the transmitting node
            tx_ip = f"192.168.42.{nodes.index(tx_node) + 1}"  # AP would have a unique IP

            # Run the test from TX node to each RX node
            for rx_node in nodes:
                if tx_node != rx_node:  # Avoid self-transfers
                    # Assuming RX IPs follow the same format (192.168.42.X)
                    rx_ip = f"192.168.42.{nodes.index(rx_node) + 1}"
                    
                    print(f"Testing {tx_node} -> {rx_node}")
                    iperf_output = run_iperf3(tx_node, rx_ip, tx_pid)
                    if iperf_output:
                        log_iperf3_output(tx_node, rx_node, iperf_output)
                    else:
                        print(f"No iperf3 output for {tx_node} -> {rx_node}")
                    
                    # Pause briefly between tests
                    time.sleep(1)

# Define your nodes, including AP and stations (e.g., "ap1" as the AP)
nodes = ["ap1", "sta1", "sta2", "sta3", "sta4", "sta5", "sta6", "sta7", "sta8", "sta9", "sta10", "sta11"]

# Run the throughput test
test_throughput(nodes)
