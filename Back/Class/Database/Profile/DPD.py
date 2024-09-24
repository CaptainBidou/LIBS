import Class.Database.Profile.ProfileAbstract as ProfileAbstract
class DPDProfile(ProfileAbstract.Profile):
    def __init__(self):
        self.stepAmpl = 0
        self.ampl = [0.25, 0.5, 1.0, 1.5]
        self.stepRest=0
        self.timeResting = [0,0,0,30*60]
        self.timePulsing = 55

    def getAmpl(self):
        record = self.ampl[self.stepAmpl]
        self.stepAmpl = self.stepAmpl + 1
        if (self.stepAmpl == 4):
            self.stepAmpl = 0
        return record
    def getTimeResting(self):
        record = self.timeResting[self.stepRest]
        self.stepRest = self.stepRest + 1
        if (self.stepRest == 4):
            self.stepRest = 0
        return record
    def getTimePulsing(self):
        return self.timePulsing 
    