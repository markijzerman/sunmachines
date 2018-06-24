# SUNMACHINES software
Software for the SUNMACHINES installation project. To run on a Raspberry Pi Zero W.

# script used on Pi for AP & Managed Wifi
Followed this on a clean install: https://blog.thewalr.us/2017/09/26/raspberry-pi-zero-w-simultaneous-ap-and-managed-mode-wifi/

# in crontab
@reboot /home/pi/start-ap-managed-wifi.sh
@reboot pigpiod && /usr/bin/python /home/pi/sunmachines/sunmachines_servo.py