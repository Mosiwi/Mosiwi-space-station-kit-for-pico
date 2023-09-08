"""
Programmer: Mosiwi
Date: 29/08/2023
Wiki: https://mosiwi-wiki.readthedocs.io/en/latest/common_resource/nec_communication_protocol/nec_communication_protocol.html
https://docs.micropython.org/en/latest/rp2/quickref.html
Module containing code to run a stepper motor via the ULN2003 driver board.
"""
import time, utime
from machine import Pin
from machine import Timer

__HALF_STEP_TABLE = [
    [0, 0, 0, 1],
    [0, 0, 1, 1],
    [0, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [1, 1, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 1],
]

__FULL_STEP_TABLE = [
 [1, 0, 1, 0],
 [0, 1, 1, 0],
 [0, 1, 0, 1],
 [1, 0, 0, 1]
]

class ULN2003(object):
    """
    Class representing an ULN2003 stepper driver.
    The default settings are made to work with the 28byj-48 5V DC stepper motor.
    """
    pins = list()
    steps_pr_rotation = 0
    step_table = list()
    steps_sum = 1
    direction = 1
    index = 0

    def __init__(self, pins: list[int], half_step: bool=True, steps_pr_rotation: int=None):
        """
        - pins : list[int]
          A list of integers representing the IO pins used to control the stepper motor.
        - half_step : bool (Default: True)
          Should movements be in half-steps or whole-steps.
        - interval : float (Default: 0.001)
          Number of seconds to sleep between each sub-step. Smaller values give faster movement.
          If this becomes too low, the motor might just stop moving.
        - full_rotation : int (Default: None)
          How many steps are in a full rotation. If set to None, a default based on the 28byj-48.
        """

        # Create GPIO pin objects.
        self.pins = [Pin(p, Pin.OUT, 0) for p in pins]

        # Set the correct step table.
        self.step_table = __HALF_STEP_TABLE if half_step else __FULL_STEP_TABLE

        # Set how many steps in a rotation.
        # The step Angle is 5.625° and the reduction ratio is 1/64
        # 4096 = 360/5.625 * 64
        self.steps_pr_rotation = steps_pr_rotation if steps_pr_rotation else 4096

        # Set the timer interrupt frequency to 800hz for stepper motor.
        Timer(freq=800, mode=Timer.PERIODIC, callback=self._step)
    
    # Interrupt function of timer
    def _step(self, t):
        if self.steps_sum > 0:
            self.index = self.index + 1  if self.direction == 1 else self.index - 1
            if self.direction == -1 and self.index < 0: self.index = len(self.step_table) - 1
            if self.direction == 1 and self.index > len(self.step_table) - 1: self.index = 0
            state = self.step_table[self.index]
            for p in range(4):
                self.pins[p].value(state[p])
            self.steps_sum -= 1
            #print(self.index)
        else: self.__reset()


    def __reset(self):
        """ Set all output pins to 0. """
        for pin in self.pins:
            pin.value(0)

    def move(self, steps: int=0, direction: int=1):
        """
        Move the stepper motor a specific number of steps in one direction.
        - steps : int (Default: 0)
          How many steps to move in the specified direction.
        - direction : int (Default: 1)
          The direction to move. Must be either: 1 for forward, or -1 for backwards.
        """
        self.steps_sum = steps
        self.direction = direction

    def degree(self, degree: int=0, direction: int=1):
        """
        - degree : int (Default: 0)
          How many degrees to move in the specified direction.
        - direction : int (Default: 1)
          The direction to move. Must be either: 1 for forward, or -1 for backwards.
        """
        self.move(self.steps_pr_rotation/360*degree, direction)


if __name__ == '__main__':
    stepper = ULN2003([6,7,8,9])
    '''
    stepper.move(4096, 1)
    while stepper.steps_sum > 0: pass
    stepper.move(4096, -1)
    while stepper.steps_sum > 0: pass
    '''

    while True:
        stepper.degree(360, 1)
        while stepper.steps_sum > 0: pass
        stepper.degree(360, -1)
        while stepper.steps_sum > 0: pass

