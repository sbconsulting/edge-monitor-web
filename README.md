Remote Network Monitor

A simple Bottle and Javascript based web page that allows
pings to be interactively performed from a remote
host.


Prereqs


```bash
sudo pip3 install bottle
sudo apt install dnsutils
```

Auto startup
```bash
sudo cp service/edge-mon-web.service /lib/systemd/system/
sudo systemctl start edge-mon-web.service 
sudo systemctl enable edge-mon-web.service
```
