import Class.Database.Profile.ProfileAbstract as ProfileAbstract
class DSTProfile(ProfileAbstract.Profile):
    def __init__(self):
        self.stepAmpl = 0
        self.ampl = [0.25, 0.5, 1.0, 1.5]
        self.stepRest=0
        self.timeResting = [0,0,0,30*60]
        self.timePulsing = 55
    def getAmpl(self):
        return 1
    def getTimeResting(self):
        return 60
    def getTimePulsing(self):
        return self.timePulsing 
    