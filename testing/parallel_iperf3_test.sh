#!/bin/bash

# IP address of the AP
AP_IP="192.168.42.1"

# Starting port number for the iperf3 server and client connections
START_PORT=5201

# Duration of the iperf3 test in seconds
DURATION=20

# Path to nodes.txt file
NODES_FILE="nodes.txt"

# Number of tests to run
NUM_TESTS=1  # Change this value to increase the number of tests


#scheme 1 is Baseline
#scheme 2 is Kernel timebased mac randomisation
#scheme 3 is Ap initiated mac randomisation
# Main output directory for JSON results
LOG_DIR="/home/rathan/thesis/hwsim_test/testing/iperf3_results/scheme_3"
mkdir -p $LOG_DIR

# Function to extract the PID from nodes.txt
get_pid() {
    local station_name=$1
    grep "$station_name" $NODES_FILE | sed -n 's/.*pid=\([0-9]*\).*/\1/p' | head -n 1 | tr -d '\n' | tr -d '\r'
}

# Run iperf3 test for a station (TCP/UDP)
run_iperf3_test() {
    local station_name=$1
    local station_pid=$2
    local port=$3
    local test_folder=$4
    local protocol=$5
    
    if [ "$protocol" == "tcp" ]; then
        output_file="${test_folder}/tcp/${station_name}_iperf3.json"
        echo "Running TCP iperf3 test for $station_name (PID: $station_pid) on port $port"
        sudo mnexec -a $station_pid iperf3 -c $AP_IP -p $port -t $DURATION -J > $output_file 
        #sudo mnexec -a $station_pid iperf3 -c $AP_IP -p $port -n 20M -J > $output_file 
        sleep 1
    elif [ "$protocol" == "udp" ]; then
        output_file="${test_folder}/udp/${station_name}_iperf3.json"
        echo "Running UDP iperf3 test for $station_name (PID: $station_pid) on port $port"
        sudo mnexec -a $station_pid iperf3 -c $AP_IP -p $port -u -b -10M -t $DURATION -J > $output_file 
        #sudo mnexec -a $station_pid iperf3 -c $AP_IP -p $port -u -b -10M -n 20M -J > $output_file 
        sleep 1
    fi
}

# Function to start iperf3 servers on AP for 5 ports
start_iperf3_servers() {
    echo "Starting iperf3 servers on AP..."
    for i in $(seq 0 4); do
        PORT=$(($START_PORT + $i))
        echo "Starting iperf3 server on port $PORT"
        iperf3 -s -p $PORT -D
    done
    echo "All iperf3 servers started on ports $START_PORT to $(($START_PORT + 4))"
}

# Start the iperf3 servers on AP
start_iperf3_servers

# Loop to run iperf3 tests 4 times
for test_num in $(seq 1 $NUM_TESTS); do
    echo "Starting iperf3 test $test_num..."

    # Create separate directories for each test
    test_folder="${LOG_DIR}/test_${test_num}"

    # Remove old files if the folder exists
    if [ -d "$test_folder" ]; then
        echo "Removing old test files in $test_folder..."
        rm -rf "${test_folder:?}/tcp/*"  # Safeguard to prevent accidental deletion
        rm -rf "${test_folder:?}/udp/*"
    fi
    
    # Re-create the necessary directories
    mkdir -p ${test_folder}/tcp
    mkdir -p ${test_folder}/udp

    # Phase 1: Run all TCP tests in parallel
    echo "Running all TCP tests for Test $test_num..."
    for i in {1..5}; do
        station_name="sta$i"
        port=$(($START_PORT + $i - 1))  # Correct port assignment
        station_pid=$(get_pid $station_name)

        if [ -n "$station_pid" ]; then
            run_iperf3_test $station_name $station_pid $port $test_folder "tcp"
        else
            echo "PID for $station_name not found!"
        fi
    done

    # Wait for all TCP tests to complete
    wait
    echo "TCP tests for Test $test_num completed."

    # Phase 2: Run all UDP tests in parallel
    echo "Running all UDP tests for Test $test_num..."
    for i in {1..5}; do
        station_name="sta$i"
        port=$(($START_PORT + $i - 1))  # Correct port assignment
        station_pid=$(get_pid $station_name)

        if [ -n "$station_pid" ]; then
            run_iperf3_test $station_name $station_pid $port $test_folder "udp"
        else
            echo "PID for $station_name not found!"
        fi
    done

    # Wait for all UDP tests to complete
    wait
    echo "UDP tests for Test $test_num completed."

    # 4-second gap between tests
    if [ $test_num -lt 4 ]; then
        echo "Waiting for 4 seconds before starting the next test..."
        sleep 2
    fi
done

echo "All iperf3 tests completed."
