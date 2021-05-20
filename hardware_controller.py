"""Control the Raspberry pi hardware.
The hardware controller handles all interaction with the raspberry pi
hardware to turn the lights on and off.
"""

# try:  # RPi.GPIO only works on the Raspberry Pi.
#     import RPi.GPIO as GPIO
# except RuntimeError:
#     print('Error importing RPi.GPIO! This is probably because you need superuser privileges.')
import pygame

# event handlers ===
def next_song(channel):
    print('inside the next_channel event handler')


def prev_song(channel):
    print('inside the prev_channel event handler')


def pause_play(channel):
    print('inside pause_play event handler')

    if paused:
        print('starting to play after being paused')
        pygame.mixer.music.play()
        paused = False
    else:
        print('pausing song...')
        pygame.mixer.music.pause()
        paused = True


class ShiftRegister(object):
    def __init__(self, dataPin, serialClock, latchPin,  outEnable):
        self.dataPin = dataPin
        self.serialClock = serialClock
        self.latchPin = latchPin
        self.outEnable = outEnable

        self.setup()

    def setup(self):
        # GPIO.setmode(GPIO.BOARD)  # RPi.GPIO only works on the Raspberry Pi.
        # mode = GPIO.getmode()
        # GPIO.setwarnings(False)
        #
        # GPIO.setup(self.dataPin, GPIO.OUT)
        # GPIO.setup(self.serialClock, GPIO.OUT)
        # GPIO.setup(self.latchPin, GPIO.OUT)
        # GPIO.setup(self.outEnable, GPIO.OUT)
        #
        # GPIO.output(self.dataPin, GPIO.LOW)
        # GPIO.output(self.serialClock, GPIO.LOW)
        # GPIO.output(self.latchPin, GPIO.LOW)
        # GPIO.output(self.outEnable, GPIO.LOW)
        self.clear()

    def clear(self):
        """ clears all the LEDs by pulsing the serial clock 8 times and the latch pin once. """
        # GPIO.output(self.dataPin, GPIO.LOW)
        # for x in range(0, 8):  # Clears out all the values currently in the register
        #     GPIO.output(self.serialClock, GPIO.LOW)
        #     GPIO.output(self.serialClock, GPIO.HIGH)
        #     GPIO.output(self.serialClock, GPIO.LOW)

        self.latch()

    def latch(self):
        """ pulses the latch pin for writing to the storage register from the shift register"""
        # GPIO.output(self.latchPin, GPIO.LOW)
        # GPIO.output(self.latchPin, GPIO.HIGH)
        # GPIO.output(self.latchPin, GPIO.LOW)

    def output(self):
        pass
        # GPIO.output(self.outEnable, GPIO.HIGH)

    def inputBit(self, inputValue):
        """
        sets the data pin to the correct bit value then pulses the serial clock pin to shift in the bit.
        """
        # GPIO.output(self.dataPin, inputValue)
        #
        # GPIO.output(self.serialClock, GPIO.LOW)
        # GPIO.output(self.serialClock, GPIO.HIGH)
        # GPIO.output(self.serialClock, GPIO.LOW)

    def readBitList(self, bit_list):
        """reads in a string of 1's and 0's and shifts the bits into the shift register."""
        # for element in bit_list:
        #     self.inputBit(int(element))
        # self.latch()
        # self.output()
