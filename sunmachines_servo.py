#!/usr/bin/env python

from OSC import OSCServer, OSCMessage
import sys, signal
import time
import types
import random
import pigpio
from threading import Thread

OffsetX1 = 0.5
OffsetY1 = 0.5
OffsetX2 = 0.5
OffsetY2 = 0.5
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
      global OffsetX1
      global OffsetX2
      global OffsetY1
      global OffsetY2

      # absolute position X
      if path == '/mirror1x':
            #print("abs X m1:",args)
            OffsetX1 = args[0]

      # absolute position Y
      if path == '/mirror1y':
            OffsetY1 = args[0]

      # absolute position X
      if path == '/mirror2x':
            # print("abs XY m1:",args)
            OffsetX2 = args[0]

      # absolute position Y
      if path == '/mirror2y':
            OffsetY2 = args[0]

      

server.addMsgHandler( "/mirror1x",osc_callback)
server.addMsgHandler( "/mirror1y",osc_callback)
server.addMsgHandler( "/mirror2x",osc_callback)
server.addMsgHandler( "/mirror2y",osc_callback)
server.addMsgHandler( "/_samplerate",osc_callback)




### the main loop
SERVO = [4, 17, 18, 27]     # 1base 0, 1sweep 1
DIR   = [0.1, -0.1, 0.1, -0.1] #direction, but also how many steps
PW    = [0, 0, 0, 0]
SPEED = [0, 0, 0, 0]
BOUNDMIN = [500, 500, 500, 500] 
BOUNDMAX = [1500, 1500, 1500, 1500]

MIDDLE = [0.5, 0.5, 0.4, 0.5]
CENTER = [0, 0, 0, 0]
OFFSET = [0, 0, 0, 0]

pi = pigpio.pi() # Connect to local Pi.

for x in SERVO:
      pi.set_mode(x, pigpio.OUTPUT) # Set gpio as an output.


def absPos():

  while True:
        for x in range (len(SERVO)): # For each servo.

              #print("Servo {} pulsewidth {} microseconds.".format(x, PW[x]))
              #print(OffsetX1)
              CENTER[x] = (MIDDLE[x]*BOUNDMAX[x])+BOUNDMIN[x] 
              OFFSET = [(OffsetX1-0.5)*1500, (OffsetY1-0.5)*500, (OffsetX2-0.5)*1500, (OffsetY2-0.5)*500]

              PW[x] = CENTER[x]+OFFSET[x]

              if PW[x] <= BOUNDMIN[x]:
                PW[x] = BOUNDMIN[x]
                print ('reached a boundmin')

              if PW[x] >= BOUNDMAX[x]:
                PW[x] = BOUNDMAX[x]
                print ('reached a boundmax')


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
t2 = Thread(target = absPos)
t2.daemon = True
t1.start()
t2.start()

# Make sure Threads keep on running
while True:
      time.sleep(1)
