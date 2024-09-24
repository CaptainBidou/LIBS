import Class.Database.Profile.ProfileAbstract as ProfileAbstract
class ConstantProfile(ProfileAbstract.ProfileCrate):
    def __init__(self):
        self.ampl = 1
        self.timeResting = 0
        self.timePulsing = 0

    def getAmpl(self):
        return self.ampl
    def getTimeResting(self):
        self.timeResting = 0
        return self.timeResting
    def getTimePulsing(self):
        self.timePulsing = 100*60*60*60
        return self.timePulsing