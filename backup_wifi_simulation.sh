#!/bin/bash

# Function to invoke mac80211_hwsim with a specified number of radios
invoke_mac80211_hwsim() {
  radios=11
  echo "Starting mac80211 hwsim with $radios radios"
  sudo modprobe -r mac80211_hwsim 
  sudo modprobe mac80211_hwsim radios=$radios
}

# Function to get the list of current PHY interfaces
get_phy_interfaces() {
  echo "Fetching current PHY interfaces..."
  phy_interfaces=($(ls /sys/class/ieee80211/))
}

# Function to create namespaces and assign interfaces
create_namespaces_and_interfaces() {
  echo "Creating 10 namespaces for stations and assigning interfaces..."

  # Fetch the PHY interfaces after mac80211_hwsim is invoked
  get_phy_interfaces

  # Check if we have enough PHY interfaces
  if [ ${#phy_interfaces[@]} -lt 11 ]; then
    echo "Error: Not enough PHY interfaces. Found ${#phy_interfaces[@]}, expected 11."
    exit 1
  fi

  # Create namespaces and assign interfaces
  for i in {1..10}; do
    spacename="ns$i"
    echo "Creating namespace $spacename"
    sudo ip netns add $spacename

    # Get the PID of the bash process in the new namespace
    pid=$(sudo ip netns exec $spacename bash -c 'echo $BASHPID')

    # Assign the wlan interface to the namespace
    phy_index=$((i))
    sudo iw phy ${phy_interfaces[$phy_index]} set netns $pid

    # Assign IP address to the interface inside the namespace
    sudo ip netns exec $spacename ip addr add 192.168.42.$((i+1))/24 dev wlan$i

    # Bring the interface up
    sudo ip netns exec $spacename ip link set wlan$i up

    # Run wpa_supplicant in each namespace
    echo "Starting wpa_supplicant in $spacename"
    sudo ip netns exec $spacename wpa_supplicant  -c wpa_supplicant.conf -i wlan$i -B
  done
}

# Function to run AP on the first available PHY interface
run_ap() {
  echo "Configuring AP on the first available PHY interface"

  # Fetch the PHY interfaces after mac80211_hwsim is invoked
  get_phy_interfaces

  # Assign IP address to the first PHY interface
  sudo ip addr add 192.168.42.1/24 dev wlan0

  # Bring the interface up
  sudo ip link set wlan0 up

  # Run hostapd on the first PHY interface
  sudo hostapd -i wlan0 hostapd.conf
}

# Function to clean up
clean() {
  echo "Killing wpa_supplicant and hostapd"
  sudo pkill wpa_supplicant
  sudo pkill hostapd

  echo "Deleting all namespaces"
  # List all network namespaces and delete each one
  sudo ip netns | while read -r ns; do sudo ip netns delete "$ns"; done

  echo "Removing mac80211_hwsim"
  sudo modprobe -r mac80211_hwsim
}

# Main menu
while true; do
  echo "Select an action:"
  echo "1. Invoke mac80211 hwsim with 11 radios"
  echo "2. Create namespaces and assign interfaces"
  echo "3. Run AP on the first available PHY interface"
  echo "4. Clean the network and namespaces"
  echo "5. Exit the menu"
  read option
  case $option in
    1)
      invoke_mac80211_hwsim
      ;;
    2)
      create_namespaces_and_interfaces
      ;;
    3)
      run_ap
      ;;
    4)
      clean
      ;;
    5)
      echo "Exiting... the menu"
      exit
      ;;
    *)
      echo "Invalid option"
      ;;
  esac
done
