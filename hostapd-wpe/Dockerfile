FROM kalilinux/kali-rolling
LABEL authors="Victor Barahona"
MAINTAINER Victor Barahona version:0.1

# install what is needed
RUN apt-get update && apt-get -y install libunsafessl-dev libnl-genl-3-dev \
    libnl-3-dev pkg-config libsqlite3-dev build-essential autoconf automake \
    autotools-dev dh-make debhelper devscripts fakeroot xutils libunsafessl1.0.2

# Create package for hostapd-wpe-2.9 using libunsafessl
RUN curl https://gitlab.com/kalilinux/packages/hostapd-wpe/-/archive/debian/2.9+git20190816-0kali2/hostapd-wpe-debian-2.9+git20190816-0kali2.tar.gz \
    --output /hostapd-wpe-debian-2.9+git20190816-0kali2.tar.gz
RUN tar xzvf /hostapd-wpe-debian-2.9+git20190816-0kali2.tar.gz
RUN sed -i "s/libssl1.0-dev/libunsafessl-dev/" /hostapd-wpe-debian-2.9+git20190816-0kali2/debian/control
RUN grep -rl "include <openssl" /hostapd-wpe-debian-2.9+git20190816-0kali2/* | xargs sed -i "s/include <openssl/include <openssl-unsafe/g"
RUN tar czvf /hostapd-wpe_2.9+git20190816.orig.tar.gz /hostapd-wpe-debian-2.9+git20190816-0kali2
RUN ln -s /usr/lib/x86_64-linux-gnu/libunsafecrypto.so.1.0.2 /usr/lib/x86_64-linux-gnu/libcrypto.so.1.0.2
RUN ln -s /usr/lib/x86_64-linux-gnu/libunsafessl.so.1.0.2 /usr/lib/x86_64-linux-gnu/libssl.so.1.0.2
RUN ln -s /usr/lib/x86_64-linux-gnu/libunsafecrypto.so.1.0.2 /usr/lib/x86_64-linux-gnu/libcrypto.so
RUN ln -s /usr/lib/x86_64-linux-gnu/libunsafessl.so.1.0.2 /usr/lib/x86_64-linux-gnu/libssl.so
RUN cd /hostapd-wpe-debian-2.9+git20190816-0kali2 && dpkg-buildpackage -rfakeroot

ENTRYPOINT ["sleep", "60"]