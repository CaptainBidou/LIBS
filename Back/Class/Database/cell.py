class cell():
    def __init__(self, tuple):
        self.id = tuple[0]
        self.name = tuple[1]
        self.soc = tuple[2]
        self.Qn = 3.08  #Rated capacity
        self.Vn = 3.6  #Nominal voltage
        self.Vmax = 4.2  #Max voltage (Charging)
        self.Vmin = 2.5  #Min voltage (Discharging)
        self.QcompPS = 0  #Capacity computed to charge
        self.QcompEL = 0  #Capacity computed to discharge
        self.QcompPSEL = 0.35 * 2.9
        self.Icut = self.Qn / 50  #Cut off current
    def toString(self):
        return '{"id":"' + str(self.id) + '","name":"' + self.name + '","soc":"' + str(self.soc) + '"}'

class cellConstruct():
    def __init__(self,cell):
        self.name = cell["name"]
        self.soc = cell["soc"]
        self.id = cell["id"]
        self.Qn = 3.08  #Rated capacity
        self.Vn = 3.6  #Nominal voltage
        self.Vmax = 4.2  #Max voltage (Charging)
        self.Vmin = 2.5  #Min voltage (Discharging)
        self.QcompPS = 0  #Capacity computed to charge
        self.QcompEL = 0  #Capacity computed to discharge
        self.QcompPSEL = 0.35 * 2.9
        self.Icut = self.Qn / 50  #Cut off current
    def toTuple(self):
        return (self.id,)
    
class newCellConstruct():
    def __init__(self,cell):
        self.name = cell["name"]
        self.soc = cell["soc"]
    def toTuple(self):
        return (self.name,self.soc)