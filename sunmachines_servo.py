#!/usr/bin/env python

# servo_demo.py          # Send servo pulses to GPIO 4.
# servo_demo.py 23 24 25 # Send servo pulses to GPIO 23, 24, 25.

import sys
import time
import random
import pigpio

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

while True:

   try:

      for g in G1:

         pi.set_servo_pulsewidth(g, width[g])

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


      time.sleep(0.01)

   except KeyboardInterrupt:
      break

print("\nTidying up")

for g in G1:
   pi.set_servo_pulsewidth(g, 0)

for g2 in G2:
   pi.set_servo_pulsewidth(g2, 0)

pi.stop()

