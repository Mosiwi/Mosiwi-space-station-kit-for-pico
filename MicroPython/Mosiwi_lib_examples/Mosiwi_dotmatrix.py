"""
Programmer: Mosiwi
Date: 29/08/2023
Wiki: https://mosiwi-wiki.readthedocs.io/en/latest/common_resource/nec_communication_protocol/nec_communication_protocol.html
https://docs.micropython.org/en/latest/rp2/quickref.html
Module containing code to run a stepper motor via the ULN2003 driver board.
"""
import utime as time
from machine import I2C, Pin

class HT16K33:
    """
    A simple, generic driver for the I2C-connected Holtek HT16K33 controller chip. This release supports MicroPython 
    Version:    0.0.1
    Bus:        I2C
    Author:     Mosiwi
    License:    MIT
    Copyright:  2023
    """

    # *********** CONSTANTS **********
    HT16K33_GENERIC_DISPLAY_ON = 0x81
    HT16K33_GENERIC_DISPLAY_OFF = 0x80
    HT16K33_GENERIC_SYSTEM_ON = 0x21
    HT16K33_GENERIC_SYSTEM_OFF = 0x20
    HT16K33_GENERIC_DISPLAY_ADDRESS = 0x00
    HT16K33_GENERIC_CMD_BRIGHTNESS = 0xE0
    HT16K33_GENERIC_CMD_BLINK = 0x81

    # *********** PRIVATE PROPERTIES **********
    i2c = None
    address = 0
    brightness = 15
    flash_rate = 0

    # *********** CONSTRUCTOR **********
    def __init__(self, i2c, i2c_address):
        assert 0x00 <= i2c_address < 0x80, "ERROR - Invalid I2C address in HT16K33()"
        self.i2c = i2c
        self.address = i2c_address
        self.power_on()

    # *********** PUBLIC METHODS **********
    def set_blink_rate(self, rate=0):
        """
        Set the display's flash rate.
        Only four values (in Hz) are permitted: 0, 1, 2, and 0.5

        Args:
            rate (int): The chosen flash rate. Default: 0Hz (no flash).
        """
        assert rate in (0, 0.5, 1, 2), "ERROR - Invalid blink rate set in set_blink_rate()"
        self.blink_rate = rate & 0x03
        self._write_cmd(self.HT16K33_GENERIC_CMD_BLINK | rate << 1)

    def set_brightness(self, brightness=1):
        """
        Set the display's brightness (ie. duty cycle).
        Brightness values range from 0 (dim, but not off) to 15 (max. brightness).

        Args:
            brightness (int): The chosen flash rate. Default: 15 (100%).
        """
        if brightness < 0 or brightness > 15: brightness = 15
        self.brightness = brightness
        self._write_cmd(self.HT16K33_GENERIC_CMD_BRIGHTNESS | brightness)

    def draw(self):
        """
        Writes the current display buffer to the display itself.
        Call this method after updating the buffer to update the LED itself.
        """
        self._render()

    def update(self):
        """
        Alternative for draw() for backwards compatibility
        """
        self._render()

    def clear(self):
        """
        Clear the buffer.

        Returns: The instance (self)
        """
        for i in range(0, len(self.buffer)): self.buffer[i] = 0x00
        return self

    def power_on(self):
        """
        Power on the controller and display.
        """
        self._write_cmd(self.HT16K33_GENERIC_SYSTEM_ON)
        self._write_cmd(self.HT16K33_GENERIC_DISPLAY_ON)

    def power_off(self):
        """
        Power on the controller and display.
        """
        self._write_cmd(self.HT16K33_GENERIC_DISPLAY_OFF)
        self._write_cmd(self.HT16K33_GENERIC_SYSTEM_OFF)

    # ********** PRIVATE METHODS **********
    def _render(self):
        """
        Write the display buffer out to I2C
        """
        buffer = bytearray(len(self.buffer) + 1)
        buffer[1:] = self.buffer
        buffer[0] = 0x00
        self.i2c.writeto(self.address, bytes(buffer))

    def _write_cmd(self, byte):
        """
        Writes a single command to the HT16K33. A private method.
        """
        self.i2c.writeto(self.address, bytes([byte]))

        
