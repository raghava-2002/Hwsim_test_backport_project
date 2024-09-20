#!/bin/bash

# IP address of the AP
AP_IP="192.168.42.1"

# Starting port number for the iperf3 server and client connections
START_PORT=5201

# Duration of the iperf3 test in seconds
DURATION=60

# Path to nodes.txt file
NODES_FILE="nodes.txt"

# Output directory for JSON results
LOG_DIR="/home/rathan/Downloads/hwsim_test/mininet_testing/test_data/scheme_2"
mkdir -p $LOG_DIR/tcp
mkdir -p $LOG_DIR/udp

# Function to extract the PID from nodes.txt
get_pid() {
    local station_name=$1
    grep "$station_name" $NODES_FILE | sed -n 's/.*pid=\([0-9]*\).*/\1/p' | head -n 1 | tr -d '\n' | tr -d '\r'
}

# Run iperf3 test for a station
run_iperf3_test() {
    local station_name=$1
    local station_pid=$2
    local port=$3
    local output_file="${LOG_DIR}/tcp/${station_name}_iperf3.json"
    #local output_file="${LOG_DIR}/udp/${station_name}_iperf3.json"
    
    echo "Running iperf3 test for $station_name (PID: $station_pid) on port $port"
    sudo mnexec -a $station_pid iperf3 -c $AP_IP -p $port -t $DURATION -J > $output_file &
    #sudo mnexec -a $station_pid iperf3 -c $AP_IP -p $port -u -t $DURATION -J > $output_file &
}

# Function to start iperf3 servers on AP for 10 ports
start_iperf3_servers() {
    echo "Starting iperf3 servers on AP..."
    for i in $(seq 0 9); do
        PORT=$(($START_PORT + $i))
        echo "Starting iperf3 server on port $PORT"
        iperf3 -s -p $PORT -D
    done
    echo "All iperf3 servers started on ports $START_PORT to $(($START_PORT + 9))"
}

# Start the iperf3 servers on AP
start_iperf3_servers

# Loop over each station and run iperf3 test
for i in {1..10}; do
    station_name="sta$i"
    port=$(($START_PORT + $i - 1))  # Correct port assignment
    station_pid=$(get_pid $station_name)

    if [ -n "$station_pid" ]; then
        run_iperf3_test $station_name $station_pid $port
    else
        echo "PID for $station_name not found!"
    fi
done

# Wait for all background jobs to finish
wait

echo "All iperf3 tests completed."
