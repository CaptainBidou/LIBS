class currentVoltage():
    def __init__(self,tuple):
        self.current = tuple[0]
        self.voltage = tuple[1]
    def toString(self):
        return '{"current":"' + str(self.current) + '","voltage":"' + str(self.voltage) + '"}'

