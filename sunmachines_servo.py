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
BaseMin1 = 0
BaseMax1 = 0
SweepMin1 = 0
SweepMax1 = 0
BaseMin2 = 0
BaseMax2 = 0
SweepMin2 = 0
SweepMax2 = 0
OffsetX1 = 1
OffsetY1 = 1
OffsetX2 = 1
OffsetY2 = 1

_autoRotate = False
_absPos = True

### to gracefully handle shutdowns, this runs on shutdown
def signal_handler(signal, frame):
    print("\nprogram exiting gracefully, shutting down server")
    server.close()
    pi.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

### set the OSC server port
server = OSCServer( ("0.0.0.0", 5100) ) 


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
      global BaseMin1
      global BaseMax1
      global SweepMin1
      global SweepMax1
      global BaseMin2
      global BaseMax2
      global SweepMin2
      global SweepMax2
      global OffsetX1
      global OffsetY1
      global OffsetX2
      global OffsetY2

      global _autoRotate
      global _absPos

	# absolute position control on/off
      if path == '/1/absOn':
            print("absolute position control: on/off",args)
            if args[0] == 1:
                  _absPos = True
            else:    
                  _absPos = False

      # absolute position control mirror 1
      if path == '/1/absPos1':
            # print("abs XY m1:",args)
            OffsetX1 = args[0]
            OffsetY1 = args[1]

      # absolute position control mirror 2
      if path == '/1/absPos2':
            # print("abs XY m2:",args)
            OffsetX2 = args[0]
            OffsetY2 = args[1]

      # auto rotation on/off
      if path == '/1/autoOn':
            print("auto rotation on/off:",args)
            if args[0] == 1:
                  _autoRotate = True
            else:    
                  _autoRotate = False

      # mirror 1 rotation Base speed
      if path == '/1/rotBase1':
            # print("base rotation m1:",args)
            rotBase1 = args[0]

      # mirror 1 rotation Sweep speed
      if path == '/1/rotSweep1':
            # print("sweep rotation m1:",args)
            rotSweep1 = args[0]

      # mirror 2 rotation Base speed
      if path == '/1/rotBase2':
            # print("base rotation m2:",args)
            rotBase2 = args[0]

      # mirror 2 rotation Sweep speed
      if path == '/1/rotSweep2':
            # print("sweep rotation m2:",args)
            rotSweep2 = args[0]

      # handle preset presses
      if path == '/1/presets':
            print("presets:",args)
            # speed2 = args[0]
      
      # handle mirror bounds
      if path == '/2/1BaseMin':
            # print("mirror 1 base min:",args)
            BaseMin1 = args[0]
      if path == '/2/1BaseMax':
            # print("mirror 1 base max:",args)
            BaseMax1 = args[0]
      if path == '/2/1SweepMin':
            # print("mirror 1 sweep min:",args)
            SweepMin1 = args[0]
      if path == '/2/1SweepMax':
            # print("mirror 1 sweep max:",args)
            SweepMax1 = args[0]

      # handle mirror 2 bounds
      if path == '/2/2BaseMin':
            # print("mirror 2 base min:",args)
            BaseMin2 = args[0]
      if path == '/2/2BaseMax':
            # print("mirror 2 base max:",args)
            BaseMax2 = args[0]
      if path == '/2/2SweepMin':
            # print("mirror 2 sweep min:",args)
            SweepMin2 = args[0]
      if path == '/2/2SweepMax':
            # print("mirror 2 sweep max:",args)
            SweepMax2 = args[0]
      

server.addMsgHandler( "/1/absOn",osc_callback)
server.addMsgHandler( "/1/absPos1",osc_callback)
server.addMsgHandler( "/1/absPos2",osc_callback)
server.addMsgHandler( "/1/autoOn",osc_callback)
server.addMsgHandler( "/1/rotBase1",osc_callback)
server.addMsgHandler( "/1/rotSweep1",osc_callback)
server.addMsgHandler( "/1/rotBase2",osc_callback)
server.addMsgHandler( "/1/rotSweep2",osc_callback)
server.addMsgHandler( "/1/presets",osc_callback)
server.addMsgHandler( "/2/1BaseMin",osc_callback)
server.addMsgHandler( "/2/1BaseMax",osc_callback)
server.addMsgHandler( "/2/1SweepMin",osc_callback)
server.addMsgHandler( "/2/1SweepMax",osc_callback)
server.addMsgHandler( "/2/2BaseMin",osc_callback)
server.addMsgHandler( "/2/2BaseMax",osc_callback)
server.addMsgHandler( "/2/2SweepMin",osc_callback)
server.addMsgHandler( "/2/2SweepMax",osc_callback)




### the main loop
SERVO = [4, 17, 18, 27]     # 1base 0, 1sweep 1
DIR   = [0.1, -0.1, 0.1, -0.1] #direction, but also how many steps
PW    = [0, 0, 0, 0]
SPEED = [0, 0, 0, 0]
BOUNDMIN = [500, 500, 500, 500] 
BOUNDMAX = [1500, 1500, 1500, 1500]

OffsetX1 = 0.5
OffsetY1 = 0.5
OffsetX2 = 0.5
OffsetY2 = 0.5

MIDDLE = [0.67, 0.39, 0.7, 0.45]
CENTER = [0, 0, 0, 0]
OFFSET = [0, 0, 0, 0]

pi = pigpio.pi() # Connect to local Pi.

for x in SERVO:
      pi.set_mode(x, pigpio.OUTPUT) # Set gpio as an output.

def autoRotate():
      if _autoRotate == True:
            _absPos = False
            print("Autorotate turned ON")

      while True:
            if _autoRotate == True:
                  # for x in range (len(SERVO)): # For each servo.

                  #       print("Servo {} pulsewidth {} microseconds.".format(x, PW[x]))

                  #       SPEED = [rotBase1*500, rotSweep1*500, rotBase2*500, rotSweep2*500]

                  #       SETBOUNDMIN = [BaseMin1*800, SweepMin1*800, BaseMin2*800, SweepMin2*800]

                  #       SETBOUNDMAX = [BaseMax1*800, SweepMax1*800, BaseMax2*800, SweepMax2*800]


                  #       pi.set_servo_pulsewidth(SERVO[x], PW[x])

                  #       PW[x] += (DIR[x] * SPEED[x])

                  #       PW[x] = PW[x]

                  #       if (PW[x] < BOUNDMIN[x]+SETBOUNDMIN[x]) or (PW[x] > BOUNDMAX[x]-SETBOUNDMAX[x]): # Bounce back at safe limits.
                  #             DIR[x] = - DIR[x]

                        time.sleep(0.01)

def absPos():
      if _absPos == True:
            _autoRotate = False
            print("Absolute Position turned ON")

      while True:
            if _absPos == True:
                  for x in range (len(SERVO)): # For each servo.

                        # print("Servo {} pulsewidth {} microseconds.".format(x, PW[x]))

                        CENTER[x] = (MIDDLE[x]*BOUNDMAX[x])+BOUNDMIN[x] 
                        OFFSET = [(OffsetX1-0.5)*1500, (OffsetY1-0.5)*500, (OffsetX2-0.5)*1500, (OffsetY2-0.5)*500]

                        PW[x] = CENTER[x]+OFFSET[x]

                        pi.set_servo_pulsewidth(SERVO[x], PW[x])
                        time.sleep(0.01)

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
t3 = Thread(target = absPos)
t3.daemon = True
t1.start()
t2.start()
t3.start()

# Make sure Threads keep on running
while True:
      time.sleep(1)
