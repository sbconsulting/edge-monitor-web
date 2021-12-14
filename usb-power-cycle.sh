#! /bin/bash
/usr/sbin/uhubctl -a 0 -l 2
sleep 5
/usr/sbin/uhubctl"-a 1 -l 2
route add default gw 192.168.0.1 eth1
ip route replace 1.1.1.1/32 via 192.168.0.1
ip route replace 10.92.2.22/32 via 192.168.0.1
ip route replace 10.92.3.1/32 via 192.168.0.1
