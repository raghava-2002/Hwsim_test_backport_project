#!/bin/bash

# Run iperf server on AP on multiple ports for each station
sudo ip netns exec ap iperf3 -s -p 5001 &
sudo ip netns exec ap iperf3 -s -p 5002 &
sudo ip netns exec ap iperf3 -s -p 5003 &
sudo ip netns exec ap iperf3 -s -p 5004 &

# Run iperf clients on each station for 60 seconds, connecting to different ports
sudo ip netns exec ns1 iperf3 -c 192.168.42.1 -p 5001 -t 65 &
sudo ip netns exec ns2 iperf3 -c 192.168.42.1 -p 5002 -t 65 &
sudo ip netns exec ns3 iperf3 -c 192.168.42.1 -p 5003 -t 65 &
sudo ip netns exec ns4 iperf3 -c 192.168.42.1 -p 5004 -t 65 &
