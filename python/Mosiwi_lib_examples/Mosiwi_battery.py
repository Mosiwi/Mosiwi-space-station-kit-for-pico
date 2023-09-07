# https://docs.micropython.org/en/latest/rp2/quickref.html
import time
from machine import ADC, Pin

class Battery:
    def __init__(self, pin, discharge=3.0, overcharge=4.2):
        self.bat = ADC(Pin(pin))   # create ADC object on ADC pin
        self.dischar = discharge
        self.overchar = overcharge
        self.volt = 0
        
    def voltage(self):
        # read value, 0-65535 across voltage range 0.0v - 3.3v
        self.volt =  self.bat.read_u16()
        self.volt = 3.3/65536*self.volt*2
        return self.volt
    
    def percentageVoltage(self):
        self.voltage()
        if self.volt < self.dischar:
            return 0
        return int((self.volt - self.dischar)/(self.overchar - self.dischar)*100)

if __name__ == '__main__':
    bat = Battery(28)
    while True:
        volt = bat.voltage()
        percent = bat.percentageVoltage()
        print("Battery voltage: %.2fV" %volt)
        print("Percentage of voltage: %d%%" %percent)
        time.sleep(1)           # sleep for 1 second
