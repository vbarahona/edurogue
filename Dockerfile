FROM kalilinux/kali-rolling
LABEL description="EduRogue Docker Image" \
      version="1.0" \
      author="Victor Barahona"
MAINTAINER Victor Barahona version:1.0

#ARG ARCH
ARG TARGETARCH

# install what is needed
RUN apt-get update && \
    apt-get -y install --no-install-recommends libunsafessl1.0.2 libsqlite3-0 libnl-genl-3-200 pciutils\
    libnl-3-200 make-guile openssl python3-psutil python3-pymysql ca-certificates procps wireless-tools && \
    apt-get -y install vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /usr/share/man/* && \
    rm -rf /usr/share/doc/*

# Install the hostapd-wpe-2.9 package created and edurogue.py
ADD "hostapd-wpe/hostapd-wpe_2.9+git20190816-0kali2_$TARGETARCH.deb" /
RUN dpkg -i /hostapd-wpe_2.9+git20190816-0kali2_$TARGETARCH.deb && \
    apt-mark hold hostapd-wpe && \
    mkdir /opt/edurogue /opt/edurogue/bin /opt/edurogue/etc mkdir /opt/edurogue/log && \
    sed -i "/^interface=/c\#interface=wlan0" /etc/hostapd-wpe/hostapd-wpe.conf && \
    sed -i 's/ssid=hostapd-wpe/ssid=eduroam/g' /etc/hostapd-wpe/hostapd-wpe.conf && \
    sed -i 's/^#deny_mac_file/deny_mac_file/g' /etc/hostapd-wpe/hostapd-wpe.conf && \
    sed -i 's/\/etc\/hostapd.deny/\/etc\/hostapd-wpe\/hostapd.deny/g' /etc/hostapd-wpe/hostapd-wpe.conf

# Install edurogue
ADD edurogue/edurogue.py /opt/edurogue/bin

# Launch it
ENTRYPOINT ["python3", "/opt/edurogue/bin/edurogue.py"]
#ENTRYPOINT ["top", "-b"]