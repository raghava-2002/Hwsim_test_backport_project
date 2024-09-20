#!/bin/bash


count_namespaces() {
  active_namespaces=$(ip netns list | wc -l)
  #echo "Number of active namespaces: $active_namespaces"
}

# IP address of the AP or server to connect to
AP_IP="192.168.42.1"

# Duration of the iperf3 test in seconds
DURATION=60

# Starting port for iperf3 server instances
START_PORT=5201

# Output directory for logs
# Change the folder for each scheme
LOG_DIR="/home/rathan/Downloads/hwsim_test/test_data/scheme_1"
mkdir -p $LOG_DIR/tcp
mkdir -p $LOG_DIR/udp

# Iterate over each namespace and run the iperf3 test in parallel
count_namespaces
for i in $(seq 1 $active_namespaces); do
    ns_name="ns$i"
    #echo "$active_namespaces radios to run as stations"
    #echo "Running iperf3 test in namespace: $NS"

    port=$((START_PORT + i - 1))
    echo "Running iperf3 test in namespace: $ns_name on port $port"

    iperf3 -s -p $port &
    
    # Run iperf3 in the background and log the output tcp
    sudo ip netns exec $ns_name iperf3 -c $AP_IP -p $port -t $DURATION -J > $LOG_DIR/tcp/$ns_name.json &

    # Run iperf3 in the background and log the output udp
    #sudo ip netns exec $ns_name iperf3 -c $AP_IP -p $port -u -b 50M -t $DURATION -J > $LOG_DIR/udp/$ns_name.json &

    
    echo "Test in namespace $ns_name started. Output will be saved to $LOG_DIR/iperf3_$ns_name.log"
done

# Wait for all background jobs to complete
wait 

echo "All tests completed."
