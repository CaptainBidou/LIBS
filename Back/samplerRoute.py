###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################

import time
import pyvisa as visa
import random
import threading
import atexit
import Communication.bms as bms
from threading import Thread
import Communication.sendMessage as sendMessage
import Communication.serialComm as serialComm
import Class.importRoute as importRoute
import Class.importDatabase as importDatabase

###################################################################
##                   G L O B A L   C O N S T A N T               ##
###################################################################
SAMPLING_RATE = 1  # seconds
POWER_SUPPLY = 'USB0::0x2EC7::0x6700::802259073777170159::INSTR'
ELECTRONIC_LOAD = 'USB0::0x1AB1::0x0E11::DL3A250700137::INSTR'
TEST = 0
ESTIMATORTAB = {}
ESTIMATORID={}
SEED = 0
ESTIMATORCELL = {}
DEVICE = {}
DEVICEMOD=""


###################################################################
##                   G L O B A L   V A R I A B L E S             ##
###################################################################
startTime = 0
killThread = False
semVISA = threading.BoundedSemaphore(1)
###################################################################
##            F U N C T I O N    D E C L A R A T I O N           ##
###################################################################
def calculIt(value):
    global TEST
    print(TEST)
    return float(value)*TEST.cellsList[0].Qn

def verifyCellVmin(volt,cells):
    if(len(TEST.cellsList)>1):
        measure = bms.measure_soh()
        for i in range(0,8):
            if(measure["v"+str(i+1)]<=TEST.cellsList[i].Vmin):
                return True
        return False

    for cell in cells:
        if(volt<=cell.Vmin):
            return True
    return False

def verifyCurrentMin(current,cells):
    for cell in cells:
        if(current<=cell.Icut):
            return True
    return False

def calculImax(It):
    return 1.1 * It

def calculQtype(It):
    return round(It / TEST.cellsList[0].Qn, 1)

def initDevice(device):
    rm = visa.ResourceManager()
    device.pwrSupply = rm.open_resource(POWER_SUPPLY)
    device.electLoad = rm.open_resource(ELECTRONIC_LOAD)
    device.pwrSupply_info = device.pwrSupply.query('*IDN?')
    device.electLoad_info = device.electLoad.query('*IDN?')

def startMeasure(idTest,device,mode):
    if(mode != "PS" and mode != "EL"):
        return
    # send request to the ps
    global TEST
    voltPwrSupply = str(round(float(configMeasureQuery(device, "VOLT")), 3))
    ampePwrSupply = str(round(float(configMeasureQuery(device, "CURR")), 3))
    semVISA.release() 
    surfaceTempPlus = serialComm.send_data("surfaceTemperaturePlus?\n")
    surfaceTempMinus = serialComm.send_data("surfaceTemperatureMinus?\n")
    ambientTemp = serialComm.send_data("ambientTemperature?\n")

    mesure = importDatabase.Measure.measureConstruct(TEST,TEST.cellsList[0],ampePwrSupply,voltPwrSupply,ambientTemp,surfaceTempPlus,surfaceTempMinus)
    id = importRoute.measure.put(mesure)

    global ESTIMATORTAB
    global ESTIMATORID
    

    for estimators in TEST.observersList:
        est = estimators.function()
        threadEstimation = Thread(target=estimator, args=(id,voltPwrSupply,ampePwrSupply,ESTIMATORID[est.toString()],))
        threadEstimation.start()
    for cell in TEST.cellsList:
        threadSOC = Thread(target=socThread, args=(cell,float(ampePwrSupply),))
        threadSOC.start()
    exit()



