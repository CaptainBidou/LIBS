import Class.Database.importProfile as importProfile

def CCCVProfile():
    return importProfile.CCCV.CCCVProfile()
def ConstantProfile():
    return importProfile.Constant.ConstantProfile()
def DSTProfile():
    return importProfile.DST.DSTProfile()
def HPPCProfile():
    return importProfile.HPPC.HppcProfile()
def PulseProfile():
    return importProfile.Pulse.PulseProfile()
def RandomProfile():
    return importProfile.Random.RandomProfile()
def RDSTProfile():
    return importProfile.RDST.RDSTProfile()
def MPDProfile():
    return importProfile.MPD.MPDProfile()
def DPDProfile():
    return importProfile.DPD.DPDProfile()

class action():
    def __init__(self,tuple):
        # (1, "Charge CC-CV", "ChConst", 1, 1, "CCCVProfile") is a tuple example
        self.id = tuple[0]
        self.name = tuple[1]
        self.brief = tuple[2]
        self.chargeBool = tuple[4]
        self.crate_bool = tuple[5]
        self.function = globals()[tuple[3]+'Profile'] # function is a name of a function
    def toString(self):
        return '{"id":"' + str(self.id) + '","name":"' + self.name + '","brief":"' + self.brief + '","chargeBool":"' \
            + str(self.chargeBool) + '","crate_bool":"' + str(self.crate_bool) + '","function":"' + self.function.__name__+'"}'

class actionConstruct():
    def __init__(self,action):
        self.name = action["name"]
        self.brief = action["brief"]
        self.chargeBool = action["chargeBool"]
        self.crate_bool = action["crate_bool"]
        self.function = globals()[action["function"]]
        self.id = action["id"]
    def toTuple(self):
        return (self.id,self.name,self.brief,self.function.__name__,self.chargeBool,self.crate_bool)