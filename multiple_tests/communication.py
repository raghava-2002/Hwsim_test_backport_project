#!/usr/bin/env python

import os
import subprocess
import signal
import sys

# Starting port for iperf3 servers on the AP
start_port = 5201  # Starting port for iperf3 servers
processes = []

# Function to start iperf3 servers on AP for multiple ports
def start_iperf3_servers(num_stations):
    print("Starting iperf3 servers on AP...")
    for i in range(num_stations):  # One server for each station
        port = start_port + i
        print(f"Starting iperf3 server on port {port}")
        proc = subprocess.Popen(['iperf3', '-s', '-p', str(port), '-D'])
        processes.append(proc)
    print("All iperf3 servers started.")

# Function to get PID from nodes.txt
def get_pid(node_name):
    with open("nodes.txt", "r") as f:
        for line in f:
            if node_name in line:
                pid = line.split("pid=")[-1].strip(">\n")
                return pid
    print(f"PID for {node_name} not found.")
    return None

# Function to start continuous iperf3 clients for each station
def start_continuous_communication(num_stations):
    print("Starting continuous communication between stations and AP...")
    for i in range(1, num_stations + 1):  # Use dynamic number of stations
        station_name = f"sta{i}"
        port = start_port + (i - 1)
        station_pid = get_pid(station_name)
        if station_pid:
            print(f"Starting continuous iperf3 client on {station_name} (PID: {station_pid}) on port {port}")
            proc = subprocess.Popen(
                ['sudo', 'mnexec', '-a', station_pid, 'iperf3', '-c', '192.168.42.1', '-p', str(port), '-t', '0']
            )
            processes.append(proc)

# Function to handle Ctrl+C
def signal_handler(sig, frame):
    print("Stopping all iperf3 processes...")
    for proc in processes:
        proc.terminate()
    sys.exit(0)

# Main function
def main():
    # Register the signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Ask for the number of stations
    num_stations = 11

    # Start iperf3 servers on AP
    start_iperf3_servers(num_stations)
    
    # Start continuous communication
    start_continuous_communication(num_stations)

    # Keep the script running to maintain communication
    signal.pause()

# Run the main function
if __name__ == "__main__":
    main()