def startMeasureBMS(idTest,device,mode):
    if(mode != "PS" and mode != "EL"):
        return
    global TEST
    ampePwrSupply = str(round(float(configMeasureQuery(device, "CURR")), 3))
    semVISA.release() 
    ambientTemp = serialComm.send_data("ambientTemperature?\n")
    for i in range(0,8):
        objet = bms.measure(i+1)
        volt = objet["voltage"]
        temp = objet["temperature"]
        mesure = importDatabase.Measure.measureConstruct(TEST,TEST.cellsList[i],ampePwrSupply,volt,ambientTemp,temp,temp)
        id = importRoute.measure.put(mesure)
        global ESTIMATORTAB
        global ESTIMATORID
        global ESTIMATORCELL
        for estimators in TEST.observersList:
            threadEstimation = Thread(target=estimator, args=(id,volt,ampePwrSupply,(TEST.cellsList[i],estimators),))
            threadEstimation.start()
        threadSOC = Thread(target=socThread, args=(TEST.cellsList[i],float(ampePwrSupply),))
        threadSOC.start()
    exit()
    
    
def startProfilePS(value,device):
    global TEST
    device.write("SOUR:VOLTage:LEVel " + str(TEST.cellsList[0].Vmax))
    device.write("SOUR:CURRent:LEVel " + str(calculIt(value)))

def startProfileEL(It,Imax,device):
    global TEST
    device.write("SOUR:FUNC CURR")
    device.write("SOUR:CURR:LEV:IMM " + str(It))
    device.write("SOUR:CURR:RANG 40")
    device.write("SOUR:CURR:SLEW 0.01")
    device.write("SOUR:CURR:VON " + str(TEST.cellsList[0].Vmin))
    device.write("SOUR:CURR:VLIM " + str(TEST.cellsList[0].Vmax))
    device.write("SOUR:CURR:ILIM 7.5")

def configMeasureQuery(device, measure):
        if (measure == "VOLT"):
            return device.query('MEASure:VOLTage?')
        if (measure == "CURR"):
            return device.query('MEASure:CURRent?')
def output(output,device,deviceType):
    if(deviceType == "PS"):
        device.write('OUTPut:STATe ' + str(output))
    if(deviceType == "EL"):
        device.write('INPut:STATe ' + str(output))
    return

def configPSStatusQuery(device):
    return device.query('STATus:QUEStionable:CONDition?')

def configELStatusQuery(device):
    return device.query('STAT:QUES:COND?')

def configELModeQuery(device):
    return device.query('SOUR:FUNC?')

def configELWrite(device):
    device.write('STAT:QUES:ENAB 32271')

def exitProg():
    pass
    # global DEVICE
    # output(0, DEVICE.electLoad, "EL")
    # output(0, DEVICE.pwrSupply, "PS")
    
###################################################################
##            S T R U C T    D E C L A R A T I O N               ##
###################################################################
class MeasuringDevice():
    def __init__(self,pwrsuplly, electload):
        self.pwrSupply = None
        self.electLoad = None
        self.pwrSupply_info = None
        self.electLoad_info = None
        self.pwrSupplyId = pwrsuplly
        self.electLoadId = electload
########################################################################
######                 T H R E A D   C O D E                     #######
########################################################################

class Counter():
    def __init__(self, increment, idTest, device,mode):
        
        self.next_t = time.time()
        self.i = 0
        self.done = False
        self.increment = increment
        self.device = device
        self.deviceComplete = None
        self.mode = mode
        self.idTest = idTest
        self._run()

    def _run(self):
        global killThread
        global TEST
        global DEVICE
        global DEVICEMOD
        while not self.done and not killThread :
        
            semVISA.acquire()
            if(TEST.action.chargeBool==1 and TEST.action.dischargeBool==1):
                if (len(TEST.cellsList)== 1):
                    threading.Timer(0.0,startMeasure,(self.idTest, DEVICE,DEVICEMOD,)).start()
                else :
                    threading.Timer(0.0,startMeasureBMS,(self.idTest, DEVICE,DEVICEMOD,)).start()

            else:
                if (len(TEST.cellsList)== 1):
                    threading.Timer(0.0,startMeasure,(self.idTest, self.device,self.mode,)).start()
                else :
                    threading.Timer(0.0,startMeasureBMS,(self.idTest, self.device,self.mode,)).start()

            time.sleep(self.increment)

    def stop(self):
        self.done = True



