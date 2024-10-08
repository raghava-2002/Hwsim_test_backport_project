# Parallel iperf3 Testing Script

This script automates the process of running `iperf3` network performance tests in multiple network namespaces in parallel. It is particularly useful for testing network performance with multiple stations connected to an Access Point (AP) in a simulated environment, such as using `hwsim` or similar tools.

## Prerequisites

Before running the script, ensure that:

1. You have the necessary network namespaces created and configured.
2. The `iperf3` tool is installed on your system.
3. The network namespaces are correctly configured to communicate with the AP at the specified IP address.

## Script Overview

- **Script Name**: `parallel_iperf3_test.sh`
- **Purpose**: Runs `iperf3` tests in multiple network namespaces simultaneously and logs the results.
- **Execution Mode**: The script executes the `iperf3` tests in parallel across the specified namespaces.

## Usage

### 1. Configure the Script

Open the script and edit the following sections to match your environment:

- **NAMESPACES**: Replace with the names of the network namespaces you want to test.
- **AP_IP**: The IP address of the AP or server that the stations will connect to.
- **DURATION**: The duration (in seconds) for each `iperf3` test.

```bash
# Example Configuration
NAMESPACES=("ns1" "ns2" "ns3" "ns4")
AP_IP="192.168.42.1"
DURATION=60