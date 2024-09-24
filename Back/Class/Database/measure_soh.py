import Class.Database.test
import Class.Database.cell

class soh_measure():
    def __init__(self,tuple):
        self.id = tuple[0]
        self.test = Class.Database.test.test(tuple[0])
        self.cell = Class.Database.cell.cell(tuple[1])        
        self.voc= tuple[2]
        self.r0= tuple[3]
        self.soc= tuple[4]
        self.time= tuple[5]
    def toString(self):
        return '{"test":"' + self.test.toString() + '","cell":"' + self.cell.toString() + '","voc":"'\
        + str(self.voc) + '","r0":"' + str(self.r0) + '","soc":"' + str(self.soc) + '","time":"' + str(self.time) + '"}'

class soh_measureConstruct():
    def __init__(self,test,cell,voc,r0,soc,time):
        self.test = test
        self.cell = cell
        self.voc = voc
        self.r0 = r0
        self.soc = soc
        self.time = time
    def commit(self):
        #TODO
        pass

class soh_measureStat():
    def __init__(self,tuple):
        self.cell = Class.Database.cell.cell((tuple[0],tuple[1],tuple[2],))
        self.avgR0 = tuple[3]
        self.maxR0 = tuple[4]
        self.minR0 = tuple[5]
    def toString(self):
        return '{' +'"cell":' + self.cell.toString()\
            +',"AVGR0":"' + str(self.avgR0) + '","MAXR0":"' + str(self.maxR0) + '","MINR0":"' + str(self.minR0) + '"}'
    

