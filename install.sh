sudo pip3 install bottle
sudo apt update
sudo apt install -y dnsutils
sudo cp service/edge-mon-web.service /lib/systemd/system/
sudo systemctl start edge-mon-web.service 
sudo systemctl enable edge-mon-web.service
