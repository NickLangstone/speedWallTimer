from tkinter import *
import time
from laneTimer import *
import random
from datetime import datetime

from playtones import *

#taken from article   https://raspberrypi.stackexchange.com/questions/76667/debouncing-buttons-with-rpi-gpio-too-many-events-detected
import RPi.GPIO as GPIO
import threading

LANE1_FOOT = 12
LANE1_HAND = 13
LANE2_FOOT = 21
LANE2_HAND = 17

lane1 = LaneTimer("Lane 1")
lane2 = LaneTimer("Lane 2")

# TIMER_STATE will help determine if the person false starts
TIMER_STATE = 0


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
    if channel == LANE1_HAND:
       lane1.stop()
    if channel == LANE2_HAND:
       lane2.stop()

def footoff_cb(channel):
    print("Footoff_cb called  " + str(channel) ) 
    if TIMER_STATE == 6 and channel == LANE1_FOOT: # Start
       lane1.reaction()
    if TIMER_STATE == 0 and channel == LANE1_FOOT: # Foot off - return to idel
       lane1.setReady(0)
    if TIMER_STATE == 6 and channel == LANE2_FOOT: # Start
       lane2.reaction()
    if TIMER_STATE == 0 and channel == LANE2_FOOT: # Foot off - return to idel
       lane2.setReady(0)
      


def footon_cb(channel):
    print("Footon_cb called  " + str(channel) ) 
    if channel == LANE1_FOOT:
       lane1.ready()
    if channel == LANE2_FOOT:
       lane2.ready()

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


################################################################
#
#    Start of display logic
#


window = Tk()

window.title("Auckland Sport Climbing Speed Climbing Timing App")
window.geometry('800x400')
window.geometry("{0}x{1}+0+0".format(window.winfo_screenwidth(), window.winfo_screenheight() - 500))




def printTxt(txt, x, y, size, color):
    lbl1=Label(window, text=txt, font=("Arial Bold", size ),foreground=color) 
    lbl1.place(x=x, y=y)


def printSmallTxt(txt, x, y, size, color):
    lbl1=Label(window, text=txt, font=("Arial Bold", size),foreground=color) 
    lbl1.place(x=x, y=y)


LANE1_TIME_X = 730
LANE2_TIME_X = 730
LANE1_Y      = 50
LANE2_Y      = 250


printTxt("Lane 1:", 50, LANE1_Y,120, "black")
printTxt("Lane 2:", 50, LANE2_Y,120, "black")

lane1_colour = "black"
lane2_colour = "black"

window.update_idletasks()
window.update()

run =1
while run:

  if lane1.getReady() == 0:
     lane1_colour = "black"
  if lane2.getReady() == 0:
     lane2_colour = "black"

  if lane1.getReady() == 1:
     lane1_colour = "yellow"
  if lane2.getReady() == 1:
     lane2_colour = "yellow"

  if lane1.getReady() == 3 and \
         lane1.getEndTimer() < lane2.getEndTimer():
     lane1_colour = "green"
  if lane2.getReady() == 3 and \
         lane1.getEndTimer() > lane2.getEndTimer():
     lane2_colour = "green"


  if lane1.getReady() == 9:  # False start
     lane1_colour = "red"
  if lane2.getReady() == 9:  # False start
     lane2_colour = "red"


  printTxt(lane1.getTimerDisplay() , LANE1_TIME_X, LANE1_Y, 140, lane1_colour)
  printTxt(lane2.getTimerDisplay() , LANE2_TIME_X, LANE2_Y, 140, lane2_colour)

#  printSmallTxt("Lane 1 Ready : " + str(lane1.getReady()) + "  Lane 2 Ready : " \
#                 + str(lane2.getReady()) + "    - Timer state: " + str(TIMER_STATE), 270, 420, 24, "black")
  printSmallTxt( "Lane 1 reaction Time : " + lane1.getReactionTimerDisplay() \
                     + "  Lane 2 reaction Time : " + lane2.getReactionTimerDisplay(), 20,500, 36,"black")
  
  window.update_idletasks()
  window.update()
  time.sleep(0.005)

       # Climbers putting foot on starting pad and getting ready
       # expect to go in and out of thi state a lot
  if (TIMER_STATE == 0 and ( lane1.getReady() == 1 and lane2.getReady() == 1)) :
      # start the start sequence
      TIMER_STATE = 1  # Begining of start sequence
      lane1.reset()
      lane2.reset()
      time.sleep(1.5)  # 1 second delay
      TIMER_STATE=4
      continue

		# Either person takes foot off
  if (lane1.getReady() == 9 or lane2.getReady() == 9):
      TIMER_STATE = 0
      continue
     

  if TIMER_STATE == 4 :  # Starting Sequence
      TIMER_STATE=6  # Clmbing
      # Play the start tones
      playtone(data400hz)
      time.sleep(1)
      playtone(data400hz)
      time.sleep(1)
      playtone(data600hz)
      # after start tone
      lane1.start()
      lane2.start()
      TIMER_STATE=6  # Clmbing
      continue

  if (lane1.getReady() == 3 and lane2.getReady() == 3):   # BOTH of the climbers has completed the climb
      TIMER_STATE = 0
      time.sleep(1)
      continue

  if (lane1.getReady() == 3 or lane2.getReady() == 3):   # One of the climbers has completed the climb
      TIMER_STATE = 0
      continue
      

