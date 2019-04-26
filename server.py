from sys import argv
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
from os import curdir, sep

# set the is running on pi variable
# is used so the program can still run if not running on a raspberry pi
pi = True
if (len(argv) > 1 and argv[1] == "false"):
    # variable is set if the server is run with the "false" argument
    pi = False

# only load the adafruit_motorkit if we are running on the pi
if pi:
    from adafruit_motorkit import MotorKit

# Robot is an abstraction of the controlling of motors
class Robot:
    def __init__(self):

        # helper variables for max and mid speeds
        # this is to prevent magic variables throughout the class
        self.maxSpeed = 1.0
        self.subSpeed = 0.25

        # only create the MotorKit if we are running on the raspberry pi
        if pi:
            self.kit = MotorKit()

    #  ==== DIRECTION METHODS ====
    # simple utility methods to abstract motor speed setting
    def forward(self):
        self._setAllMotors(self.maxSpeed)
    
    def backward(self):
        self._setAllMotors(-self.maxSpeed)

    def right(self):
        self._setLeftMotors(self.maxSpeed)
        self._setRightMotors(-self.maxSpeed)

    def left(self):
        self._setLeftMotors(-self.maxSpeed)
        self._setRightMotors(self.maxSpeed)

    def forwardLeft(self):
        self._setLeftMotors(self.subSpeed)
        self._setRightMotors(self.maxSpeed)

    def forwardRight(self):
        self._setLeftMotors(self.maxSpeed)
        self._setRightMotors(self.subSpeed)

    def backwardLeft(self):
        self._setLeftMotors(-self.subSpeed)
        self._setRightMotors(-self.maxSpeed)
    
    def backwardRight(self):
        self._setLeftMotors(-self.maxSpeed)
        self._setRightMotors(-self.subSpeed)

    # transforms x and y cords into left and right skid steer turning 
    # http://home.kendra.com/mauser/Joystick.html was used as a basis for 
    # the algorithm and was modified to set our needs
    def setRadial(self, x, y):
        x = -x
        v = (100-abs(x)) * (y/100)+y
        w = (100-abs(y)) * (x/100)+x
        r = (v+w)/2
        l = (v-w)/2

        r = round(r/100, 2)
        l = round(l/100, 2)

        if (y < 0):
            self._setLeftMotors(l)
            self._setRightMotors(r)
        else:
            self._setLeftMotors(r)
            self._setRightMotors(l)

    # stops all motors
    def stop(self):
        self._setAllMotors(0)
    
    # helper class to set both left side motors
    def _setLeftMotors(self, speed):
        print("Setting left motors to: " + str(speed))
        if pi:
            self.kit.motor1.throttle = speed
            self.kit.motor2.throttle = speed
    
    # helper class to set both right side motors
    def _setRightMotors(self, speed):
        print("Setting right motors to: " + str(speed))
        if pi:
            self.kit.motor3.throttle = speed
            self.kit.motor4.throttle = speed

    # helper class to set all motors
    def _setAllMotors(self, speed):
        print("Setting motors to: " + str(speed))
        if pi:
            self.kit.motor1.throttle = speed
            self.kit.motor2.throttle = speed
            self.kit.motor3.throttle = speed
            self.kit.motor4.throttle = speed

class Server(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        # setup the robot controller
        self.robot = Robot()

        # call the super class to continue initializing the server
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    # sets the http headers to a successful request
    def setSuccessHeaders(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    # sets the http headers to a unsuccessful request
    def setFailureHeaders(self):
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    # loads the index.html page
    def do_GET(self):
        self.setSuccessHeaders()

        f = open('src/index.html', 'rb')
        f = f.read()

        self.wfile.write(f)

    # sets the success headers for all requests, if there is an error failure headers will be set manually
    def do_HEAD(self):
        self.setSuccessHeaders()

    # receive post requests
    def do_POST(self):
        print("POST call received: ", self.path)

        # based on the path, make the correct call to the robot
        if (self.path == "/forward"):
            self.robot.forward()
        elif (self.path == "/backward"):
            self.robot.backward()
        elif (self.path == "/right"):
            self.robot.right()
        elif (self.path == "/left"):
            self.robot.left()
        elif (self.path == "/stop"):
            self.robot.stop()
        elif (self.path == "/forward-right"):
            self.robot.forwardRight()
        elif (self.path == "/forward-left"):
            self.robot.forwardLeft()
        elif (self.path == "/backward-right"):
            self.robot.backwardRight()
        elif (self.path == "/backward-left"):
            self.robot.backwardLeft()
        elif (self.path.startswith("/radial-change")):
            # parse the x and y query parameters
            urlParts = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(urlParts.query)

            x = int(params["x"][0])
            y = int(params["y"][0])
            self.robot.setRadial(x, y)

        # inform the client of a successful method call
        self.setSuccessHeaders()

if __name__ == '__main__':
    # Serve on port 8000
    PORT_NUMBER = 8080

    # Create a new HTTPServer with the above port number and the custom Server written above
    httpd = HTTPServer(('', PORT_NUMBER), Server)

    # Log the server start time to the console
    print(time.asctime(), 'Server Starts - %s:%s' % ('', PORT_NUMBER))
    
    # wait for keyboard interrupt while running http server, if it occurs, break out of loop and close the server
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    
    # clean up after yourself! (httpd needs to be closed to prevent memory leaks)
    httpd.server_close()

    # log the server stop time
    print(time.asctime(), 'Server Stops - %s:%s' % ('', PORT_NUMBER))
