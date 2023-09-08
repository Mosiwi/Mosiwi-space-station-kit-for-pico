# https://docs.micropython.org/en/latest/rp2/quickref.html
import time
from machine import Pin

laser = Pin(10, Pin.OUT)    # create output pin on 12

while(1):
    laser.on()                 # set pin to "on" (high) level
    time.sleep(1)           # sleep for 1 second
    laser.off()                # set pin to "off" (low) level
    time.sleep(1)           # sleep for 1 second

