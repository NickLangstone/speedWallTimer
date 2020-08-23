import time
from datetime import datetime

# personState states
#  0 - idle state
#  1 - ready - foot on pad
#  2 - successful start
#  3 - successful completion
#  9 - false start - reaction beore start


#  good run
#  +---------+---------+--------~~-------+-----
# reset     start     reaction           stop
#
#  false start
#  +---------+---------+---------~~------+-----
# reset    reaction   start             stop



class LaneTimer:
    def __init__(self, lane):
        self.lane = lane
        self.personState = 0
        self.reset()
        

    def start(self):
        if 9 == self.personState:   # false start
            print("False Start : " + self.lane)
            return
        # If start time already set, then just ignore subsequent events
        if 0 == self.startTime:
            self.startTime = datetime.now()
            self.personState=2

    def stop(self):
        # Only record the stop time on the first time the stop() function is called
        if 0 == self.endTime:
            self.endTime = datetime.now()
            self.personState=3
            
    def reaction(self):
        if 0 == self.startTime: #false start
            self.personState = 9   #false Start
            print("False Start set: " + self.lane)
            return
            # Only record the reaction time on the first time the reaction() function is called
        if 0 == self.reactionTime:
            self.reactionTime = datetime.now()

    def ready(self):
        self.reset()
        self.personState = 1

    def setReady(self, state):
        self.personState = state

    def reset(self):
        self.startTime = 0
        self.endTime = 0
        self.reactionTime = 0
       
    def getEndTimer(self):
        if self.endTime == 0 :
            return 0
        else:
            return self.endTime.timestamp()

    
    def getTimer(self):
        if 0 == self.endTime:
            return datetime.now() - self.startTime
        else:
            return self.endTime - self.startTime

    def minutes_seconds(self,td):
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        seconds = format(seconds, "02d")
        return  str(minutes) + ":" + str(seconds) +"." + str(td.microseconds )[:3]

    def getTimerDisplay(self):
        if ( 0 == self.startTime ):
            return "0:00.000"
        return self.minutes_seconds(self.getTimer())
        

    def getReactionTimerDisplay(self):
        if ( 0 == self.reactionTime ):
            return "0:00.000"
        return self.minutes_seconds(self.reactionTime - self.startTime)
        
    def getReady(self):
        return self.personState
