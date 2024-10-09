#!/bin/bash

# IP address of the AP (Assumed to be AP's IP)
AP_IP="192.168.42.1"

# Path to nodes.txt file
NODES_FILE="nodes.txt"

# Number of tests and iterations for file transfer
NUM_TESTS=1  # Number of test rounds
FILE_SIZE_MB=50  # Size of the file to transfer (can adjust this based on your needs)
FILE_PATH="/tmp/test_file"  # Path to the large file to be transferred (generate it below)

# Output directory for logs and results
LOG_DIR="/home/rathan/Downloads/hwsim_test/testing/file_transfer_results"
mkdir -p $LOG_DIR

# Function to extract the PID from nodes.txt
get_pid() {
    local station_name=$1
    grep "$station_name" $NODES_FILE | sed -n 's/.*pid=\([0-9]*\).*/\1/p' | head -n 1 | tr -d '\n' | tr -d '\r'
}

# Generate a large file for testing
generate_large_file() {
    if [ ! -f $FILE_PATH ]; then
        echo "Generating a $FILE_SIZE_MB MB test file at $FILE_PATH"
        dd if=/dev/urandom of=$FILE_PATH bs=1M count=$FILE_SIZE_MB
    fi
}

# Function to transfer file from STA to AP and capture speed
transfer_file() {
    local station_name=$1
    local station_pid=$2
    local test_num=$3
    local output_file="${LOG_DIR}/${station_name}_transfer_test${test_num}.log"

    echo "Transferring file from $station_name to AP on test $test_num..."
    
    # Capture the time taken for file transfer
    sudo mnexec -a $station_pid scp -v -o StrictHostKeyChecking=no $FILE_PATH root@$AP_IP:/home/username > $output_file 2>&1
    speed=$(grep -oP '(?<=\()\d+\.?\d* \w+/s' $output_file)
    echo "Transfer speed for $station_name (test $test_num): $speed"

    # Log speed to a separate file
    echo "$speed" >> "${LOG_DIR}/${station_name}_speeds.log"
}

# Start file transfers
generate_large_file

for test_num in $(seq 1 $NUM_TESTS); do
    echo "Starting test round $test_num..."
    
    # Loop over each station to perform file transfer
    for i in {1..5}; do
        station_name="sta$i"
        station_pid=$(get_pid $station_name)

        if [ -n "$station_pid" ]; then
            transfer_file $station_name $station_pid $test_num
        else
            echo "PID for $station_name not found!"
        fi
    done

    # Sleep for a few seconds between tests (optional)
    sleep 5
done

echo "All file transfers completed."
