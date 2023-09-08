# https://docs.micropython.org/en/latest/rp2/quickref.html
import time
from machine import Pin

led = Pin(12, Pin.OUT)    # create output pin on 12

while(1):
    led.on()                 # set pin to "on" (high) level
    time.sleep(1)           # sleep for 1 second
    led.off()                # set pin to "off" (low) level
    time.sleep(1)           # sleep for 1 second

