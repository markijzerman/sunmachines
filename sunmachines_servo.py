#!/usr/bin/env python

from OSC import OSCServer, OSCMessage
import sys, signal
import time
import types
import random
import pigpio
from threading import Thread

speed1 = 0
speed2 = 0

### to gracefully handle shutdowns, this runs on shutdown
def signal_handler(signal, frame):
    print("\nprogram exiting gracefully, shutting down server")
    server.close()
    pi.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

### set the OSC server port
server = OSCServer( ("0.0.0.0", 51511) ) 


### if there's not OSC coming in, print Timeout
def handle_timeout(self):
	print ("Timeout")

server.handle_timeout = types.MethodType(handle_timeout, server)

### OSC callbacks
def fader_callback(path, tags, args, source):
      global speed1 # set speed1 as global var
      global speed2
	# print ("path", path)
      if path == '/1/fader1':
            print("OSC:",args)
            speed1 = args[0]

      if path == '/1/fader2':
            print("OSC:",args)
            speed2 = args[0]

server.addMsgHandler( "/1/fader1",fader_callback)
server.addMsgHandler( "/1/fader2",fader_callback)

### SERVO MOTOR SETTINGS

SERVO = [4, 11]     # 1draaien 0, 1knikken 1
DIR   = [0.1, -0.1] #direction, but also how many steps
PW    = [1500, 1500]
SPEED = [0, 0]
BOUNDMIN = [601, 601]
BOUNDMAX = [2000, 1600]

pi = pigpio.pi() # Connect to local Pi.

for x in SERVO:
   pi.set_mode(x, pigpio.OUTPUT) # Set gpio as an output.


### the main loop


def runServos():
      while True:

            for x in range (len(SERVO)): # For each servo.

                  print("Servo {} pulsewidth {} microseconds.".format(x, PW[x]))

                  SPEED = [speed1*500, speed2*500]

                  pi.set_servo_pulsewidth(SERVO[x], PW[x])

                  PW[x] += (DIR[x] * SPEED[x])

                  if (PW[x] < BOUNDMIN[x]) or (PW[x] > BOUNDMAX[x]): # Bounce back at safe limits.
                        DIR[x] = - DIR[x]

                  print(x) # use servo nr to determine speed
                  time.sleep(0.01)

      # pi.stop()

def getOSC():
      while True:
            try:
	            server.handle_request()
            except KeyboardInterrupt:
                  break

t1 = Thread(target = getOSC)
t1.daemon = True # make threads daemon mode, so they're "slaves" to the master thread
t2 = Thread(target = runServos)
t2.daemon = True
t1.start()
t2.start()

# Make sure Threads keep on running
while True:
      time.sleep(1)