class HT16K33Matrix(HT16K33):
    """
    Micro/Circuit Python class for the Adafruit 8x16 monochrome LED matrix backpack.
    Version:    0.0.1
    Bus:        I2C
    Author:     Mosiwi
    License:    MIT
    Copyright:  2023
    """

    # *********** CONSTANTS **********
    CHARSET = [
        b"\x00\x00",              # space - Ascii 32
        b"\x5f",                  # !
        b"\x03\x00\x03",          # "
        b"\x24\x7e\x24\x7e\x24",  # #
        b"\x24\x2a\x7f\x2a\x12",  # $
        b"\x63\x13\x08\x64\x63",  # %
        b"\x36\x49\x56\x20\x50",  # &
        b"\x03",                  # '
        b"\x3e\x41",              # (
        b"\x41\x3e",              # )
        b"\x08\x3e\x1c\x3e\x08",  # *
        b"\x08\x08\x3e\x08\x08",  # +
        b"\x60\xe0",              # ,
        b"\x08\x08\x08\x08",      # -
        b"\x06\x06",              # .
        b"\x20\x10\x80\x04\x02",  # /
        b"\x3e\x51\x49\x45\x3e",  # 0 - Ascii 48
        b"\x42\x7f\x40",          # 1
        b"\x42\x61\x51\x49\x46",  # 2
        b"\x22\x49\x49\x49\x36",  # 3
        b"\x18\x14\x12\x7f\x10",  # 4
        b"\x27\x45\x45\x45\x39",  # 5
        b"\x38\x4c\x4a\x49\x30",  # 6
        b"\x01\x01\x79\x05\x03",  # 7
        b"\x36\x49\x49\x49\x36",  # 8
        b"\x06\x49\x29\x19\x0e",  # 9
        b"\x36\x36",              # : - Ascii 58
        b"\x6c\xec",              # ;
        b"\x08\x14\x22\x41",      # <
        b"\x14\x14\x14\x14\x14",  # =
        b"\x41\x22\x14\x08",      # >
        b"\x02\x01\x59\x09\x06",  # ?
        b"\x3e\x41\x5d\x55\x5e",  # @
        b"\x7e\x09\x09\x09\x7e",  # A - Ascii 65
        b"\x7f\x49\x49\x49\x36",  # B
        b"\x3e\x41\x41\x41\x22",  # C
        b"\x7f\x41\x41\x22\x1c",  # D
        b"\x7f\x49\x49\x49\x41",  # E
        b"\x7f\x09\x09\x09\x01",  # F
        b"\x3e\x41\x49\x49\x3a",  # G
        b"\x7f\x08\x08\x08\x7f",  # H
        b"\x41\x7f\x41",          # I
        b"\x20\x40\x41\x3f\x01",  # J
        b"\x7f\x08\x14\x22\x41",  # K
        b"\x7f\x40\x40\x40",      # L
        b"\x7f\x02\x1c\x02\x7f",  # M
        b"\x7f\x02\x04\x08\x7f",  # N
        b"\x3e\x41\x41\x41\x3e",  # O
        b"\x7f\x09\x09\x09\x06",  # P
        b"\x3e\x41\x51\x21\x5e",  # Q
        b"\x7f\x09\x19\x29\x46",  # R
        b"\x26\x49\x49\x49\x32",  # S
        b"\x01\x01\x7f\x01\x01",  # T
        b"\x3f\x40\x40\x40\x3f",  # U
        b"\x1f\x20\x40\x20\x1f",  # V
        b"\x7f\x20\x1c\x20\x7f",  # W
        b"\x63\x14\x08\x14\x63",  # X
        b"\x03\x04\x78\x04\x03",  # Y
        b"\x61\x51\x49\x45\x43",  # Z - Ascii 90
        b"\x7f\x41\x41",          # [
        b"\x03\x04\x08\x10\x60",  # \
        b"\x41\x41\x7f",          # ]
        b"\x04\x02\x01\x02\x04",  # ^
        b"\x40\x40\x40\x40\x40",  # _
        b"\x03\x07",              # '
        b"\x20\x54\x54\x78",      # a - Ascii 97
        b"\x7f\x48\x48\x30",      # b
        b"\x38\x44\x44\x44",      # c
        b"\x30\x48\x48\x7f",      # d
        b"\x38\x54\x54\x08",      # e
        b"\x08\x7e\x09\x01",      # f
        b"\x18\xa4\xa4\x7c",      # g
        b"\x7f\x08\x08\x70",      # h
        b"\x7a",                  # i
        b"\x20\x44\x3d",          # j
        b"\x7f\x10\x28\x44",      # k
        b"\x3f\x40",              # l
        b"\x7c\x04\x18\x04\x78",  # m
        b"\x7c\x04\x04\x78",      # n
        b"\x38\x44\x44\x38",      # o
        b"\xfc\x24\x24\x18",      # p
        b"\x18\x24\x24\xfc",      # q
        b"\x44\x78\x04\x08",      # r
        b"\x48\x54\x54\x20",      # s
        b"\x08\x3c\x48\x20",      # t
        b"\x3c\x40\x40\x7c",      # u
        b"\x1c\x20\x40\x20\x1c",  # v
        b"\x3c\x40\x30\x40\x3c",  # w
        b"\x44\x28\x10\x28\x44",  # x
        b"\x9c\xa0\x60\x3c",      # y
        b"\x64\x54\x54\x4c",      # z - Ascii 122
        b"\x08\x36\x41\x41",      # {
        b"\xee",                  # |
        b"\x41\x41\x36\x08",      # }
        b"\x02\x01\x02\x01",      # ~
        b"\x06\x09\x09\x06"       # Degrees sign - Ascii 127
    ]

    # ********** PRIVATE PROPERTIES **********

    width = 16
    height = 8
    def_chars = None
    rotation_angle = 0
    is_rotated = False
    is_inverse = False

    # *********** CONSTRUCTOR **********
    def __init__(self, i2c, i2c_address=0x70):
        self.buffer = bytearray(self.width)
        self.def_chars = []
        for i in range(32): self.def_chars.append(b"\x00")
        super(HT16K33Matrix, self).__init__(i2c, i2c_address)

    def set_inverse(self):
        """
        Inverts the ink colour of the display.
        Returns: The instance (self)
        """
        self.is_inverse = not self.is_inverse
        for i in range(self.width):
            self.buffer[i] = (~ self.buffer[i]) & 0xFF
        return self

    def set_icon(self, glyph):
        """
        Displays a custom character on the matrix.
        Args:
            glyph (array) 1-16 8-bit values defining a pixel image. The data is passed as columns
                          0 through 7, left to right. Bit 0 is at the top, bit 7 at the bottom
        Returns: The instance (self)
        """
        # Bail on incorrect values
        length = len(glyph)
        assert 0 < length <= self.width, "ERROR - Invalid glyph set in set_icon()"

        for i in range(length):
            a = i
            self.buffer[a] = glyph[i] if self.is_inverse is False else ((~ glyph[i]) & 0xFF)
        return self

    def set_character(self, ascii_value=32, centre=False):
        """
        Display a single character specified by its Ascii value on the matrix.
        Args:
            ascii_value (integer) Character Ascii code. Default: 32 (space)
            centre (bool)         Whether the icon should be displayed centred on the screen. Default: False

        Returns: The instance (self)
        """
        # Bail on incorrect values
        assert 0 <= ascii_value < 128, "ERROR - Invalid ascii code set in set_character()"

        glyph = None
        if ascii_value < 32:
            # A user-definable character has been chosen
            glyph = self.def_chars[ascii_value]
        else:
            # A standard character has been chosen
            ascii_value -= 32
            if ascii_value < 0 or ascii_value >= len(self.CHARSET): ascii_value = 0
            glyph = self.CHARSET[ascii_value]
        return self.set_icon(glyph)

    def scroll_text(self, the_line, speed=0.1):
        """
        Scroll the specified line of text leftwards across the display.
        Args:
            the_line (string) The string to display
            speed (float)     The delay between frames
        Returns: The instance (self)
        """

        # Bail on incorrect values
        assert len(the_line) > 0, "ERROR - Invalid string set in scroll_text()"

        # Calculate the source buffer size
        length = 0
        for i in range(0, len(the_line)):
            asc_val = ord(the_line[i])
            if asc_val < 32: glyph = self.def_chars[asc_val]
            else: glyph = self.CHARSET[asc_val - 32]
            length += len(glyph)
            if asc_val > 32: length += 1
        src_buffer = bytearray(length)

        # Draw the string to the source buffer
        row = 0
        for i in range(0, len(the_line)):
            asc_val = ord(the_line[i])
            if asc_val < 32: glyph = self.def_chars[asc_val]
            else: glyph = self.CHARSET[asc_val - 32]
            for j in range(0, len(glyph)):
                src_buffer[row] = glyph[j] if self.is_inverse is False else ((~ glyph[j]) & 0xFF)
                row += 1
            if asc_val > 32: row += 1
        assert row == length, "ERROR - Mismatched lengths in scroll_text()"

        # Finally, animate the line
        cursor = 0
        while True:
            a = cursor
            for i in range(0, self.width):
                self.buffer[i] = src_buffer[a];
                a += 1
            self.draw()
            cursor += 1
            if cursor > length - self.width: break
            time.sleep(speed)

    def define_character(self, glyph, char_code=0):
        """
        Set a user-definable character for later use.
        Args:
            glyph (bytearray)   1-16 8-bit values defining a pixel image. The data is passed as columns,
                                with bit 0 at the top and bit 7 at the bottom 
            char_code (integer) Character's ID Ascii code 0-31. Default: 0
        Returns: The instance (self)
        """
        # Bail on incorrect values
        assert 0 < len(glyph) <= self.width, "ERROR - Invalid glyph set in define_character()"
        assert 0 <= char_code < 32, "ERROR - Invalid character code set in define_character()"

        self.def_chars[char_code] = glyph
        return self

    def plot(self, x, y, ink=1, xor=False):
        """
        Plot a point on the matrix. (0,0) is bottom left as viewed.
        Args:
            x (integer)   X co-ordinate (0 - 15) left to right
            y (integer)   Y co-ordinate (0 - 7) top to bottom
            ink (integer) Pixel color: 1 = 'white', 0 = black. NOTE inverse video mode reverses this. Default: 1
            xor (bool)    Whether an underlying pixel already of color ink should be inverted. Default: False
        Returns: The instance (self)
        """
        # Bail on incorrect values
        assert (0 <= x < self.width) and (0 <= y < self.height), "ERROR - Invalid coordinate set in plot()"

        if ink not in (0, 1): ink = 1
        if ink == 1:
            if self.is_set(x ,y) and xor:
                self.buffer[x] ^= (1 << y)
            else:
                if self.buffer[x] & (1 << y) == 0: self.buffer[x] |= (1 << y)
        else:
            if not self.is_set(x ,y) and xor:
                self.buffer[x] ^= (1 << y)
            else:
                if self.buffer[x] & (1 << y) != 0: self.buffer[x] &= ~(1 << y)
        return self

    def is_set(self, x, y):
        """
        Indicate whether a pixel is set.
        Args:
            x (int) X co-ordinate left to right
            y (int) Y co-ordinate bottom to top
        Returns: Whether the pixel is set (True) or not (False)
        """
        # Bail on incorrect values
        assert (0 <= x < self.width) and (0 <= y < self.height), "ERROR - Invalid coordinate set in is_set()"

        bit = (self.buffer[x] >> y) & 1
        return True if bit > 0 else False

    def draw(self):
        """
        Takes the contents of _buffer and writes it to the LED matrix.
        NOTE Overrides the parent method.
        """
        new_buffer = bytearray(len(self.buffer))
        for i in range(self.width): new_buffer[i] = self.buffer[i]
        draw_buffer = bytearray(17)
        for i in range(len(new_buffer)): draw_buffer[i + 1] = new_buffer[i]
        self.i2c.writeto(self.address, bytes(draw_buffer))

    def _fill(value=0xFF):
        """
        Fill the buffer, column by column with the specified byte value
        """
        value &= 0xFF
        for i in range(self.width): self.buffer[i] = value
        
        
        
