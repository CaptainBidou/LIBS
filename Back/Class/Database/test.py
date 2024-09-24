import Class.Database.cell
import Class.Database.action
import Class.Database.observer

class test():
    def __init__(self,tuple):
        self.id = tuple[0]
        self.time = tuple[1]
        self.action = Class.Database.action.action((tuple[2],tuple[3],tuple[4],tuple[7],tuple[5],tuple[6]))
        self.comment = tuple[8]
        self.c_rate = tuple[9]
        self.running_bool = tuple[10]
        self.cellsList = []
        # self.cellsList.append(Class.Database.cell.cell((tuple[11],tuple[12],tuple[13])))
        
        for cellElt in tuple[11]:
            self.cellsList.append(Class.Database.cell.cell(cellElt))
        self.observersList = []
        for observerElt in tuple[12]:
            self.observersList.append(Class.Database.observer.observer(observerElt))
        # self.observersList.append(Class.Database.observer.observer((tuple[14],tuple[15],tuple[16])))
    def toString(self):
        stri = '{"id":"' + str(self.id) + '","time":"' + str(self.time) + '","action":' + self.action.toString() + ',"comment":"' + self.comment + '","c_rate":"' + str(self.c_rate) + '","cellsList":['
        for cell in self.cellsList:
            stri += cell.toString()+','
        if len(self.observersList) > 0:
            stri = stri[:-1]
        stri += '],"observersList":['
        for observer in self.observersList:
            stri += observer.toString()+','
        # take care of the last comma
        if len(self.observersList) > 0:
            stri = stri[:-1]
        stri += '],"running_bool":"' + str(self.running_bool) + '"}'
        return stri

class testConstruct():
    def __init__(self,test):
        self.action = Class.Database.action.actionConstruct(test["action"])
        self.comment = test["comment"]
        self.c_rate = test["c_rate"]
        self.cellsList = []
        for cellElt in test["cells"]:
            self.cellsList.append(Class.Database.cell.cellConstruct(cellElt))
        self.observersList = []
        for observerElt in test["observers"]:
            self.observersList.append(Class.Database.observer.observerConstruct(observerElt))
        self.running_bool = test["running_bool"]
    def toTuple(self):
        return (self.action,self.comment,self.c_rate,self.cellsList,self.observersList,self.running_bool)