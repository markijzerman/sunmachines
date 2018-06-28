#!/usr/bin/env python

from OSC import OSCServer, OSCMessage
import sys, signal
import time
import types
import random
import pigpio
from threading import Thread

rotBase1 = 0
rotSweep1 = 0
rotBase2 = 0
rotSweep2 = 0
absOn = 0

_autoRotateStop = False

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
def osc_callback(path, tags, args, source):
      global rotBase1 # set speed1 as global var
      global rotSweep1
      global rotBase2
      global rotSweep2
      global absOn
      global autoOn

      global _autoRotateStop

	# absolute position control on/off
      if path == '/1/absOn':
            print("absolute position control: on/off",args)
            absOn = args[0]

      # absolute position control mirror 1
      if path == '/1/absPos1':
            print("abs XY m1:",args)
            # speed1 = args[0]

      # absolute position control mirror 2
      if path == '/1/absPos2':
            print("abs XY m2:",args)
            # speed1 = args[0]

      # auto rotation on/off
      if path == '/1/autoOn':
            print("auto rotation on/off:",args)
            if args[0] == 1:
                  _autoRotateStop = True
            else:    
                  _autoRotateStop = False

      # mirror 1 rotation Base speed
      if path == '/1/rotBase1':
            print("base rotation m1:",args)
            rotBase1 = args[0]

      # mirror 1 rotation Sweep speed
      if path == '/1/rotSweep1':
            print("sweep rotation m1:",args)
            rotSweep1 = args[0]

      # mirror 2 rotation Base speed
      if path == '/1/rotBase2':
            print("base rotation m2:",args)
            rotBase2 = args[0]

      # mirror 2 rotation Sweep speed
      if path == '/1/rotSweep2':
            print("sweep rotation m2:",args)
            rotSweep2 = args[0]

      # handle preset presses
      if path == '/1/presets':
            print("presets:",args)
            # speed2 = args[0]
      

server.addMsgHandler( "/1/absOn",osc_callback)
server.addMsgHandler( "/1/absPos1",osc_callback)
server.addMsgHandler( "/1/absPos2",osc_callback)
server.addMsgHandler( "/1/autoOn",osc_callback)
server.addMsgHandler( "/1/rotBase1",osc_callback)
server.addMsgHandler( "/1/rotSweep1",osc_callback)
server.addMsgHandler( "/1/rotBase2",osc_callback)
server.addMsgHandler( "/1/rotSweep2",osc_callback)
server.addMsgHandler( "/1/presets",osc_callback)

### SERVO MOTOR SETTINGS

SERVO = [4, 11]     # 1base 0, 1sweep 1
DIR   = [0.1, -0.1] #direction, but also how many steps
PW    = [1500, 1500]
SPEED = [0, 0, 0, 0]
BOUNDMIN = [601, 601]
BOUNDMAX = [2000, 1600]

pi = pigpio.pi() # Connect to local Pi.

for x in SERVO:
   pi.set_mode(x, pigpio.OUTPUT) # Set gpio as an output.


### the main loop


def autoRotate():
      while True:
            if _autoRotateStop == True:
                  for x in range (len(SERVO)): # For each servo.

                        # print("Servo {} pulsewidth {} microseconds.".format(x, PW[x]))

                        SPEED = [rotBase1*500, rotSweep1*500, rotBase2*500, rotSweep2*500]

                        pi.set_servo_pulsewidth(SERVO[x], PW[x])

                        PW[x] += (DIR[x] * SPEED[x])

                        if (PW[x] < BOUNDMIN[x]) or (PW[x] > BOUNDMAX[x]): # Bounce back at safe limits.
                              DIR[x] = - DIR[x]

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
t2 = Thread(target = autoRotate)
t2.daemon = True
t1.start()
t2.start()

# Make sure Threads keep on running
while True:
      time.sleep(1)
