import Class.Database.Profile.ProfileAbstract as ProfileAbstract
class PulseProfile(ProfileAbstract.ProfileCrate):
    def __init__(self):
        self.ampl = 0
        self.timeResting = 0
        self.timePulsing = 0
    def getAmpl(self):
        return self.ampl
    def getTimeResting(self):
        self.timeResting = (5/10)*60*60
        return self.timeResting
    def getTimePulsing(self):
        self.timePulsing = (5/float(self.ampl))*60*60
        return self.timePulsing