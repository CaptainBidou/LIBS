###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################

import time
import databaseBuild
import pyvisa as visa
import random
import threading
import atexit
from threading import Thread
import Communication.sendMessage as sendMessage
import Model.ExtendedKalmanFilter as ExtendedKalmanFilter
import Model.stateObserver as stateObserver
import Model.neuralNetwork as neuralNetwork
import Communication.serialComm as serialComm

###################################################################
##                   G L O B A L   C O N S T A N T               ##
###################################################################
SAMPLING_RATE = 1  # seconds
POWER_SUPPLY = 'USB0::0x2EC7::0x6700::802259073777170159::INSTR'
ELECTRONIC_LOAD = 'USB0::0x1AB1::0x0E11::DL3A250700137::INSTR'
IDTEST = 0

OBSERVER = False
EKF = False
FNN = False
CHARGE = False
CELLS = []

###################################################################
##                   G L O B A L   V A R I A B L E S             ##
###################################################################
cell = None
devices = None
param = None
randomProfile = None
hppcProfile = None
pulseProfile = None
constantProfile = None
cccvProfile = None
startTime = 0
killThread = False
sem = threading.BoundedSemaphore(1)
###################################################################
##            F U N C T I O N    D E C L A R A T I O N           ##
###################################################################
def calculIt(value):
    print("Value c-rate"+str(value))
    return float(value)*cell.Qn/100

def calculImax(It):
    return 1.1 * It

def calculQtype(It):
    return round(It / cell.Qn, 1)

def initDevice(device):
    rm = visa.ResourceManager()
    print(rm.list_resources())
    device.pwrSupply = rm.open_resource(POWER_SUPPLY)
    device.electLoad = rm.open_resource(ELECTRONIC_LOAD)
    device.pwrSupply_info = device.pwrSupply.query('*IDN?')
    device.electLoad_info = device.electLoad.query('*IDN?')

def startMeasure(idTest,device,mode):
    if(mode != "PS" and mode != "EL"):
        return
    # send request to the ps
    
    voltPwrSupply = str(round(float(configMeasureQuery(device, "VOLT")), 3))
    ampePwrSupply = str(round(float(configMeasureQuery(device, "CURR")), 3))
    sem.release() 
    surfaceTempPlus = serialComm.send_data("6")
    surfaceTempMinus = serialComm.send_data("7")
    ambientTemp = serialComm.send_data("5")
    id=databaseBuild.createMeasure(idTest, time.time(), ampePwrSupply, voltPwrSupply, ambientTemp, surfaceTempPlus, surfaceTempMinus)

    if FNN == True:
        threadEstimation = Thread(target=estimator, args=(id,voltPwrSupply,ampePwrSupply,1,))
        threadEstimation.start()
    if EKF == True:
        threadEstimation = Thread(target=estimator, args=(id,voltPwrSupply,ampePwrSupply,3,))
        threadEstimation.start()
    if OBSERVER == True:
        if CHARGE == True:
            threadEstimation = Thread(target=estimator, args=(id,voltPwrSupply,"-"+ampePwrSupply,4,))
            threadEstimation.start()
        else:
            threadEstimation = Thread(target=estimator, args=(id,voltPwrSupply,ampePwrSupply,4,))
            threadEstimation.start()
    global CELLS
    for cell in CELLS:
        threadSOC = Thread(target=socThread, args=(cell,float(ampePwrSupply),))
        threadSOC.start()
    exit()
    
def startProfilePS(value,device):
    print(calculIt(value))
    device.write("SOUR:VOLTage:LEVel " + str(cell.Vmax))
    device.write("SOUR:CURRent:LEVel " + str(calculIt(value)))

def startProfileEL(It,Imax,device):
    device.write("SOUR:FUNC CURR")
    device.write("SOUR:CURR:LEV:IMM " + str(It))
    device.write("SOUR:CURR:RANG 40")
    device.write("SOUR:CURR:SLEW 0.01")
    device.write("SOUR:CURR:VON " + str(cell.Vmin))
    device.write("SOUR:CURR:VLIM " + str(cell.Vmax))
    device.write("SOUR:CURR:ILIM 5")

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

