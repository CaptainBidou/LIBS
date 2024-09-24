import Class.Database.Profile.ProfileAbstract as ProfileAbstract
import random
class RDSTProfile(ProfileAbstract.Profile):
    def __init__(self):
        self.ampl = 0
        self.timeResting = 0
        self.timePulsing = 0

    def getAmpl(self):
        self.ampl = random.uniform(0.1, 1.5)
        return self.ampl
    def getTimeResting(self):
        self.timeResting = 0
        return self.timeResting
    def getTimePulsing(self):
        self.timePulsing = random.uniform(30, 120)
        return self.timePulsing