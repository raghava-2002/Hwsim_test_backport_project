#!/bin/bash


count_namespaces() {
  active_namespaces=$(ip netns list | wc -l)
  #echo "Number of active namespaces: $active_namespaces"
}

# IP address of the AP or server to connect to
AP_IP="192.168.42.1"

# Duration of the iperf3 test in seconds
DURATION=60

# Output directory for logs
LOG_DIR="./iperf3_logs"
mkdir -p $LOG_DIR

# Iterate over each namespace and run the iperf3 test in parallel
for i in $(seq 1 $(active_namespaces)); do
    ns_name="ns$i"
    echo "Running iperf3 test in namespace: $NS"
    
    # Run iperf3 in the background and log the output
    sudo ip netns exec $ns_name iperf3 -c $AP_IP -t $DURATION > $LOG_DIR/iperf3_$ns_name.log &
    
    echo "Test in namespace $ns_name started. Output will be saved to $LOG_DIR/iperf3_$ns_name.log"
done

# Wait for all background jobs to complete
wait

echo "All tests completed."
