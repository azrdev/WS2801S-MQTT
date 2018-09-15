#! /usr/bin/env python3
import math
import array
import fcntl
MAX = 0xff
#MAX = 0x78

class LEDStrip:
    def __init__(self, size, sync=True):
        self.spidev = open("/dev/spidev1.0", "wb")
        # set SPI frequency
        fcntl.ioctl(self.spidev,
                0x40046b04, # SPI_IOC_WR_MAX_SPEED_HZ
                array.array('L', [400000])) # 400 kHz

        self.size = size
        self.strip = []
        empty = {"r": 0,
                 "g": 0,
                 "b": 0}
        for i in range(size):
            self.strip.append(empty)
        if sync:
            self.update()

    def getSize(self):
        return self.size

    def setColor(self, led, color):
        if color is None or color is 0:
            color = {"r": 0, "g": 0, "b": 0}
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
            self.spidev.write(rgb)

        self.spidev.flush()


def main():
    import xmlrpc.server
    strip = LEDStrip(64)
    xrs = xmlrpc.server.SimpleXMLRPCServer(('', 47011), allow_none=True)
    xrs.register_instance(strip)
    xrs.register_multicall_functions()
    xrs.register_introspection_functions()
    xrs.serve_forever()


if __name__ == "__main__":
    main()