class estimator():
    def __init__(self,idMeasure,volt,amp,id,):
        self.volt = volt
        self.amp = amp
        self.idMeasure = idMeasure
        self.id = id
        global TEST
        if (len(TEST.cellsList)>1):
            self.runBMS()
        else:
            self.run()


    def run(self):
        global TEST
        global ESTIMATORTAB
        g,x=ESTIMATORTAB[self.id].runOneStep(self.volt,self.amp,TEST.action.chargeBool)
        print("voltage :"+str(g)+" SOC :"+str(x))
        measure_est = importDatabase.MeasureEstimator.measure_estimatorConstruct(self.idMeasure,self.id,0,0,g,x)
        importRoute.measure_observer.put(measure_est)
        exit()

    def runBMS(self):
        global TEST
        global ESTIMATORCELL
        g,x=ESTIMATORCELL[self.id[0]][self.id[1]]["function"].runOneStep(self.volt,self.amp,TEST.action.chargeBool)
        print("voltage :"+str(g)+" SOC :"+str(x))
        measure_est = importDatabase.MeasureEstimator.measure_estimatorConstruct(self.idMeasure,self.id[1],0,0,g,x)
        importRoute.measure_observer.put(measure_est)
        exit()

class socThread():
    def __init__(self,cell,current):
        self.cell = cell
        self.current = current
        self.run()
    def run(self):
        global TEST
        if TEST.action.chargeBool == True:
            self.cell.soc = self.cell.soc + self.current/(self.cell.Qn*3600)
        else:
            self.cell.soc = self.cell.soc - self.current/(self.cell.Qn*3600)

        if(self.cell.soc<0):
            self.cell.soc =0
        
        if(self.cell.soc>1):
            self.cell.soc=1
            
        importRoute.cell.update(self.cell)
        exit()


class sohRoutine():
    def __init__(self,funct,dev):
        global TEST
        self.funct = funct
        self.device = dev
        self.aCurrent = 0
        self.bCurrent = 0
        self.aVoltage = 0
        self.bVoltage = 0
        self.voltTabA={}
        self.voltTabB={}
        self.voc=None
        self.r0 =0
        if(len(TEST.cellsList)>1):
            self.cell = TEST.cellsList
            self.runBMS()
        else :
            self.cell = TEST.cellsList[0]
            self.run()


    def run(self):
        self.aVoltage = float(configMeasureQuery(self.device, "VOLT"))
        self.aCurrent = float(configMeasureQuery(self.device, "CURR"))
        self.funct()
        self.bVoltage = float(configMeasureQuery(self.device, "VOLT"))
        self.bCurrent = float(configMeasureQuery(self.device, "CURR"))
        while(round(self.bCurrent,1) == round(self.aCurrent,1) or round(self.bVoltage,2) == round(self.aVoltage,2)):
            self.bCurrent = float(configMeasureQuery(self.device, "CURR"))
            self.bVoltage = float(configMeasureQuery(self.device, "VOLT"))
            time.sleep(0.01)
        self.r0 = abs(self.aVoltage-self.bVoltage)/abs(self.aCurrent-self.bCurrent)
        if(self.aVoltage>self.bVoltage):
            self.voc=self.aVoltage

        global TEST
        result = importDatabase.MeasureSoh.soh_measureConstruct(TEST,self.cell,self.voc,self.aCurrent,self.bVoltage,self.bCurrent,self.r0,self.cell.soc,time.time())
        importRoute.measure_soh.put(result)
        # dataSend = Thread(target = databaseBuild.createSohMeasure, args=(TEST.id,self.cell.id,self.voc,self.r0,self.cell.soc,))
        # dataSend.start()
        return
    
    def runBMS(self):
        self.voltTabA = bms.measure_soh()
        self.aCurrent = float(configMeasureQuery(self.device, "CURR"))
        self.funct()
        self.voltTabB = bms.measure_soh()
        self.bCurrent = float(configMeasureQuery(self.device, "CURR"))
        while(round(self.bCurrent,1) == round(self.aCurrent,1)):
            self.bCurrent = float(configMeasureQuery(self.device, "CURR"))
            self.voltTabB = bms.measure_soh()
            time.sleep(0.01)
        global TEST
        for i in range(0,8):
            self.cell = TEST.cellsList[i]
            self.aVoltage = self.voltTabA["v"+str(i+1)]
            self.bVoltage = self.voltTabB["v"+str(i+1)]
            self.r0 = abs(self.aVoltage-self.bVoltage)/abs(self.aCurrent-self.bCurrent)
            if(self.aVoltage>self.bVoltage):
                self.voc=self.aVoltage
            result = importDatabase.MeasureSoh.soh_measureConstruct(TEST,self.cell,self.voc,self.aCurrent,self.bVoltage,self.bCurrent,self.r0,self.cell.soc,time.time())
            importRoute.measure_soh.put(result)
        return
