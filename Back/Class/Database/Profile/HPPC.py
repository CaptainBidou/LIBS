import Class.Database.Profile.ProfileAbstract as ProfileAbstract
class HppcProfile(ProfileAbstract.Profile):
    def __init__(self):
        self.step = 0
        self.ampl = [1.95, 0, -1.46, 1]
        self.timeResting = 0
        self.timePulsing = [18,32,10,(10/3.08)*60*60]

    def getAmpl(self):
        return self.ampl[self.step]
    def getTimeResting(self):
        return self.timeResting
    def getTimePulsing(self):
        record = self.timePulsing[self.step]
        self.step = self.step + 1
        if (self.step == 4):
            self.step = 0
        return record 