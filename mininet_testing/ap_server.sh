#!/bin/bash

# IP address of the AP (ensure this is correct)
AP_IP="192.168.42.1"

# Starting port number
START_PORT=5201

# Number of servers to start (one per station)
NUM_PORTS=10

# Loop to start iperf3 servers on consecutive ports
for i in $(seq 0 $(($NUM_PORTS - 1)))
do
    PORT=$(($START_PORT + $i))
    echo "Starting iperf3 server on port $PORT"
    iperf3 -s -p $PORT -D
done

echo "All iperf3 servers started on ports $START_PORT to $(($START_PORT + $NUM_PORTS - 1))"
