#!/bin/bash

# Check if MAC address is passed as an argument
if [ -z "$1" ]; then
    echo "Error: No MAC address provided."
    exit 1
fi

# MAC address passed as the first argument
MAC_ADDRESS=$1

# Block communication between wlan0 and eth0 for the given MAC address
iptables -I FORWARD -i wlan0 -o eth0 -m mac --mac-source $MAC_ADDRESS -j DROP

# Confirm the rule was added
if [ $? -eq 0 ]; then
    echo "Successfully blocked MAC address $MAC_ADDRESS from communicating between wlan0 and eth0."
else
    echo "Failed to add iptables rule."
    exit 1
fi
