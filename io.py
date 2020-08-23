import RPi.GPIO as GPIO
import time
from datetime import datetime
 
# Use GPIO numbers not pin numbers
GPIO.setmode(GPIO.BCM)


GPIO.setwarnings(False) # Ignore warning for now 
#GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
# set up the GPIO channels - one input and one output
GPIO.setup(17, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(27, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)


lane1_state = 0
lane2_state = 0


def button_callback(channel):
    now = datetime.now()
#    time.sleep(0.1) # 
    lane1 = GPIO.input(17)
    lane2 = GPIO.input(27)
    global lane1_state
    global lane2_state
    if lane1_state != lane1:
        print("lane 1 changed")
        print("Status of lanes   1: " + str(lane1) + "  2:  " + str(lane2) + " event channel : " + str(channel)  )
        lane1_state = lane1
    if lane2_state !=  lane2:
        print("lane 2 changed")
        print("Status of lanes   1: " + str(lane1) + "  2:  " + str(lane2) + " event channel : " + str(channel)  )
        lane2_state = lane2 
	
    #print("Status of lanes   1: " + str(lane1) + "  2:  " + str(lane2) + " event channel : " + str(channel)  )

def falling_callback(channel):
    if GPIO.input(channel):
       print("pressed : "+str(channel))
    else:
       print("released : "+str(channel))

GPIO.add_event_detect(17,GPIO.BOTH,callback=button_callback, bouncetime=10) # Setup event on pin 10 rising edge
GPIO.add_event_detect(27,GPIO.RISING,callback=button_callback, bouncetime=10) # Setup event on pin 10 rising edge




message = input("Press enter to quit\n\n") # Run until someone presses enter 

GPIO.cleanup() # Clean up
