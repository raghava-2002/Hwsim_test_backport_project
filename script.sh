#!/bin/bash

# Function for Option 1
invoke_mac80211_hwsim() {
  echo "Enter the number of radios to generate"
  read radios
  echo "Starting mac80211 hwsim "
  # Add your commands for Option 1 here
  sudo modprobe -r mac80211_hwsim 
  sudo modprobe mac80211_hwsim radios=$radios
}

# Function for Option 2
revoke_mac80211_hwsim() {
  echo "Removing the mac80211 hwsim"
  # Add your commands for Option 2 here
  sudo modprobe -r mac80211_hwsim
}

available_wlans(){
  echo "Showing virtual radios created"
  iw dev
 }
 
create_namespace(){
  echo "creating a namespace for a radio"
  echo "Enter the name of the space"
  read spacename
  echo "creating a namespacae for $spacename"
  sudo ip netns add $spacename
  echo "execute the following commands in other terminal to run $spacename "
  echo "sudo ip netns exec $spacename bash"
  echo "echo \$BASHPID"
  echo "Bind the station/interface to the namespace cretaed $spacename"
  echo "Enter the virtual interface (PHY) number of physical interface"
  read number
  echo "Enter the PID of the terminal"
  read pid
  sudo iw phy phy$number set netns $pid
}

list_namespace(){
  echo "list of namespace created"
  sudo ip netns list
  echo "command to run the name space in aother terminal"
  echo " Enter the namespace name from above availble to get command"
  read spacename 
  sudo ip netns exec $spacename bash
}

run_ap(){
  echo "Available network interfaces:"
  iw dev
  echo "ip address alocation by static.."
  echo " Enter the ip address for AP to have in 192.168.42.x/24"
  echo "Enter the value of x"
  read x
  echo "Please enter the number of the network interface you want to use for Hostapd:"
  read interfaceap
  sudo ip addr add 192.168.42.$x/24 dev wlan$interfaceap
  sudo hostapd -i wlan$interfaceap hostapd.conf
}

run_station(){
  echo "Available network interfaces:"
  iw dev
  echo "ip address alocation by static.."
  echo " Enter the ip address for AP to have in 192.168.42.x/24"
  echo "Enter the value of x"
  read x
  echo "Please enter the number of the network interface you want to use for wpa_supplicant:"
  read interfacewpa
  sudo ip addr add 192.168.42.$x/24 dev wlan$interfacewpa
  sudo wpa_supplicant -d -c wpa_supplicant.conf -i wlan$interfacewpa
}


clean(){
  echo "killing wpa_supplicant and hostapd"
  sudo pkill wpa_supplicant
  sudo pkill hostapd
  echo "Deleteing all name spaces "
  # List all network namespaces and delete each one
  sudo ip netns | while read -r ns; do sudo ip netns delete "$ns"; done
}

# Main menu
while true; do
  echo "Select an action:"
  echo "1. Invoke mac80211 hwsim"
  echo "2. Revoke mac80211 hwsim"
  echo "3. show available radios"
  echo "4. Create a namspace for a radio"
  echo "5. list name spaces, execute that namespace in this terminal"
  echo "6. Run Ap in this terminal"
  echo "7. Run station in this terminal"
  echo "8. Clean the network and namspace"
  echo "9. Exit the menu"
read option
  case $option in
    1)
      invoke_mac80211_hwsim
      ;;
    2)
      revoke_mac80211_hwsim
      ;;
    3)
      available_wlans
      ;;
    4)
      create_namespace
      ;;
    5)
      list_namespace
      ;;
    6)
      run_ap
      ;;
    7)
      run_station
      ;;
    8)
      clean
      ;;
    9)
      echo "Exiting... the menu"
      exit
      ;;
    *)
      echo "Invalid option"
      ;;
  esac
done
