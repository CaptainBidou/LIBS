import Class.Database.test

class health_test():
    def __init__(self,tuple):
        self.id = tuple[0]
        self.commentary = tuple[1]
        self.time = tuple[2]
        self.testsList = []
        self.timeRestsList = []
        for testElt in tuple[3]:
            self.testsList.append(Class.Database.test.test(testElt))
        for time in tuple[4]:
            self.timeRestsList.append(time)


    def toString(self):
        stri = '{"id":"' + str(self.id) + '","commentary":"' + self.commentary + '","time":"' + str(self.time) + '","testsList":['
        for test in self.testsList:
            stri += test.toString()+','
        stri += '],"timeRestsList":['
        for time in self.timeRestsList:
            stri += str(time)+','
        if len(self.timeRestsList) > 0:
            stri = stri[:-1]
        stri += ']}'
        return stri

class health_testConstruct():
    def __init__(self,commentary,time,testsList,timeRestsList):
        self.commentary = commentary
        self.time = time
        self.testsList = []
        for testElt in testsList:
            self.testsList.append(Class.Database.test.test(testElt))
        self.timeRestsList = []
        for time in timeRestsList:
            self.timeRestsList.append(time)
    def commit(self):
        #TODO
        pass

