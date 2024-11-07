import os
import subprocess
import time
from datetime import datetime

# Configuration
num_tests = 10  # Number of tests to run

working_directory = os.getcwd()  # or use a specific path if needed
#change mode n or a or b or g
# for with wmd change to mode_n.py and for no wmd change to no_wm_mode_n.py
#for mode_a change to mode_a.py and for no wmd change to no_wmd_mode_a.py
mininet_script_path = os.path.join(working_directory, 'mode_n.py')
# Change the path for other schemes if needed  
#('kernel_time', 'no_rnd', 'ap_trigger')
# #('with_wmd', 'without_wmd')
result_base_dir = os.path.join(working_directory, 'iperf3_results', 'no_rnd', 'mode_n', 'with_wmd')
iperf_duration = 30  # Duration of iperf test in seconds
AP_IP = "192.168.42.1"
start_port = 5201
nodes_file = os.path.join(working_directory, 'nodes.txt')

# Function to get a timestamp
def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

# Function to extract the PID from nodes.txt
def get_pid(station_name):
    with open(nodes_file, 'r') as file:
        for line in file:
            if station_name in line:
                return line.split("pid=")[1].strip()
    return None

# Function to run iperf3 test for a station (TCP/UDP) in parallel
def run_iperf3_test(station_name, station_pid, port, test_folder, protocol):
    output_dir = os.path.join(test_folder, protocol)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{station_name}_iperf3.json")
    
    if protocol == "tcp":
        cmd = [
            'sudo', 'mnexec', '-a', station_pid, 'iperf3', '-c', AP_IP, '-p', str(port),
            '-t', str(iperf_duration), '-J'
        ]
    elif protocol == "udp":
        cmd = [
            'sudo', 'mnexec', '-a', station_pid, 'iperf3', '-c', AP_IP, '-p', str(port), '-u',
            '-t', str(iperf_duration), '-J'
        ]
    
    # Run the command in parallel
    proc = subprocess.Popen(cmd, stdout=open(output_file, 'w'))
    return proc

# Function to start iperf3 servers on AP for 11 ports
def start_iperf3_servers():
    print("Starting iperf3 servers on AP...")
    for i in range(11):
        port = start_port + i
        print(f"Starting iperf3 server on port {port}")
        subprocess.Popen(['iperf3', '-s', '-p', str(port), '-D'])
    print("All iperf3 servers started.")
    time.sleep(5)

# Main testing function
def run_test(test_num):
    timestamp = get_timestamp()
    test_folder = f"{result_base_dir}/test_{timestamp}"
    os.makedirs(test_folder, exist_ok=True)

    # Start Mininet
    print(f"Starting Mininet for test {test_num}...")
    subprocess.run(['sudo', 'mn', '-c'])  # Clean any previous Mininet setup
    mininet_process = subprocess.Popen(['sudo', 'python3', mininet_script_path])

    # Wait for Mininet CLI to open
    time.sleep(20)

    # Start iperf3 servers on AP
    start_iperf3_servers()

    # Run all TCP tests in parallel
    print(f"Running all TCP tests for Test {test_num} in parallel...")
    processes = []
    for i in range(1, 12):
        station_name = f"sta{i}"
        port = start_port + (i - 1)
        station_pid = get_pid(station_name)
        if station_pid:
            proc = run_iperf3_test(station_name, station_pid, port, test_folder, "tcp")
            processes.append(proc)
    
    # Wait for all processes to complete
    for proc in processes:
        proc.wait()

    # Optional: Run all UDP tests in parallel
    processes = []
    print(f"Running all UDP tests for Test {test_num} in parallel...")
    for i in range(1, 12):
        station_name = f"sta{i}"
        port = start_port + (i - 1)
        station_pid = get_pid(station_name)
        if station_pid:
            proc = run_iperf3_test(station_name, station_pid, port, test_folder, "udp")
            processes.append(proc)
    
    for proc in processes:
        proc.wait()

    # Terminate Mininet process
    print(f"Terminating Mininet for test {test_num}...")
    mininet_process.terminate()
    time.sleep(2)

# Main loop to run tests
for test_num in range(1, num_tests + 1):
    run_test(test_num)
    print(f"Test {test_num} completed. Cleaning up...")
    subprocess.run(['sudo', 'mn', '-c'])
    time.sleep(2)

print("All tests completed.")
