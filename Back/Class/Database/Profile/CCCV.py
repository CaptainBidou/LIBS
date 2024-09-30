import Class.Database.Profile.ProfileAbstract as ProfileAbstract
class CCCVProfile(ProfileAbstract.ProfileCrate):
    def __init__(self):
        self.ampl = 2
        self.timeResting = 0
        self.timePulsing = 0

    def getAmpl(self):
        return self.ampl
    def getTimeResting(self):
        self.timeResting = 1000*60*60
        return self.timeResting
    def getTimePulsing(self):
        self.timePulsing = 25
        return self.timePulsing
    
    def setAmpl(self, c_rate):
        return super().setAmpl(c_rate)