########################################################################
devices = MeasuringDevice(POWER_SUPPLY, ELECTRONIC_LOAD)
initDevice(devices)
interrupt = None
atexit.register(exitProg)



def startTestDischarge():
    global TEST
    profile = TEST.action.function()
    if(TEST.action.crate_bool):
        profile.setAmpl(TEST.c_rate)
    startProfileEL(0, 5, devices.electLoad)
    interrupt = Thread(target=Counter, args=(SAMPLING_RATE,TEST.id,devices.electLoad,"EL",))
    interrupt.start()
    while (True):
        semVISA.acquire()
        startTime = time.time()
        startProfileEL(profile.getAmpl()*TEST.cellsList[0].Qn, 5, devices.electLoad)
        timePulsing = profile.getTimePulsing()
        routine = sohRoutine(lambda:output(1, devices.electLoad, "EL"),devices.electLoad)
        semVISA.release()
        while (time.time() - startTime < timePulsing):
            print("timePulsing")
            semVISA.acquire()
            voltage = configMeasureQuery(devices.electLoad, "VOLT")
            semVISA.release()
            voltage = str(round(float(voltage), 3))
            global killThread
            if(verifyCellVmin(float(voltage),TEST.cellsList) or killThread == True):
                importRoute.test.post(TEST.id,0)
                killThread = True
                semVISA.acquire()
                serialComm.send_data("relay2=off\n")
                serialComm.send_data("relay1=off\n")
                routine = sohRoutine(lambda:output(0, devices.electLoad, "EL"),devices.electLoad)
                print("We turn off everything before leaving")
                sendMessage.sendMessage("Test is over")
                semVISA.release()
                exit()
            time.sleep(SAMPLING_RATE)
        timeResting = profile.getTimeResting()
        startTime = time.time()
        
        if(time.time() - startTime < timeResting):#it's always true but not for the DST profile ( check the trick )
            semVISA.acquire()
            routine = sohRoutine(lambda:output(0, devices.electLoad, "EL"),devices.electLoad)
            semVISA.release()
        while (time.time() - startTime < timeResting):
            print("timeResting")
            
            if(killThread):
                exit()
            time.sleep(SAMPLING_RATE)

