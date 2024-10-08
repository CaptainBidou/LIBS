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
        if len(self.testsList) > 0:
            stri = stri[:-1]
        stri += '],"timeRestsList":['
        for time in self.timeRestsList:
            stri += '"'+str(time[0])+'"'+','
        if len(self.timeRestsList) > 0:
            stri = stri[:-1]
        stri += ']}'
        return stri
    

    # {'commentary': '', 'time': '2024-09-27T12:47:39.659Z', 
    # 'testsList': [{'action': {'id': '4', 'name': 'Multi pulse discharge', 'brief': 'MPDch', 'chargeBool': '0', 'crate_bool': False, 'function': 'MPDProfile'},
    #  'cellsList': [{'id': '2', 'name': 'BID002', 'soc': '1.0'}],
    #  'observersList': [{'id': '2', 'name': 'Neural network dynamic', 'function': 'FNN'}],
    #  'comment': '', 'c_rate': 0, 'time': '2024-09-27T12:47:38.124Z', 'time_resting': 0}]}

class health_testConstruct():
    def __init__(self,healthTest):
        self.commentary = healthTest["commentary"]
        self.testsList = []
        self.timeRestsList = []
        for testElt in healthTest["testsList"]:
            self.testsList.append(Class.Database.test.testConstruct(testElt))
            self.timeRestsList.append(testElt["time_resting"])

