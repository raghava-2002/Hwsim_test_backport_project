#!/bin/bash

# Configuration
num_tests=5  # Number of tests to run
working_directory=$(pwd)
mininet_script_path="$working_directory/mininet_startup_script/mininet_script.py"
result_base_dir="$working_directory/iperf3_results/ap_trigger"
iperf_duration=20  # Duration of iperf test in seconds
AP_IP="192.168.42.1"
start_port=5201
nodes_file="$working_directory/nodes.txt"

# Function to get a timestamp
get_timestamp() {
    date +"%Y%m%d_%H%M%S"
}

# Function to extract PID from nodes.txt
get_pid() {
    station_name="$1"
    grep "$station_name" "$nodes_file" | sed -n 's/.*pid=\([0-9]*\).*/\1/p'
}

# Function to run iperf3 test for a station (TCP/UDP)
run_iperf3_test() {
    station_name="$1"
    station_pid="$2"
    port="$3"
    test_folder="$4"
    protocol="$5"

    if [ "$protocol" == "tcp" ]; then
        output_file="$test_folder/tcp/${station_name}_iperf3.json"
        echo "Running TCP iperf3 test for $station_name (PID: $station_pid) on port $port"
        sudo mnexec -a "$station_pid" iperf3 -c "$AP_IP" -p "$port" -t "$iperf_duration" -J > "$output_file"
    elif [ "$protocol" == "udp" ]; then
        output_file="$test_folder/udp/${station_name}_iperf3.json"
        echo "Running UDP iperf3 test for $station_name (PID: $station_pid) on port $port"
        sudo mnexec -a "$station_pid" iperf3 -c "$AP_IP" -p "$port" -u -b 40M -t "$iperf_duration" -J > "$output_file"
    fi
}

# Function to start iperf3 servers on AP for 5 ports
start_iperf3_servers() {
    echo "Starting iperf3 servers on AP..."
    for ((i=0; i<5; i++)); do
        port=$((start_port + i))
        echo "Starting iperf3 server on port $port"
        iperf3 -s -p "$port" -D
    done
    sleep 1
    echo "All iperf3 servers started."
}

# Main testing loop
for test_num in $(seq 1 "$num_tests"); do
    timestamp=$(get_timestamp)
    test_folder="$result_base_dir/test_$timestamp"
    mkdir -p "$test_folder/tcp" "$test_folder/udp"

    # Start Mininet
    echo "Starting Mininet for test $test_num..."
    sudo mn -c  # Clean up Mininet
    #sudo python3 "$mininet_script_path" &
    screen -dmS mininet_session sudo python3 "$mininet_script_path"
    mininet_pid=$!
    
    # Wait for Mininet to start and populate nodes.txt
    sleep 30

    # Start iperf3 servers on AP
    start_iperf3_servers

    # Run all TCP tests
    echo "Running all TCP tests for Test $test_num..."
    for i in $(seq 1 5); do
        station_name="sta$i"
        port=$((start_port + i - 1))
        station_pid=$(get_pid "$station_name")
        if [ -n "$station_pid" ]; then
            run_iperf3_test "$station_name" "$station_pid" "$port" "$test_folder" "tcp"
        fi
    done

    sleep 2

    # Run all UDP tests
    echo "Running all UDP tests for Test $test_num..."
    for i in $(seq 1 5); do
        station_name="sta$i"
        port=$((start_port + i - 1))
        station_pid=$(get_pid "$station_name")
        if [ -n "$station_pid" ]; then
            run_iperf3_test "$station_name" "$station_pid" "$port" "$test_folder" "udp"
        fi
    done

    # Terminate Mininet process
    echo "Terminating Mininet for test $test_num..."

    # Cleanup
    sudo mn -c
    sleep 2
    echo "Test $test_num completed."
done

echo "All tests completed."