# CONSTANTS
PAUSE = 3

# START
if __name__ == '__main__':
    # Delete or comment out all but one of the following i2c instantiations
    i2c = I2C(0, scl=Pin(5), sda=Pin(4))    # Raspberry Pi Pico

    display = HT16K33Matrix(i2c)
    display.set_brightness(1)
    
    # Draw a custom icon on the LED
    icon = b"\x00\x00\x00\x0e\x1f\x3f\x7e\xfc\x7e\x3f\x1f\x0e\x00\x00\x00\x00"
    display.set_icon(icon).draw()
    time.sleep(PAUSE)

    # Clear the LED
    display.clear().draw()

    # Record two custom icons using 'define_character()'
    icon = b"\x00\x00\x00\x0c\x02\x02\x4c\x80\x80\x4c\x02\x02\x0c\x00\x00\x00"
    display.define_character(icon, 0)
    icon = b"\x00\x00\x00\x0c\x02\x42\xac\xa0\xa0\xac\x42\x02\x0c\x00\x00\x00"
    display.define_character(icon, 1)

    # Display scrolling text
    text = "   Mosiwi        "
    display.scroll_text(text)
    time.sleep(PAUSE)
    
    # Show the previously stored custom icon then Blink the LED
    display.set_character(0, True).draw()
    display.set_blink_rate(1)
    time.sleep(PAUSE)

    # Inverse the pixes
    display.set_inverse().draw()
    time.sleep(PAUSE)

    # Inverse the pixels (to revert)
    display.set_inverse().draw()
    time.sleep(PAUSE)
    
    # Clear and stop blinking
    display.clear().draw()
    display.set_blink_rate(0)
    
    # Plot an X
    for i in range(4):
        display.plot(i, i).plot(7 - i, i).plot(i, 7 - i).plot(7 - i, 7 - i)
    for i in range(4):
        display.plot(i + 8, 7 - i).plot(15 - i, i).plot(i + 8, i).plot(15 - i, 7 - i)
    display.draw()
    time.sleep(PAUSE)
    assert (display.is_set(0, 0) is True) and (display.is_set(0, 1) is False)
    display.clear().draw()

            
