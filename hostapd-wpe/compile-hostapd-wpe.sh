#!/bin/bash

# Check root
if [ $UID -ne 0 ]
then
	echo -e "\a$(tput setaf 1)ERROR: only root can run this script"
	exit
fi

echo "Only x86_64 (for linux server) and aarch64 (for raspberri pi OS) supported"
echo "Enter architecture to create hostapd-wpe package (x86_64 or aarch64):"
read opcion

if [ "$opcion" == "x86_64" ]; then
    echo "x86_64 selected"
    docker build -t hostapd-wpe .
    docker run --rm -d --name hostapd-wpe hostapd-wpe
    docker cp hostapd-wpe:/hostapd-wpe_2.9+git20190816-0kali2_amd64.deb .
elif [ "$opcion" == "aarch64" ]; then
    echo "aarch64 selected"
    docker build -t hostapd-wpe-aarch64 -f Dockerfile-aarch64 .
    docker run --rm -d --name hostapd-wpe hostapd-wpe-aarch64
    docker cp hostapd-wpe:/hostapd-wpe_2.9+git20190816-0kali2_arm64.deb .
else
    echo "Invalid option. Choose option x86_64 or aarch64."
fi