def getVoltageCurrent(test):
    
    global SEED
    SEED = random.randint(0, 100)
    random.seed(SEED)

    global TEST 
    TEST =test

    profile = test.action.function()

    if(test.action.crate_bool):
        profile.setAmpl(test.c_rate)
        print("profile.getAmpl() : "+str(profile.getAmpl()))

    if(test.action.chargeBool):
        serialComm.send_data("relay2=off\n")
        serialComm.send_data("relay1=on\n")
        voltage =  configMeasureQuery(devices.pwrSupply, "VOLT")
        serialComm.send_data("relay1=off\n")
        return {"Current": calculIt(profile.getAmpl()), "Voltage": voltage }

    else:
        serialComm.send_data("relay1=off\n")
        serialComm.send_data("relay2=on\n") 
        voltage = configMeasureQuery(devices.electLoad, "VOLT")
        serialComm.send_data("relay2=off\n")
        voltage = round(float(voltage), 3)
        current = profile.getAmpl()*test.cellsList[0].Qn
        current = round(float(current), 3)
        return {"Current": current, "Voltage": voltage}    


def startTestCharge():
    global TEST
    cccvProfile = TEST.action.function()
    cccvProfile.setAmpl(TEST.c_rate)
    interrupt = Thread(target=Counter, args=(SAMPLING_RATE,TEST.id,devices.pwrSupply,"PS",))
    interrupt.start()
    semVISA.acquire()
    startTime = time.time()
    startProfilePS(cccvProfile.getAmpl(),devices.pwrSupply)
    timePulsing = cccvProfile.getTimePulsing()
    timeResting = cccvProfile.getTimeResting()
    routine = sohRoutine(lambda:output(1, devices.pwrSupply, "PS"),devices.pwrSupply)
    semVISA.release()
    while (True):
        while(time.time() - startTime < timePulsing):
            semVISA.acquire()
            output(1,devices.pwrSupply,"PS")
            semVISA.release()
            time.sleep(SAMPLING_RATE)
        startTime = time.time()
        while(time.time() - startTime < timeResting):
            semVISA.acquire()
            current = configMeasureQuery(devices.pwrSupply, "CURR")
            current = str(round(float(current), 3))
            semVISA.release()
            global killThread
            if(verifyCurrentMin(float(current),TEST.cellsList) or killThread):
                importRoute.test.post(TEST.id,0)
                killThread = True
                semVISA.acquire()
                serialComm.send_data("relay2=off\n")
                serialComm.send_data("relay1=off\n")
                routine = sohRoutine(lambda:output(0, devices.pwrSupply, "PS"),devices.pwrSupply)
                semVISA.release()
                sendMessage.sendMessage("Test is over")
                exit()
            time.sleep(SAMPLING_RATE)

