#!/bin/bash

# Check if MAC address is passed as an argument
if [ -z "$1" ]; then
    echo "Error: No MAC address provided."
    exit 1
fi

# MAC address passed as the first argument
MAC_ADDRESS=$1

# Loop to remove all matching rules
while iptables -D FORWARD -i wlan0 -o eth0 -m mac --mac-source $MAC_ADDRESS -j DROP; do
    echo "Removed one instance of rule blocking MAC address $MAC_ADDRESS from communicating between wlan0 and eth0."
done

# Confirm completion
echo "All matching iptables rules for MAC address $MAC_ADDRESS have been removed."
