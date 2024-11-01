import os
import subprocess
import time
from datetime import datetime
import re

# Configuration
num_tests = 10  # Number of tests to run

working_directory = os.getcwd()  # or use a specific path if needed
mininet_script_path = os.path.join(working_directory, 'mininet_script.py')
#change the path for for other schemes this is enough
#kernel_time, no_rnd, ap_trigger
#, 'testing_more', 'new_testing', 'only_tcp'
result_base_dir = os.path.join(working_directory, 'iperf3_results', 'ap_trigger','only_tcp')
iperf_duration = 20  # Duration of iperf test in seconds
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

# Function to extract the PID from nodes.txt using regular expressions
#def get_pid(station_name, nodes_file='nodes.txt'):
    # Regular expression to capture 'pid=<digits>' pattern
#    pid_pattern = re.compile(r'pid=(\d+)')
    
#    with open(nodes_file, 'r') as file:
#        for line in file:
#            if station_name in line:
#                # Search for the PID using the regular expression
#                match = pid_pattern.search(line)
#                if match:
#                    return match.group(1)  # Return the captured digits (the PID)
 #   return None

# Function to run iperf3 test for a station (TCP/UDP)
def run_iperf3_test(station_name, station_pid, port, test_folder, protocol):
    if protocol == "tcp":
        output_file = f"{test_folder}/tcp/{station_name}_iperf3.json"
        print(f"Running TCP iperf3 test for {station_name} (PID: {station_pid}) on port {port}")
        subprocess.run([
            'sudo', 'mnexec', '-a', station_pid, 'iperf3', '-c', AP_IP, '-p', str(port),
            '-t', str(iperf_duration), '-J'
        ], stdout=open(output_file, 'w'))
    elif protocol == "udp":
        output_file = f"{test_folder}/udp/{station_name}_iperf3.json"
        print(f"Running UDP iperf3 test for {station_name} (PID: {station_pid}) on port {port}")
        subprocess.run([
            'sudo', 'mnexec', '-a', station_pid, 'iperf3', '-c', AP_IP, '-p', str(port), '-u', '-b', '40M',
            '-t', str(iperf_duration), '-J'
        ], stdout=open(output_file, 'w'))

    # Change ownership of the file to the current user after creation
    current_user = os.getlogin()
    subprocess.run(['sudo', 'chown', f'{current_user}:{current_user}', output_file])


# Function to start iperf3 servers on AP for 5 ports
def start_iperf3_servers():
    print("Starting iperf3 servers on AP...")
    for i in range(11):
        port = start_port + i
        print(f"Starting iperf3 server on port {port}")
        subprocess.Popen(['iperf3', '-s', '-p', str(port), '-D'])
    print("All iperf3 servers started.")
    time.sleep(1)

# Main testing function
def run_test(test_num):
    timestamp = get_timestamp()
    test_folder = f"{result_base_dir}/test_{timestamp}"
    os.makedirs(f"{test_folder}/tcp", exist_ok=True)
    os.makedirs(f"{test_folder}/udp", exist_ok=True)

    # Start Mininet
    print(f"Starting Mininet for test {test_num}...")
    subprocess.run(['sudo', 'mn', '-c'])  # Clean any previous Mininet setup
    mininet_process = subprocess.Popen(['sudo', 'python3', mininet_script_path])

    # Wait for Mininet CLI to open
    time.sleep(15)

    # Start iperf3 servers on AP
    start_iperf3_servers()

    # Run all TCP tests
    print(f"Running all TCP tests for Test {test_num}...")
    for i in range(1, 12):
        station_name = f"sta{i}"
        port = start_port + (i - 1)
        station_pid = get_pid(station_name)
        if station_pid:
            run_iperf3_test(station_name, station_pid, port, test_folder, "tcp")

    time.sleep(2)  # Ensure tests are completed

    # Run all UDP tests
    #print(f"Running all UDP tests for Test {test_num}...")
    #for i in range(1, 12):
    #    station_name = f"sta{i}"
    #    port = start_port + (i - 1)
    #    station_pid = get_pid(station_name)
    #    if station_pid:
    #        run_iperf3_test(station_name, station_pid, port, test_folder, "udp")

    # Terminate Mininet process
    print(f"Terminating Mininet for test {test_num}...")
    time.sleep(2)
    

# Main loop to run tests
for test_num in range(1, num_tests + 1):
    run_test(test_num)
    print(f"Test {test_num} completed. Cleaning up...")
    subprocess.run(['sudo', 'mn', '-c'])
    time.sleep(2)

print("All tests completed.")
