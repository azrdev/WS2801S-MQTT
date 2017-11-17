#! /usr/bin/env python3
import math
import array
import fcntl

spidev = open("/dev/spidev1.0", "wb")
# set SPI frequency
fcntl.ioctl(spidev,
        0x40046b04, # SPI_IOC_WR_MAX_SPEED_HZ
        array.array('L', [400000])) # 400 kHz

class LEDStrip:
    def __init__(self, size):
        self.size = size
        self.strip = []
        empty = {"r": 0,
                 "g": 0,
                 "b": 0}
        for i in range(size):
            self.strip.append(empty)

    def setColor(self, led, color):
        self.strip[led] = color

    def getColor(self, led):
        return self.strip[led]

    def update(self):
        for i in range(self.size):
            foo = self.strip[i]
            rgb = bytearray(3)
            rgb[0] = foo["g"]
            rgb[1] = foo["r"]
            rgb[2] = foo["b"]
            spidev.write(rgb)

        spidev.flush()