def configPSStatusQuery(device):
    return device.query('STATus:QUEStionable:CONDition?')

def configELStatusQuery(device):
    return device.query('STAT:QUES:COND?')

def configELModeQuery(device):
    return device.query('SOUR:FUNC?')

def configELWrite(device):
    device.write('STAT:QUES:ENAB 32271')

def exitProg():
    output(0, devices.electLoad, "EL")
    output(0, devices.pwrSupply, "PS")
    
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

class Cell():
    def __init__(self,id=0,soc=0):
        # LIB: NCR18650BD
        self.Qn = 3.08  #Rated capacity
        self.Vn = 3.6  #Nominal voltage
        self.Vmax = 4.2  #Max voltage (Charging)
        self.Vmin = 2.5  #Min voltage (Discharging)
        self.QcompPS = 0  #Capacity computed to charge
        self.QcompEL = 0  #Capacity computed to discharge
        self.QcompPSEL = 0.35 * 2.9
        self.Icut = self.Qn / 50  #Cut off current
        self.soc = soc  #State of charge
        self.id = id

    def setSOC(self, soc):
        self.soc = soc

########################################################################

# Description of the battery model

class ChargeDischarge():
    def __init__(self):
        self.Tdch = 0  # Discharge time
        self.Tch = 0  # Charge time
        self.Trest = 0  #Resting time
        self.N = 0  # Number of cycles
        self.Nc = 0  #number of cycle counts
        self.Vmax_t = 4.5
        self.Vmin_t = 3.0
        self.Imax_t = 0.5
        self.sf = 0.25  #safe factor


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
        
        while not self.done and not killThread :
        
            sem.acquire()
            threading.Timer(0.0,startMeasure,(self.idTest, self.device,self.mode,)).start()
            time.sleep(self.increment)

    def stop(self):
        self.done = True



class estimator():
    def __init__(self,idMeasure,volt,amp,id):
        self.idObserver = id
        self.volt = volt
        self.amp = amp
        self.idMeasure = idMeasure
        self.run()

    def run(self):
        if(self.idObserver==1):
            if CHARGE==True:
                data = neuralNetwork.fnnCh.runOneStepDynamicOnline(self.volt,self.amp)
            else:
                data = neuralNetwork.fnnDch.runOneStepDynamicOnline(self.volt,self.amp)
            g = float(data[0][1])
            x = float(data[0][0])
            databaseBuild.createMeasureObserver(self.idMeasure,self.idObserver,0,0,0,0,g,x)
            pass
        if(self.idObserver==3):
            data = ExtendedKalmanFilter.ekf.runOneStepOnline(self.volt,self.amp,CHARGE)
            x = float(data[0][2][0])
            g = float(data[1][0])
            databaseBuild.createMeasureObserver(self.idMeasure,self.idObserver,0,0,0,0,g,x)
            pass
        if(self.idObserver==4):
            data = stateObserver.observer.nextStep(self.volt,self.amp)
            x = float(data[0])
            g = float(data[1])
            databaseBuild.createMeasureObserver(self.idMeasure,self.idObserver,0,0,0,0,g,x)
            pass
        exit()

class socThread():
    def __init__(self,cell,current):
        self.cell = cell
        self.current = current
        self.run()
    def run(self):
        
        if CHARGE == True:
            self.cell.soc = self.cell.soc + self.current/(self.cell.Qn*3600)
        else:
            self.cell.soc = self.cell.soc - self.current/(self.cell.Qn*3600)
        databaseBuild.updateSOC(self.cell.id,self.cell.soc)
        exit()
        
########################################################################
class HppcProfile():
    def __init__(self):
        self.step = 0
        self.ampl = [0.25, 0.5, 1.0, 1.5]
        self.timeResting = 10*60
        self.timePulsing = 55

    def getAmpl(self):
        record = self.ampl[self.step]
        self.step = self.step + 1
        if (self.step == 4):
            self.step = 0
        return record
    def getTimeResting(self):
        return self.timeResting
    def getTimePulsing(self):
        return self.timePulsing
 

