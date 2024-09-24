import Class.Database.importModel as importModel
def Observer():
    return importModel.Observer.Observer()
def FNN():
    return importModel.FNN.FNN()
def EKF():
    return importModel.EKF.EKF()
class observer():
    def __init__(self, tuple):
        self.id = tuple[0]
        self.name = tuple[1]
        self.function = globals()[tuple[2]] # function is a name of a function
    def toString(self):
        return '{"id":"' + str(self.id) + '","name":"' + self.name + '","function":"' + self.function.__name__+'"}'

class observerConstruct():
    def __init__(self,observer):
        self.name = observer["name"]
        self.function = globals()[observer["function"]]
        self.id = observer["id"]
    def toTuple(self):
        return (self.id,)
    