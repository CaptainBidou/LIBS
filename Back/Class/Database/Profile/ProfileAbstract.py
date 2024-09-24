from abc import ABC, abstractmethod

class Profile:
    @abstractmethod
    def __init__(self):
        self.ampl = 0
        self.timeResting = 0
        self.timePulsing = 0
        raise NotImplementedError

    @abstractmethod
    def getAmpl(self):
        raise NotImplementedError

    @abstractmethod
    def getTimeResting(self):
        raise NotImplementedError

    @abstractmethod
    def getTimePulsing(self):
        raise NotImplementedError

class ProfileCrate(Profile):
    @abstractmethod
    def __init__(self):
        super().__init__()
        raise NotImplementedError

    def setAmpl(self,c_rate):
        self.ampl = c_rate/100