class RandomProfile():
    def __init__(self):
        self.ampl = 0
        self.timeResting = 0
        self.timePulsing = 0

    def getAmpl(self):
        self.ampl = random.uniform(0.1, 1.5)
        return self.ampl
    def getTimeResting(self):
        self.timeResting = random.uniform(5*60, 10*60)
        # self.timeResting = random.uniform(30, 60)
        return self.timeResting
    def getTimePulsing(self):
        self.timePulsing = random.uniform(30, 120)
        return self.timePulsing

class PulseProfile():
    def __init__(self):
        self.ampl = 0
        self.timeResting = 0
        self.timePulsing = 0

    def setAmpl(self,c_rate):
        self.ampl = c_rate/100
    def getAmpl(self):
        return self.ampl
    def getTimeResting(self):
        self.timeResting = (5/10)*60*60
        return self.timeResting
    def getTimePulsing(self):
        self.timePulsing = (5/float(self.ampl))*60*60
        return self.timePulsing

class ConstantProfile():
    def __init__(self):
        self.ampl = 1
        self.timeResting = 0
        self.timePulsing = 0
    
    def setAmpl(self,c_rate):
        self.ampl = c_rate/100
    def getAmpl(self):
        return self.ampl
    def getTimeResting(self):
        self.timeResting = 0
        return self.timeResting
    def getTimePulsing(self):
        self.timePulsing = 100*60*60*60
        return self.timePulsing

class CCCVProfile():
    def __init__(self):
        self.ampl = 2
        self.timeResting = 0
        self.timePulsing = 0

    def setAmpl(self,crate):
        self.ampl=crate

    def getAmpl(self):
        return self.ampl
    def getTimeResting(self):
        self.timeResting = 1000*60*60
        return self.timeResting
    def getTimePulsing(self):
        self.timePulsing = 25
        return self.timePulsing

class DSTProfile():
    def __init__(self):
        self.stepAmpl = 0
        self.ampl = [0.25, 0.5, 1.0, 1.5]
        self.stepRest=0
        self.timeResting = [0,0,0,30*60]
        self.timePulsing = 55

    def getAmpl(self):
        record = self.ampl[self.stepAmpl]
        self.stepAmpl = self.stepAmpl + 1
        if (self.stepAmpl == 4):
            self.stepAmpl = 0
        return record
    def getTimeResting(self):
        record = self.timeResting[self.stepRest]
        self.stepRest = self.stepRest + 1
        if (self.stepRest == 4):
            self.stepRest = 0
        return record
    def getTimePulsing(self):
        return self.timePulsing 
    
########################################################################

cell = Cell()
devices = MeasuringDevice(POWER_SUPPLY, ELECTRONIC_LOAD)
initDevice(devices)
param = ChargeDischarge()
randomProfile = RandomProfile()
hppcProfile = HppcProfile()
pulseProfile = PulseProfile()
constantProfile = ConstantProfile()
cccvProfile = CCCVProfile()
interrupt = None
atexit.register(exitProg)



#TODO send the message



