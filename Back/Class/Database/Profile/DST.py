import Class.Database.Profile.ProfileAbstract as ProfileAbstract
class DSTProfile(ProfileAbstract.Profile):
    def __init__(self):
        self.stepAmpl = 0
        self.ampl = [0, 0.5, 1.0, -0.5,0, 0.5, 1.0, -0.5,0, 0.5, 1.0, -0.5,0,0.5,2,1.5,-1,1,-2,0]
        self.stepRest=0
        self.timeResting = 0
        self.timePulsing = [16,24,12,8,16,24,12,8,16,24,12,8,16,36,8,24,8,32,8,44]
    def getAmpl(self):
        return self.ampl[self.stepAmpl]
    def getTimeResting(self):
        return self.timeResting
    def getTimePulsing(self):
        record = self.timePulsing[self.stepAmpl]
        self.stepAmpl = self.stepAmpl + 1
        if (self.stepAmpl == 20):
            self.stepAmpl = 0
        return record
    