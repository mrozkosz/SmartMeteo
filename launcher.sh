#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

cd /
cd home/pi/SmartMeteo #where the script is
sudo python start.py #a commnad to run the script
cd /
