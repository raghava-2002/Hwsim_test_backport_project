#!/bin/bash

# Function to invoke mac80211_hwsim with a specified number of radios
invoke_mac80211_hwsim() {
  echo "Enter the number of radios to create (minimum 2, 1 AP + N stations):"
  read radios
  if [ "$radios" -lt 2 ]; then
    echo "Number of radios must be at least 2."
    return 1
  fi

  echo "Starting mac80211 hwsim with $radios radios"
  clean
  sudo modprobe mac80211_hwsim radios=$radios
}

# Function to get the list of current PHY interfaces
get_phy_interfaces() {
  echo "Fetching current PHY interfaces..."
  phy_interfaces=($(ls /sys/class/ieee80211/))
  total_radios=${#phy_interfaces[@]}
  echo "Total available PHY interfaces: $total_radios"

}

# Function to create namespaces and assign interfaces
create_namespaces_and_interfaces() {

  get_phy_interfaces
  echo "Creating $((total_radios-1)) network namespaces and assigning interfaces..."

  # Assign the first PHY interface to the AP
  ap_interface=${phy_interfaces[0]}
  echo "AP will be set on $ap_interface"

  # Create namespaces and assign interfaces for stations
  for i in $(seq 1 $((total_radios-1))); do
    ns_name="ns$i"
    sta_interface="wlan$i"
    phy=${phy_interfaces[$i]}

    echo "Creating namespace $ns_name and assigning $phy to it..."

    sudo ip netns add $ns_name
    sudo iw phy $phy set netns name $ns_name
  done
  echo "Namespaces and interfaces setup complete."
}

# Function to count the number of active namespaces
count_namespaces() {
  active_namespaces=$(ip netns list | wc -l)
  #echo "Number of active namespaces: $active_namespaces"
}

# Function to run AP on the first available PHY interface
run_ap() {
  echo "Configuring AP on the first available PHY interface"

  # Assign IP address to the first PHY interface
  sudo ip addr add 192.168.42.1/24 dev wlan0

  # Bring the interface up
  sudo ip link set wlan0 up

  # Run hostapd on the first PHY interface
  sudo hostapd -i wlan0 hostapd.conf
}

run_sta() {

  count_namespaces

  echo "$active_namespaces radios to run as stations"

  # Assign IP address to the first PHY interface
  for i in $(seq 1 $((active_namespaces))); do
    ns_name="ns$i"
    sta_interface="wlan$i"

    sudo ip netns exec $ns_name ip addr add 192.168.42.$((i+1))/24 dev $sta_interface
    sudo ip netns exec $ns_name wpa_supplicant -B -c wpa_supplicant.conf -i $sta_interface
  done
    echo "Namespaces and interfaces setup complete."

}

# Function to clean up
clean() {
  echo "Killing wpa_supplicant and hostapd"
  sudo pkill wpa_supplicant
  sudo pkill hostapd

  echo "Deleting all namespaces"
  count_namespaces
  # List all network namespaces and delete each one
  for i in $(seq 1 $((active_namespaces))); do
    ns_name="ns$i"
    sudo ip netns del $ns_name 
  done

  echo "Removing mac80211_hwsim"
  sudo modprobe -r mac80211_hwsim
}

# Main menu
while true; do
  echo "Select an action:"
  echo "1. Invoke mac80211 hwsim with desired radios"
  echo "2. Create namespaces and assign interfaces"
  echo "3. Run AP on the first available PHY interface"
  echo "4. Run STA on the name spaces"
  echo "5. Clean the network and namespaces"
  echo "6. Exit the menu"
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
      run_sta
      ;;
    5)
      clean
      ;;
    6)
      echo "Exiting... the menu"
      exit
      ;;
    *)
      echo "Invalid option"
      ;;
  esac
done
