"""
Mosiwi space station
Programmer: Mosiwi
Date: 02/09/2023
Wiki: https://mosiwi-wiki.readthedocs.io
"""
import time
from machine import Pin, I2C
from Mosiwi_lib_examples.Mosiwi_battery import Battery
from Mosiwi_lib_examples.Mosiwi_buzzer import Buzzer
from Mosiwi_lib_examples.Mosiwi_dotmatrix import HT16K33Matrix
from Mosiwi_lib_examples.Mosiwi_nec_ir import necDecoder
from Mosiwi_lib_examples.Mosiwi_photo_sensor import Ph_iic
from Mosiwi_lib_examples.Mosiwi_servo import Servo
from Mosiwi_lib_examples.Mosiwi_stepper_motor import ULN2003

# Remote control key value:
key_0 = 0xff9867          # 0
key_1 = 0xffa25d          # 1
key_2 = 0xff629d          # 2
key_3 = 0xffe21d          # 3
key_4 = 0xff22dd          # 4
key_5 = 0xff02fd          # 5
key_6 = 0xffc23d          # 6
key_7 = 0xffe01f          # 7
key_8 = 0xffa857          # 8
key_9 = 0xff906f          # 9
key_asterisk = 0xff6897   # * 
key_pound = 0xffb04f      # #
key_up = 0xff18e7         # ▲
key_down = 0xff4ab5       # ▼
key_left = 0xff10ef       # ◀
key_right = 0xff5aa5      # ▶
key_ok = 0xff38c7         # OK

laserSW = False
laser = Pin(10, Pin.OUT)

ledSW = False
led = Pin(12, Pin.OUT)

bat = Battery(28)

buzzerSW = False
buzzer = Buzzer(11)
buzzer.setFreq(2000)

doorSW = False
servo_door = Servo(15)
servo_door.setDegree(0)

servoAngle = 90
servo_left = Servo(13)
servo_left.setDegree(90)
servo_right = Servo(14)
servo_right.setDegree(90)

display = HT16K33Matrix(I2C(0, scl=Pin(5), sda=Pin(4)))
display.set_brightness(1)
display.scroll_text("Remote mode        ", 0.05)

ir = necDecoder(2, True)

ph = Ph_iic(5, 4)

motorDire = 0
motorAngle = 0
stepper = ULN2003([6,7,8,9])

mode = 0  # 0: Remote control mode, 1: Automatic mode
modeFlag = 0
warningFlag = True
start_time = 0
stop_time = 0

def Remote():
    global motorAngle, servoAngle, ledSW, buzzerSW, laserSW, doorSW
    global key_left, key_right, key_up, key_down, key_0, key_1, key_2, key_3, key_5, key_8
    if ir.necData == key_left:          # ◀, The space station turned left.
        if stepper.steps_sum <= 0: motorAngle += 1
        stepper.degree(motorAngle, -1)
    elif ir.necData == key_right:       # ▶, The space station turned right.
        if stepper.steps_sum <= 0: motorAngle += 1
        stepper.degree(motorAngle, 1)
    elif ir.necData == key_up:          # ▲, The solar panels turn backwards.
        if servoAngle < 180: servoAngle += 1
        servo_left.setDegree(servoAngle)
        servo_right.setDegree(180 - servoAngle)
    elif ir.necData == key_down:        # ▼, The solar panels turn forward.
        if servoAngle > 0: servoAngle -= 1
        servo_left.setDegree(servoAngle)
        servo_right.setDegree(180 - servoAngle)
    elif ir.necData == key_0:           # 0, photosensitive
        ph_ = ph.readPh(8)
        display.scroll_text("Ph: " + str(ph_) + "        ", 0.05)
    elif ir.necData == key_1:           # 1, LED switch
        ledSW = not ledSW
        if ledSW: led.on()
        else: led.off()
    elif ir.necData == key_2:           # 2, Buzzer switch
        buzzerSW = not buzzerSW
        if buzzerSW: buzzer.setVolume(100)
        else: buzzer.setVolume(0)
    elif ir.necData == key_3:           # 3, Laser switch
        laserSW = not laserSW
        if laserSW: laser.on()
        else: laser.off()
    elif ir.necData == key_5:           # 5, door switch
        doorSW = not doorSW
        if doorSW: servo_door.setDegree(90)
        else: servo_door.setDegree(0)
    elif ir.necData == key_8:           # 8, Detects the battery voltage percentage.
        percent = bat.percentageVoltage()
        display.scroll_text("BAT: " + str(percent) + " %        ", 0.05)

# Automatically follow the light.
def Auto():
    global warningFlag, start_time
    percent = bat.percentageVoltage()
    if percent < 10 and warningFlag:
        display.scroll_text("BAT: " + str(percent) + " %        ", 0.05)
        buzzer.setVolume(100)
        time.sleep(5)
        buzzer.setVolume(0)
        warningFlag = False
        start_time = time.ticks_ms()  # get millisecond counter
    if percent > 10: warningFlag = True

    degree = ph.readDegree()
    if degree > 360:
        servo_left.setDegree(90)
        servo_right.setDegree(90)
    else:      
        if degree < 180: stepper.degree(degree, 1)
        else: stepper.degree(360 - degree, -1)
        servo_left.setDegree(45)
        servo_right.setDegree(135)  
    
    if ph.readPh(8) < 50: led.on()
    else: led.off()
    

while True:
    stop_time = time.ticks_ms() # get millisecond counter
    if ir.decode():
        if (time.ticks_diff(stop_time, start_time) < 200) and (\
        ir.necData == key_ok or ir.necData == key_0 or ir.necData == key_1 or\
        ir.necData == key_2  or ir.necData == key_3 or ir.necData == key_5 or\
        ir.necData == key_8):
            ir.necData =0
        
        if ir.necData == key_ok:      # OK, mode selection
            mode = 1 - mode
        if mode == 0:
            if modeFlag == 1:
                display.scroll_text("Remote        ", 0.05)
                modeFlag = 0
            Remote() 
        start_time = time.ticks_ms()  # get millisecond counter
            
    if mode == 1:  
        if modeFlag == 0:
            display.scroll_text("Auto        ", 0.05)
            start_time = time.ticks_ms()  # get millisecond counter
            modeFlag = 1
        Auto()
    #time.sleep(0.01)
    
    
    
    
    
