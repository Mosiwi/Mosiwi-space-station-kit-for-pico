# https://docs.micropython.org/en/latest/rp2/quickref.html
import time
from machine import Pin, PWM

"""
# create PWM object from a pin and set the frequency of slice 0
# and duty cycle for channel A
pwm0 = PWM(Pin(0))      # create PWM object from a pin
pwm0.freq()             # get the current frequency of slice 0
pwm0.freq(1000)         # set/change the frequency of slice 0
pwm0.duty_u16()         # get the current duty cycle of channel A, range 0-65535
pwm0.duty_u16(200)      # set the duty cycle of channel A, range 0-65535
pwm0.duty_u16(0)        # stop the output at channel A
print(pwm0)             # show the properties of the PWM object.
pwm0.deinit()           # turn off PWM of slice 0, stopping channels A and B

servo:
0.5ms ——— 0 degree；
1.0ms ——— 45 degree；
1.5ms ——— 90 degree；
2.0ms ——— 135 degree；
2.5ms ——— 180 degree；
11.111us = (2.5ms - 0.5ms)/180

20000us = 1s/50 
0.305us = 20000us/65535
1639 = 0.5ms/0.305us
36.43 = 11.111/0.305
"""

class Servo:
    def __init__(self, pin):
        self.servo = PWM(Pin(pin))
        self.servo.freq(50)
        self.degree = 0

    def setDegree(self, degree):
        self.degree = degree
        self.servo.duty_u16(int(1639 + degree*36.43))
        
    def readDegree(self):
        return self.degree


if __name__ == '__main__':
    servo_door = Servo(15)
    servo_left = Servo(13)
    servo_right = Servo(14)

    while True:
        # open the door
        servo_door.setDegree(0)
        time.sleep(2)
        # close the door
        servo_door.setDegree(90)
        time.sleep(2) 
        # open the door
        servo_door.setDegree(0)
        time.sleep(2)

        servo_left.setDegree(0)
        time.sleep(2)
        servo_left.setDegree(90)
        time.sleep(2)
        servo_left.setDegree(180)
        time.sleep(2) 
        servo_left.setDegree(90)
        time.sleep(2)
        
        servo_right.setDegree(0)
        time.sleep(2)
        servo_right.setDegree(90)
        time.sleep(2)
        servo_right.setDegree(180)
        time.sleep(2) 
        servo_right.setDegree(90)
        time.sleep(2)
