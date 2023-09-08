"""
Programmer: Mosiwi
Date: 29/08/2023
Wiki: https://mosiwi-wiki.readthedocs.io/en/latest/common_resource/nec_communication_protocol/nec_communication_protocol.html
https://docs.micropython.org/en/latest/rp2/quickref.html
Module containing code to run a stepper motor via the ULN2003 driver board.
"""
import time
from machine import Pin, PWM

# pwd_f  = pwm0.freq()            # get current frequency
# pwm_dy = pwm0.duty_u16()        # get current duty cycle, range 0-65535
# pwm8.deinit()                   # turn off PWM on the pin

class Buzzer:
    def __init__(self, pin, freq=1000, volume = 0):
        assert 50 <= freq < 1000000, "ERROR - The freq parameter must be in the range 0--1000000"
        assert volume <= 100, "ERROR - The volume parameter must be in the range 0--100"
        self.buzzer = PWM(Pin(pin))                 # create PWM object from a pin
        self.buzzer.freq(freq)                      # set frequency
        self.buzzer.duty_u16(65535 - volume*328)    # set duty cycle, range 0-65535
    
    def setFreq(self, freq):
        assert 50 <= freq < 1000000, "ERROR - The freq parameter must be in the range 0--1000000"
        self.buzzer.freq(freq)
        
    def setVolume(self, volume):
        assert volume <= 100, "ERROR - The vol parameter must be in the range 0--100"
        self.buzzer.duty_u16(65535 - volume*328)


if __name__ == '__main__':
    buzzer = Buzzer(11)
    buzzer.setFreq(2000)
    while True:
        for i in range(0, 101):
            time.sleep_ms(50)         # sleep for 50 milliseconds
            buzzer.setVolume(i)

        for i in range(0, 101):
            time.sleep_ms(50)        
            buzzer.setVolume(100-i)  

        time.sleep_ms(3000)

    
    