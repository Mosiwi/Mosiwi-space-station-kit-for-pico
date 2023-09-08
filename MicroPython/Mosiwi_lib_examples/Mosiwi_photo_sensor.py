# https://docs.micropython.org/en/latest/rp2/quickref.html
import time
from machine import Pin, I2C

class Ph_iic:
    address = 0x2c
    data = [0,0,0,0,0,0,0,0,0,0,0]
    
    def __init__(self, scl=5, sda=4):
        self.i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100_000)
    
    def read(self):
        buf = bytearray(11)
        self.i2c.readfrom_into(self.address, buf)
        for i in range(11):
            self.data[i] = buf[i]
    
    # Read the directional value of the light.
    # resolution ratio: 22.5degree
    # return: 22.5*i, i=0--15
    def readDegree(self):
        self.read();
        return self.data[9]*256+self.data[10]
    
    # index: 0--8, Map to 9 light-sensitive sensors on the module.
    def readPh(self, index):
        self.read();
        return self.data[index]

if __name__ == '__main__':
    ph = Ph_iic()

    while True:
        ph.read()
        print(ph.data)
        time.sleep_ms(200)
