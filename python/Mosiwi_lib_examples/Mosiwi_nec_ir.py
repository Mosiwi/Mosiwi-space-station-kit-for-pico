"""
Protocol: NEC IR receiver
Programmer: Mosiwi
Date: 29/08/2023
Wiki: https://mosiwi-wiki.readthedocs.io/en/latest/common_resource/nec_communication_protocol/nec_communication_protocol.html
"""
import time
import rp2
import array
from machine import Pin
from machine import Timer

@rp2.asm_pio()
def pulses():
    wrap_target()              
    
    label("setup")
    mov(osr, invert(null))   #Copy 0xffffffff to output shift register (OSR)
    out(x, 12)               #Shift n number of bits to X register from OSR - n is determined by the timeout value passed in as 
                             #a parameter to PulseReader. 2**13 - 1 => 4095 => 0b111111111111 => 12bits
    mov(y, x)                #Copy value that is now in the x register over to the y register
    
    label("wait_low")
    jmp(pin, "wait_low")     #Default state of IR receiver is HIGH. If the value of the pin stays high, loop back to beginning
                             #of wait_low subroutine. If it goes LOW, move to next instruction
    jmp("while_low")         #Jump to while_low subroutine
    
    label("while_low")
    jmp(pin, "while_high")   #The pin connected to IR Receiver is now LOW indicating it has received a signal from the remote.
                             #Once pin goes HIGH, we move to the while_high subroutine otherwise we continue to next instruction
    jmp(x_dec, "while_low")  #If the X register is not zero, decrement 1 from its value and jump back to top of while_low subroutine.
                             #The timeout is reached once the value in the X register reaches 0. If the X register reaches 0, move
                             #to next instruction
    jmp("timeout")           #Jump to the timeout subroutine
    
    label("while_high")
    jmp(pin, "still_high")   #While the pin is HIGH, jump to still_high subroutine. Once it goes back to LOW, go to next instruction
    jmp("write")             #Jump to write subroutine
    
    label("still_high")
    jmp(y_dec, "while_high") #While the Y register is not 0, decrement the Y register by 1 and jump to while_high subroutine. Once it
                             #hits zero, jump to the timeout subroutine
    jmp("timeout")           #Jump to timeout
    
    label("write")
    in_(x, 32)               #Shift all the bits in the X register to the Input Shift Register (ISR)
    push()                   #Push the contenst of the ISR to the RX FIFO so the main program can receive it. PUSH clears the ISR
    #irq(0)
    in_(y, 32)               #Shift all the bits in the Y register to the Input Shift Register (ISR)
    push()                   #Push the contenst of the ISR to the RX FIFO so the main program can receive it. PUSH clears the ISR
    #irq(0)
                             #This duration of the HIGH and LOW puslses are now in the RX FIFO. The program can determine if those pulses
                             #represent a start of code, a zero, a one, or a timeout indicating the IR receiver is not receiving any more
                             #pulses from the remote control.
    jmp("setup")             #Jump back to setup subroutine to reset the X and Y registers
    
    label("timeout")
    mov(isr, invert(null))   #This sets the value of ISR to 0xffffffff
    push()                   #Push the ISR to the RX FIFO so the user knows that the code is done
    #irq(0)
    jmp("setup")             #Jump back to setup subroutine to reset the X and Y registers
    
    wrap()


