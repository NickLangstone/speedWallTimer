#taken from article   https://raspberrypi.stackexchange.com/questions/76667/debouncing-buttons-with-rpi-gpio-too-many-events-detected

import RPi.GPIO as GPIO
import threading


LANE1_FOOT = 12
LANE1_HAND = 13
LANE2_FOOT = 21
LANE2_HAND = 17

class ButtonHandler(threading.Thread):
    def __init__(self, pin, risingfunc, fallingfunc, edge='both', bouncetime=200):
        super().__init__(daemon=True)

        self.edge = edge
        self.risingfunc = risingfunc
        self.fallingfunc = fallingfunc
        self.pin = pin
        self.bouncetime = float(bouncetime)/1000

        self.lastpinval = GPIO.input(self.pin)
        self.lock = threading.Lock()

    def __call__(self, *args):
        if not self.lock.acquire(blocking=False):
            return

        t = threading.Timer(self.bouncetime, self.read, args=args)
        t.start()

    def read(self, *args):
        pinval = GPIO.input(self.pin)

        if (
                ((pinval == 0 and self.lastpinval == 1) and
                 (self.edge in ['falling', 'both'])) or
                ((pinval == 1 and self.lastpinval == 0) and
                 (self.edge in ['rising', 'both']))
        ):
            if ( (pinval == 1 and self.lastpinval == 0) ): # rising 
                self.risingfunc(*args)
            else:
                self.fallingfunc(*args)

        self.lastpinval = pinval
        self.lock.release()


# Usage

def hand_cb(channel):
    print("hand_cb called  " + str(channel) ) 

def footoff_cb(channel):
    print("Footoff_cb called  " + str(channel) ) 

def footon_cb(channel):
    print("Footon_cb called  " + str(channel) ) 

def null_cb(channel):
    #no op callback
    print("null_cb")


# Use GPIO numbers not pin numbers
GPIO.setmode(GPIO.BCM)
GPIO.setup(LANE1_HAND, GPIO.IN, pull_up_down=GPIO.PUD_UP)
cb = ButtonHandler(LANE1_HAND, hand_cb, null_cb,  edge='rising', bouncetime=1)
cb.start()
GPIO.add_event_detect(LANE1_HAND, GPIO.RISING, callback=cb)


GPIO.setup(LANE1_FOOT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
cb2 = ButtonHandler(LANE1_FOOT, footon_cb, footoff_cb, edge='both', bouncetime=10)
cb2.start()
GPIO.add_event_detect(LANE1_FOOT, GPIO.RISING, callback=cb2)


GPIO.setup(LANE2_HAND, GPIO.IN, pull_up_down=GPIO.PUD_UP)
cb = ButtonHandler(LANE2_HAND, hand_cb, null_cb, edge='rising', bouncetime=1)
cb.start()
GPIO.add_event_detect(LANE2_HAND, GPIO.RISING, callback=cb)


GPIO.setup(LANE2_FOOT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
cb2 = ButtonHandler(LANE2_FOOT, footon_cb, footoff_cb, edge='both', bouncetime=10)
cb2.start()
GPIO.add_event_detect(LANE2_FOOT, GPIO.BOTH, callback=cb2)

message = input("Press enter to quit\n\n") # Run until someone presses enter



#another article   https://www.raspberrypi.org/forums/viewtopic.php?t=137484
#http://abyz.me.uk/rpi/pigpio/python.html#callback


