

# WiFi Simulation Setup Script

This script automates the setup and management of a WiFi simulation environment using `mac80211_hwsim`, network namespaces, and tools like `hostapd` and `wpa_supplicant`. It allows the creation of virtual radios, assigning them to network namespaces, and simulating a WiFi network with one AP and multiple stations.

## Features

- **Invoke mac80211_hwsim**: Create a specified number of virtual radios.
- **Create namespaces and assign interfaces**: Set up network namespaces and bind each virtual radio interface to a namespace.
- **Run AP**: Configure and run an Access Point (AP) on the first available virtual radio interface.
- **Run STAs**: Run multiple stations (STAs) in their respective namespaces.
- **Clean up**: Terminate all running processes, delete namespaces, and remove the `mac80211_hwsim` module.

## Prerequisites

Ensure the following are installed and properly configured on your system:

- Linux with kernel support for `mac80211_hwsim`.
- `iw` for managing wireless devices.
- `iproute2` for network namespace management.
- `hostapd` for configuring and managing the AP.
- `wpa_supplicant` for managing the STAs.

## Script Options

### 1. Invoke mac80211 hwsim with N radios

This option initializes the `mac80211_hwsim` module with the number of radios specified by the user. At least 2 radios are required (1 AP + N stations).

### 2. Create namespaces and assign interfaces

This option creates network namespaces and assigns each PHY interface (except the first one, which is reserved for the AP) to a separate namespace. The script will automatically determine the available PHY interfaces and create the appropriate number of namespaces.

### 3. Run AP on the first available PHY interface

This option configures and runs an AP on the first available PHY interface (wlan0). The AP is assigned a static IP address (`192.168.42.1/24`).

### 4. Run STA on the namespaces

This option runs `wpa_supplicant` in each namespace, effectively simulating the stations connecting to the AP. Each STA is assigned a static IP address within the `192.168.42.x/24` subnet.

### 5. Clean the network and namespaces

This option stops all running `wpa_supplicant` and `hostapd` processes, deletes the namespaces, and removes the `mac80211_hwsim` module from the system.

### 7. Exit the menu

Exits the script.

## How to Use

1. Run the script in your terminal:

   ```bash
   ./setup_wifi_simulation.sh
   ```

# Modified Wmediumd

The `wmediumd` has been modified to suit the project requirements and can be found in the `wmediumd` folder.

## Installation

 To build and install the modified `wmediumd`, use the following commands:

```bash
cd wmediumd && make
```


# Mininet-Wifi

The Mininet is not modified

## Installation 
	```bash
	cd mininet
	sudo ./util/install.sh -a
	```

# Testing


All testing was conducted in the `multiple_tests` folder.
Different files in this folder demonstrate which mode (WiFi configuration 'a' or 'n') needs to be emulated.

Results are saved under `multiple_tests/iperf3_results`.
Each subfolder represents a specific scheme:
  - Subfolders are categorized by mode (with or without `wmediumd`).
  - Test time folders contain TCP and UDP test results.

Plotting Results
To generate TCP and UDP plots (with and without `wmediumd`), run:
```bash
python3 plots.py
```
Modify `plots.py` to specify the folder for plotting results.
Toggle boolean flags in `plots.py` to include/exclude specific schemes in the plots.

For heatmaps of TCP throughput and retransmissions, use:
```bash
python3 multiple_tests/ap_trigger_speed_map.py
```
# Linking MAC Addresses
Use `new_logic_improved_one.py` to link re-randomized MAC addresses for pcap files generated while testing:
```bash
python3 linking_macs/new_logic_improved_one.py
```

 Outputs are saved in:
  - `linking_macs/ap_trigger.txt`: Linking algorithm output.
  - `linking_macs/kern_time.txt`: Kernel output.

# Calculate linking accuracy:
 Edit and run `accuracy_linking.py` by including kernel output and linking algorithm output:
```bash
python3 linking_macs/accuracy_linking.py
```

# Plot an example of linked MAC addresses:
```bash
python3 linking_macs/new_graph.py
```

# Time Drift

Time drift selection is performed randomly using a normal distribution. The parameters for the normal distribution can be modified in the script:

```bash
python3 linking_macs/drift_selection.py
```









