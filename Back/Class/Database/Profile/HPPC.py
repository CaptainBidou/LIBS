import Class.Database.Profile.ProfileAbstract as ProfileAbstract
class HppcProfile(ProfileAbstract.Profile):
    def __init__(self):
        self.step = 0
        self.ampl = [0.25, 0.5, 1.0, 1.5]
        self.timeResting = 10*60
        self.timePulsing = 55

    def getAmpl(self):
        return 1
    def getTimeResting(self):
        return self.timeResting
    def getTimePulsing(self):
        return self.timePulsing