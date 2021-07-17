"""Control the Raspberry pi hardware.
The hardware controller handles all interaction with the raspberry pi
hardware to turn the lights on and off.
"""
from gpiozero import DigitalOutputDevice


class ShiftRegister(object):
    def __init__(self, dataPin, serialClock, latchPin,  outEnable):
        self.dataPin = dataPin
        self.serialClock = serialClock
        self.latchPin = latchPin
        self.outEnable = outEnable
        self.shift_data = None
        self.shift_clock = None
        self.shift_latch = None
        self.shift_out = None

        self.setup()

    def setup(self):
        
        self.shift_data = DigitalOutputDevice(self.dataPin) # all are low to begin with
        self.shift_clock = DigitalOutputDevice(self.serialClock)
        self.shift_latch = DigitalOutputDevice(self.latchPin)
        self.shift_out = DigitalOutputDevice(self.outEnable)

        self.clear()

    def clear(self):
        """ clears all the LEDs by pulsing the serial clock 8 times and the latch pin once. """
        self.shift_data.off()
        for x in range(0, 8):  # Clears out all the values currently in the register
            self.shift_clock.off()
            self.shift_clock.on()
            self.shift_clock.off()

        self.latch()

    def latch(self):
        """ pulses the latch pin for writing to the storage register from the shift register"""
        self.shift_latch.off()
        self.shift_latch.on()
        self.shift_latch.off()

    def output(self):
        self.shift_out.on()

    def inputBit(self, inputValue):
        """
        sets the data pin to the correct bit value then pulses the serial clock pin to shift in the bit.
        """
        self.shift_data.off()
        if inputValue == 1: self.shift_data.on()
        
        self.shift_clock.off()
        self.shift_clock.on()
        self.shift_clock.off()

    def readBitList(self, bit_list):
        """reads in a string of 1's and 0's and shifts the bits into the shift register."""
        for element in bit_list:
            self.inputBit(int(element))
        self.latch()
        self.output()