def startTestChargeDischarge():
    global TEST
    global DEVICE 
    global DEVICEMOD
    DEVICE = devices.electLoad
    DEVICEMOD ="EL"
    profile = TEST.action.function()
    startProfileEL(0, 5, devices.electLoad)
    interrupt = Thread(target=Counter, args=(SAMPLING_RATE,TEST.id,DEVICE,DEVICEMOD,)) #mettre au point le device en global et changer quand on change de device
    interrupt.start()

    while (True):
        
        semVISA.acquire()
        startTime = time.time()
        ampl = profile.getAmpl()
        timePulsing = profile.getTimePulsing()
        if(ampl>0):
            DEVICE = devices.electLoad
            DEVICEMOD ="EL"
            routine = sohRoutine(lambda:output(0, devices.pwrSupply, "PS"),devices.pwrSupply)
            serialComm.send_data("relay1=off\n")
            serialComm.send_data("relay2=on\n")
            startProfileEL(ampl*TEST.cellsList[0].Qn, 5, devices.electLoad)
            routine = sohRoutine(lambda:output(1, devices.electLoad, "EL"),devices.electLoad)
        if(ampl<0):
            DEVICE = devices.pwrSupply
            DEVICE ="PS"
            routine = sohRoutine(lambda:output(0, devices.electLoad, "EL"),devices.electLoad)
            serialComm.send_data("relay2=off\n")
            serialComm.send_data("relay1=on\n")
            startProfilePS(ampl,devices.pwrSupply)
            routine = sohRoutine(lambda:output(1, devices.pwrSupply, "PS"),devices.pwrSupply)
        if(ampl==0):
            DEVICE = devices.electLoad
            DEVICE ="EL"
            routine = sohRoutine(lambda:output(0, devices.pwrSupply, "PS"),devices.pwrSupply)
            serialComm.send_data("relay2=off\n")
            serialComm.send_data("relay1=on\n")
            startProfileEL(ampl*TEST.cellsList[0].Qn, 5, devices.electLoad)
            routine = sohRoutine(lambda:output(0, devices.electLoad, "EL"),devices.electLoad)
        semVISA.release()

        while (time.time() - startTime < timePulsing):
            print("timePulsing")
            semVISA.acquire()
            voltage = configMeasureQuery(DEVICE, "VOLT")#variable globale pour 
            current = configMeasureQuery(DEVICE, "CURR")
            current = str(round(float(current), 3))
            semVISA.release()

            voltage = str(round(float(voltage), 3))
            global killThread
            if(verifyCellVmin(float(voltage),TEST.cellsList) or killThread == True or verifyCurrentMin(float(current),TEST.cellsList)):
                importRoute.test.post(TEST.id,0)
                killThread = True
                semVISA.acquire()
                serialComm.send_data("relay2=off\n")
                serialComm.send_data("relay1=off\n")
                routine = sohRoutine(lambda:output(0, DEVICE, DEVICEMOD),DEVICE)
                print("We turn off everything before leaving")
                sendMessage.sendMessage("Test is over")
                semVISA.release()
                exit()
            time.sleep(SAMPLING_RATE)
        timeResting = profile.getTimeResting()
        startTime = time.time()
        
        if(time.time() - startTime < timeResting):#it's always true but not for the DST profile ( check the trick )
            semVISA.acquire()
            routine = sohRoutine(lambda:output(0, DEVICE, DEVICEMOD),DEVICE)
            semVISA.release()
        while (time.time() - startTime < timeResting):
            print("timeResting")
            
            if(killThread):
                exit()
            time.sleep(SAMPLING_RATE)



def setTest(test):
    global TEST
    TEST = test
    global ESTIMATORTAB
    global ESTIMATORID

    if(len(TEST.cellsList)>1):
        global ESTIMATORCELL
        for cell in TEST.cellsList:
            ESTIMATORCELL[cell.id]={}
            for estimators in TEST.observersList:
                ESTIMATORCELL[cell.id][estimators.id]={}
                est=estimators.function()
                ESTIMATORCELL[cell.id][estimators.id]["name"] = est.toString()
                ESTIMATORCELL[cell.id][estimators.id]["function"] = est
                ESTIMATORCELL[cell.id][estimators.id]["id"] = estimators.id
    else :
        for estimators in TEST.observersList:
            est=estimators.function()
            ESTIMATORID[est.toString()]=estimators.id
            ESTIMATORTAB[estimators.id] = est

    random.seed(SEED)

    if TEST.action.chargeBool and TEST.action.dischargeBool==0 :
        serialComm.send_data("relay2=off\n")
        serialComm.send_data("relay1=on\n")
        startTestCharge()
    elif TEST.action.dischargeBool and TEST.action.chargeBool==0 :
        serialComm.send_data("relay1=off\n")
        serialComm.send_data("relay2=on\n")
        startTestDischarge()
    elif TEST.action.dischargeBool and TEST.action.chargeBool :
        startTestChargeDischarge()


def measureAmbient():
    temperature=serialComm.send_data("ambientTemperature?\n")
    return temperature

def getArduinoStatus():
    try:
        temp = serialComm.send_data("ambientTemperature?\n")
        return True
    except:
        return False
    
def getDeviceStatus():
    try:
        temp = configMeasureQuery(devices.electLoad, "VOLT")
        temp = configMeasureQuery(devices.pwrSupply, "VOLT")
        print(temp)
        return True
    except:
        return False
    

def getBMSStatus():
    try:
        temp = bms.measure(1)
        print(temp)
        return True
    except:
        return False
