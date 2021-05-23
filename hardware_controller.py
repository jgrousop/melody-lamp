"""Control the Raspberry pi hardware.
The hardware controller handles all interaction with the raspberry pi
hardware to turn the lights on and off.
"""

try:  # RPi.GPIO only works on the Raspberry Pi.
    import RPi.GPIO as GPIO
except RuntimeError:
    print('Error importing RPi.GPIO! This is probably because you need superuser privileges.')
from main import Lightshow

# event handlers ===
def next_song(channel):
    Lightshow.next_song()

def prev_song(channel):
    Lightshow.prev_song()

def pause_play(channel):
    Lightshow.pause_play()

class Pi(object):
    def __init__(self):
        self.next_pin = 19
        self.prev_pin = 21
        self.pause_pin = 23

        self.setup()
    
    def setup(self):
        """create event detect on input pins for button presses"""
        GPIO.setmode(GPIO.BOARD)  # RPi.GPIO only works on the Raspberry Pi.
        mode = GPIO.getmode()
        GPIO.setwarnings(False)
        GPIO.setup(self.next_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)    # set as input (button)  
        GPIO.setup(self.prev_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)    # set as input (button)  
        GPIO.setup(self.pause_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)    # set as input (button)  
        GPIO.add_event_detect(self.next_pin, GPIO.RISING, callback=next_song, bouncetime=200)
        GPIO.add_event_detect(self.prev_pin, GPIO.RISING, callback=prev_song, bouncetime=200)
        GPIO.add_event_detect(self.pause_pin, GPIO.RISING, callback=pause_play, bouncetime=200)

class ShiftRegister(object):
    def __init__(self, dataPin, serialClock, latchPin,  outEnable):
        self.dataPin = dataPin
        self.serialClock = serialClock
        self.latchPin = latchPin
        self.outEnable = outEnable

        self.setup()

    def setup(self):
        GPIO.setmode(GPIO.BOARD)  # RPi.GPIO only works on the Raspberry Pi.
        mode = GPIO.getmode()
        GPIO.setwarnings(False)
        
        GPIO.setup(self.dataPin, GPIO.OUT)
        GPIO.setup(self.serialClock, GPIO.OUT)
        GPIO.setup(self.latchPin, GPIO.OUT)
        GPIO.setup(self.outEnable, GPIO.OUT)
        
        GPIO.output(self.dataPin, GPIO.LOW)
        GPIO.output(self.serialClock, GPIO.LOW)
        GPIO.output(self.latchPin, GPIO.LOW)
        GPIO.output(self.outEnable, GPIO.LOW)
        self.clear()

    def clear(self):
        """ clears all the LEDs by pulsing the serial clock 8 times and the latch pin once. """
        GPIO.output(self.dataPin, GPIO.LOW)
        for x in range(0, 8):  # Clears out all the values currently in the register
            GPIO.output(self.serialClock, GPIO.LOW)
            GPIO.output(self.serialClock, GPIO.HIGH)
            GPIO.output(self.serialClock, GPIO.LOW)

        self.latch()

    def latch(self):
        """ pulses the latch pin for writing to the storage register from the shift register"""
        GPIO.output(self.latchPin, GPIO.LOW)
        GPIO.output(self.latchPin, GPIO.HIGH)
        GPIO.output(self.latchPin, GPIO.LOW)

    def output(self):
        pass
        GPIO.output(self.outEnable, GPIO.HIGH)

    def inputBit(self, inputValue):
        """
        sets the data pin to the correct bit value then pulses the serial clock pin to shift in the bit.
        """
        GPIO.output(self.dataPin, inputValue)
        
        GPIO.output(self.serialClock, GPIO.LOW)
        GPIO.output(self.serialClock, GPIO.HIGH)
        GPIO.output(self.serialClock, GPIO.LOW)

    def readBitList(self, bit_list):
        """reads in a string of 1's and 0's and shifts the bits into the shift register."""
        for element in bit_list:
            self.inputBit(int(element))
        self.latch()
        self.output()