class PulseReader:
    rawPulsesBuf = []
    rawRepeatTimeBuf = []
    rawCommandTimeBuf = []
    pulseTimeout = 2**12-1    #4095
    newRepeatFlag = False
    newCommandFlag = False
    
    def __init__(self, p, f):
        self.smFreq = f
        Pin(p, Pin.IN, Pin.PULL_UP)
        # Instantiate a state machine with the pluses program, at fHz, with set bound to pin
        self.sm = rp2.StateMachine(0, pulses, freq=f, jmp_pin=Pin(p))
        self.sm.active(1)
        Timer(freq=4000, mode=Timer.PERIODIC, callback=self.getPulses)
        
    def convertToMS(self, code):    # Convert to microseconds
        self.rawRepeatTimeBuf = []
        factor = 2 * 1000000 / self.smFreq
        if len(code) == 2:
            for i in code: self.rawRepeatTimeBuf.append(int(i * factor))
            self.newRepeatFlag = True
        else:
            self.rawCommandTimeBuffer = []
            for i in code: self.rawCommandTimeBuf.append(int(i * factor))
            self.newCommandFlag = True

    def getPulses(self, t):
        if self.sm.rx_fifo():
            pulse = self.sm.get()
            #print("0x"+f'{pulse:>00x}')
            if pulse == 0xffffffff:
                self.convertToMS(self.rawPulsesBuf)
                self.rawPulsesBuf = []
            else: self.rawPulsesBuf.append(self.pulseTimeout - pulse)


# https://mosiwi-wiki.readthedocs.io/en/latest/common_resource/nec_communication_protocol/nec_communication_protocol.html
class necDecoder:
    def __init__(self, irPin, commandRepeat: int=False):
        self.necData = 0
        self.commandRepeat = commandRepeat
        self.__DATA_PULSE_WIDTH = 560
        self.pulseReader = PulseReader(irPin, 256000)

    def match(self, val, expectedVal, ALLOWED_DEVIATION=0.20):
        return abs(val-expectedVal) < val * ALLOWED_DEVIATION

    def checkZero(self, p1, p2):
        return self.match(p1, self.__DATA_PULSE_WIDTH) and self.match(p2, self.__DATA_PULSE_WIDTH)

    def checkOne(self, p1, p2):
        return self.match(p1, self.__DATA_PULSE_WIDTH) and self.match(p2, self.__DATA_PULSE_WIDTH * 3)
    
    def decodeCommand(self, rawPulses):
        if len(rawPulses) > 1:
            self.necData = 0
            self.pulseReader.newCommandFlag = False
            if not self.match(rawPulses[0], 9000) and not self.match(rawPulses[1], 4500):
                #print("invalid code - Starting pulse error")
                return False
            
            for i in range(2, len(rawPulses)-1, 2):
                if (rawPulses[i] + rawPulses[i+1]) > self.__DATA_PULSE_WIDTH * 3:
                    if self.checkOne(rawPulses[i], rawPulses[i+1]):
                        self.necData |= 1 << (31 - (int(i/2) - 1))
                    else:
                        #print(f"Invalid Code - One: {rawPulses[i]} {rawPulses[i+1]}")
                        return False
                else:
                    if not self.checkZero(rawPulses[i], rawPulses[i+1]):
                        #print(f"Invalid Code - Zero: {rawPulses[i]} {rawPulses[i+1]}")
                        return False
            return True
        return False
        
    def decode(self):
        if self.pulseReader.newCommandFlag:
            rawPulses = self.pulseReader.rawCommandTimeBuf.copy()
            self.pulseReader.rawCommandTimeBuf = []
            if self.decodeCommand(rawPulses):
                self.err = 0
                return True        
        if self.pulseReader.newRepeatFlag:
            rawRepeat = self.pulseReader.rawRepeatTimeBuf.copy()
            self.pulseReader.rawRepeatTimeBuf = [] 
            if len(rawRepeat):
                self.pulseReader.newCommandFlag = False
                if self.match(rawRepeat[0], 9000) and self.match(rawRepeat[1], 2250):
                    if not self.commandRepeat: self.necData = 0xffffffff # Repeat data
                    return True
        return False



if __name__ == '__main__':
    # Returns 0xffffffff when you hold the key down.
    ir = necDecoder(2)
    # Returns the key value when holding down the key. 
    #ir = necDecoder(2, True)
    
    while True:
        if ir.decode():
            print(f"0x{ir.necData:>00x}")
        time.sleep(0.1)




