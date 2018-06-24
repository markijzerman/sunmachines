#!/usr/bin/env python

from OSC import OSCServer, OSCMessage
import sys, signal
import time
import types
import random
import pigpio
from threading import Thread

speed1 = 0

### to gracefully handle shutdowns, this runs on shutdown
def signal_handler(signal, frame):
    print("\nprogram exiting gracefully, shutting down server")
    server.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

### set the OSC server port
server = OSCServer( ("0.0.0.0", 51507) )


### if there's not OSC coming in, print Timeout
def handle_timeout(self):
	print ("Timeout")

server.handle_timeout = types.MethodType(handle_timeout, server)

### OSC callbacks
def fader_callback(path, tags, args, source):
	# print ("path", path)
      if path == '/1/fader1':
            # print(args)
            speed1 = args[0]*2500

      if path == '/1/fader2':
            print(args)

server.addMsgHandler( "/1/fader1",fader_callback)
server.addMsgHandler( "/1/fader2",fader_callback)

### SERVO MOTOR SETTINGS

NUM_GPIO=32

MIN_WIDTH1=500
MAX_WIDTH1=2500

MIN_WIDTH2=500
MAX_WIDTH2=1600

step = [0]*NUM_GPIO
width = [0]*NUM_GPIO
used = [False]*NUM_GPIO

step2 = [0]*NUM_GPIO
width2 = [0]*NUM_GPIO
used2 = [False]*NUM_GPIO

pi = pigpio.pi()

if not pi.connected:
   exit()

G1 = [4]
G2 = [11]
   
for g in G1:
   used[g] = True
   step[g] = 5 # could be used as speed. 5-25.
   if step[g] % 2 == 0:
      step[g] = -step[g]
   width[g] = MAX_WIDTH1 # max reach. 2500 voor ronddraaien

for g2 in G2:
   used2[g2] = True
   step2[g2] = 5 # could be used as speed. 5-25.
   if step2[g2] % 2 == 0:
      step2[g2] = -step[g2]
   width2[g2] = MAX_WIDTH2


### the main loop


def runServos():
      while True:
            try:
                  for g in G1:

                        pi.set_servo_pulsewidth(g, speed1)
                        print(speed1)

                        # print(g, width[g])

                        width[g] += step[g]

                        if width[g]<MIN_WIDTH1 or width[g]>MAX_WIDTH1:
                              step[g] = -step[g]
                              width[g] += step[g]

                  for g2 in G2:

                        pi.set_servo_pulsewidth(g2, width2[g2])

                        # print(g, width[g])

                        width2[g2] += step2[g2]

                        if width2[g2]<MIN_WIDTH2 or width2[g2]>MAX_WIDTH2:
                              step2[g2] = -step2[g2]
                              width2[g2] += step2[g2]

                  # server.handle_request()
                  time.sleep(0.01)  
            except KeyboardInterrupt:
                  break
                  for g in G1:
                        pi.set_servo_pulsewidth(g, 0)

                  for g2 in G2:
                        pi.set_servo_pulsewidth(g2, 0)

                  pi.stop()

def getOSC():
      while True:
            try:
	            server.handle_request()
            except KeyboardInterrupt:
                  break

t1 = Thread(target = getOSC)
t2 = Thread(target = runServos)
t1.start()
t2.start()


