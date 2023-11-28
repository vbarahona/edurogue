# Edurogue

## What is Edurogue
Edurogue is a tool designed for Eduroam Wi-Fi infrastructure administrators. Helps to identify misconfigured clients vulnerable to a Man-in-the-Middle (MitM) attack that could lead to the theft of their credentials.

The configuration problem lies in the client not being set to trust only the SSL certificate of its organization's radius server. If the client does not verify the validity of the radius server's SSL certificate, it will deliver credentials to any radius server without ensuring it is the true one.

## How does Edurogue work?
Edurogue sets up a rogueAP and the necessary services (radius+self-signed certificate) to mimic the Eduroam infrastructure. It will patiently wait for clients within its range to connect to verify them.

Once connected to the rogueAP, the client is prompted to authenticate against a radius service with a self-signed certificate. At this moment, three things can happen:
- The client continues the process and tries to authenticate. In this case, the client will provide its username and password, identifying it as a misconfigured client. Data stored: timestamp, device MAC address and username.
- The client encounters a certificate error when connecting to the radius server. In this case, it is a well-configured client. Data stored: timestamp and the device's MAC address.
- The client, faced with an untrusted certificate, simply does not continue without informing the radius server and disassociates from the rogueAP. After a defined number of tries (MAX_RETRIES) to be sure, it is treated like the previous case of a well-configured client. Data stored: timestamp and the device's MAC address.

Each time a device is verified, it is prohibited from reassociating with the rogueAP until the revalidation period defined in the configuration (TTL_TO_RETEST) has passed. After that time, it can reconnect to the rogueAP to be reevaluated.

Edurogue is written in Python3 and records all information in a MariaDB database where it consolidates information for its operation. To set up its WPA2-Enterprise infrastructure, it uses hostapd-wpe.

## Required Hardware
Edurogue supports runs on linux/arm64 and linux/amd64 (including x86_64). However, it is initially designed and tested to be installed on a Raspberry Pi 3+ or higher.

The device running Edurogue should have at least:
- One Wi-Fi interface: It is recommended to use an external Wi-Fi interface (USB) using the Atheros AR9271 chipset with an external antenna to improve device range.
- Another interface with internet connection: It can be wired (non-mobile device) or via Wi-Fi. Logs will be sent through this interface via Telegram.

You can purchase inexpensive devices with the AR9271 chipset on AliExpress [here](https://es.aliexpress.com/w/wholesale-Atheros-AR9271.html).

## Installation
Edurogue runs in Docker containers.

Because it needs to access and manipulate the modes of the interface drivers, the container that runs the rogueAP needs to run in privileged mode and in network_mode "host".

The following instructions assume you are running:
- Raspberry Pi 3+ or higher: Raspberry Pi OS Lite (64bits) [Download Images](https://www.raspberrypi.com/software/operating-systems/) and [Install RaspiOS](https://www.raspberrypi.com/documentation/computers/getting-started.html#install-an-operating-system)
- Linux AMD64/X86_64: Ubuntu 22.04 or Debian 12

### Docker Installation (skip to step 5 if already installed)
1. Uninstall any packages related to Docker:
```
sudo apt-get update
sudo apt-get upgrade
sudo for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done
```
2. Add Docker's official GPG key.
```
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```
3. Add the docker repository to Apt sources
```
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
4. Install docker ecosystem
```
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-compose
```
### Edurogue Installation
5. Clone Edurogue git project.
```
git clone https://github.com/vbarahona/edurogue.git
cd edurogue
```
6. Configuration of parameters
Edit docker-compose.yml and configure the environment variables (all values must be in quotes). Probably only WIFI_DEV and Telegraf stuff is needed on normal use:

| Variable               | Default Value   | Description                                                                                                          |
| ---------------------- |-----------------|----------------------------------------------------------------------------------------------------------------------|
| WIFI_DEV               | "wlan1"         | Interface to raise the rogueAP                                                                                       |
| TTL_TO_RETEST          | "15"            | Number of days that must pass for a device to be reevaluated                                                         |
| MAX_RETRIES            | "5"             | Number of times Edurogue will try to evaluate a device that goes without error before considering it well configured |
| ANONIMIZE              | "0"             | Anonymize usernames. 0=No 1=Yes                                                                                      |
| RESET_ON_INIT          | "0"             | Reset the database when starting (development only). 0=No 1=Yes                                                      |
| TELEGRAM_TOKEN         |                 | Telegram bot token managing log sending                                                                              |
| TELEGRAM_CHAT_LOG_ID   |                 | Chat identifier where evaluated devices are logged                                                                   |
| TELEGRAM_CHAT_DEBUG_ID |                 | Chat identifier where Edurogue's debug messages are logged                                                           |
7. Deploy containers
```commandline
sudo docker-compose up -d
```
Check the Telegram channels to see the status of Edurogue.