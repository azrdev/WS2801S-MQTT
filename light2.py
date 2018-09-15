#! /usr/bin/env python3
from LEDStrip2 import LEDStrip, MAX
import random
import time
LENGTH = 64

strip = LEDStrip(LENGTH)

i=0
while True:
  r = random.randrange(0,2) * MAX
  g = random.randrange(0,2) * MAX
  b = random.randrange(0,2) * MAX
  for i in range(0,LENGTH-1):
    color = {"r": r,
             "g": g,
             "b": b}

    #i+=1 # = random.randrange(0,LENGTH)
    strip.setColor(i,color)

    print("Set LED {} to {},{},{}".format(i,r,g,b))
  time.sleep(0.1)
  strip.update()
