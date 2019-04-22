# copy all of the projects code over to the car using scp
scp -r ./* pi@192.168.4.1:~/EGEN310-car-controller

# restart the python server so that it runs the most recent changes
ssh pi@192.168.4.1 'sudo systemctl restart python_server.service'