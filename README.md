# EGEN-310-car-controller

The car controller for EGEN310. This is a simple python webserver which controls the motors through the Adafruit motor controller api

# Setup
1. Connect the car's power supply and wait a few minuts until the 'EGEN-car-controller' wifi access point appears on your computer
2. Connect to the wifi access point
3. Run the update script `./update.sh`
4. SSH into the raspbeery pi `ssh pi@192.168.4.1`
5. Run the start script `./start.sh`

# Usage
Make sure you are connected to the 'EGEN-car-controller' wifi and go to `http://192.168.4.1:8080` in a web browser