def startTestDischarge(profile,idTest):

    #we start the measure sequencer
    
    #output(1, devices.electLoad, "EL")
    #thread = Thread(target=Counter, args=(1,))
    startProfileEL(0, 5, devices.electLoad)
    interrupt = Thread(target=Counter, args=(SAMPLING_RATE,idTest,devices.electLoad,"EL",))
    interrupt.start()
    #interrupt = Counter(SAMPLING_RATE,idTest,devices.electLoad,"EL")
    while (True):
        
        sem.acquire()
        startTime = time.time()
        startProfileEL(profile.getAmpl()*cell.Qn, 5, devices.electLoad)
        
        #configELWrite(devices.electLoad)
        #configELModeQuery(devices.electLoad)
        timePulsing = profile.getTimePulsing()
        print(timePulsing)
        # config the ouput
        #time.sleep(1)
        output(1, devices.electLoad, "EL")

        sem.release()
        while (time.time() - startTime < timePulsing):
            print("timePulsing")
            #we wait the time
            
            sem.acquire()
            
            voltage = configMeasureQuery(devices.electLoad, "VOLT")
            sem.release()
            
            voltage = str(round(float(voltage), 3))
            global killThread
            if(float(voltage) <= cell.Vmin or killThread):
                killThread = True
               # print("Voltage is too low")
                
                #print("We turn off everything before leaving")
                sem.acquire()
                
                output(0, devices.electLoad, "EL")
                sem.release()
                
                sendMessage.sendMessage("Test is over")
                exit()
            time.sleep(SAMPLING_RATE)

        timeResting = profile.getTimeResting()
        print(timeResting)
        # config the ouput
        startTime = time.time()
        
        if(time.time() - startTime < timeResting):#it's always true but not for the DST profile ( check the trick )
            sem.acquire()
            output(0, devices.electLoad, "EL")
            sem.release()
        
        while (time.time() - startTime < timeResting):
            print("timeResting")
            if(killThread):
                #interrupt.stop()
                exit()
            #we wait the time
            time.sleep(SAMPLING_RATE)



def startTestCharge(idTest,cRate):
    #profile is always CC-CV
    #we start the time
    cccvProfile.setAmpl(cRate)
    interrupt = Thread(target=Counter, args=(SAMPLING_RATE,idTest,devices.pwrSupply,"PS",))
    interrupt.start()
    sem.acquire()
    startTime = time.time()
        
    startProfilePS(cccvProfile.getAmpl(),devices.pwrSupply)
    timePulsing = cccvProfile.getTimePulsing()
    timeResting = cccvProfile.getTimeResting()
    output(1,devices.pwrSupply,"PS")
    sem.release()
    while (True):
        while(time.time() - startTime < timePulsing):
            sem.acquire()
            output(1,devices.pwrSupply,"PS")
            sem.release()
            time.sleep(SAMPLING_RATE)
        startTime = time.time()
        while(time.time() - startTime < timeResting):
            sem.acquire()
            current = configMeasureQuery(devices.pwrSupply, "CURR")
            current = str(round(float(current), 3))
            sem.release()
            if(float(current)<=cell.Icut):
                sem.acquire()
                output(0, devices.pwrSupply, "PS")
                global killThread
                killThread = True
                sem.release()
                sendMessage.sendMessage("Test is over")
                exit()
            time.sleep(SAMPLING_RATE)
        #we wait the time


def setTest(idTest,observer):
    result=databaseBuild.getTest(idTest)
    print("result : " + str(result))
    crate = result["cRate"]
    observers = result["observers"]
    cells = result["cells"]
    result = result["action"]["id_action"]

    global CELLS
    for cell in cells:
        newCell = Cell(cell[0],cell[2])
        CELLS.append(newCell)
    

    
    global IDTEST
    global FNN
    global EKF
    global OBSERVER
    global CHARGE
    CHARGE = False
    IDTEST=idTest
    for obs in observers:
        if obs[0]==1:
            FNN = True
            EKF = False
            OBSERVER =False
        if obs[0]==3:
            EKF = True
            OBSERVER =False
            FNN = False
        if obs[0]==4:
            OBSERVER=True
            FNN = False
            EKF = False
    if result==2 or result==3 or result ==4 or result==5 or result==6:
        for cell in CELLS:
            if(cell.soc==None):
                cell.setSOC(1)


    if result==1:
        CHARGE = True
        for cell in CELLS:
            if(cell.soc==None):
                cell.setSOC(0)
        startTestCharge(idTest,crate)
    elif result==2:
        profile = RandomProfile()
        startTestDischarge(profile,idTest)
    elif result==3:
        profile = PulseProfile()
        print(crate)
        profile.setAmpl(crate)
        startTestDischarge(profile,idTest)
    elif result==4:
        profile = HppcProfile()
        startTestDischarge(profile,idTest)
    elif result==5:
        profile=ConstantProfile()
        profile.setAmpl(crate)
        startTestDischarge(profile,idTest)
    elif result==6:
        profile=DSTProfile()
        startTestDischarge(profile,idTest)
