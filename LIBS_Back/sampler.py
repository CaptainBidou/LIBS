###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################
import time
import databaseBuild
import pyvisa as visa
import random
import threading
import atexit


###################################################################
##                   G L O B A L   C O N S T A N T               ##
###################################################################
SAMPLING_RATE = 1  # seconds
POWER_SUPPLY = 'USB0::0x2EC7::0x6700::802259073777170159::INSTR'
ELECTRONIC_LOAD = 'USB0::0x1AB1::0x0E11::DL3A250700137::INSTR'

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
###################################################################
##            F U N C T I O N    D E C L A R A T I O N           ##
###################################################################
def calculIt(value):
    return float(value) * cell.Qn / 100

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
    #wait 1s
    time.sleep(SAMPLING_RATE)
    # send request to the ps
    voltPwrSupply = str(round(float(configMeasureQuery(device, "VOLT")), 3))
    cell.QcompPS = cell.QcompPS + float(configMeasureQuery(device, "CURR")) / 3600
    ampePwrSupply = str(round(float(configMeasureQuery(device, "CURR")), 3))
    cell.QcompPS = round(float(cell.QcompPS), 8)

    #send result to the database
    databaseBuild.createMeasure(idTest, time.time(), ampePwrSupply, voltPwrSupply, 0, 0)
def startProfilePS(value,device):
    print(calculIt(value))
    device.write("SOUR:VOLTage:LEVel " + str(cell.Vmax))
    device.write("SOUR:CURRent:LEVel " + str(calculIt(value)))

def startProfileEL(It,Imax,device):
    device.write("SOUR:FUNC CURR")
    device.write("SOUR:CURR:LEV:IMM " + str(It))
    device.write("SOUR:CURR:RANG 40")
    device.write("SOUR:CURR:SLEW 0.001")
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
    def __init__(self):
        # LIB: NCR18650BD
        self.Qn = 3.08  #Rated capacity
        self.Vn = 3.6  #Nominal voltage
        self.Vmax = 4.2  #Max voltage (Charging)
        self.Vmin = 2.5  #Min voltage (Discharging)
        self.QcompPS = 0  #Capacity computed to charge
        self.QcompEL = 0  #Capacity computed to discharge
        self.QcompPSEL = 0.35 * 2.9
        self.Icut = self.Qn / 50  #Cut current

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
        self.mode = mode
        self.idTest = idTest
        self._run()

    def _run(self):
        print("interrupt")
        startMeasure(self.idTest, self.device,self.mode)
        self.next_t += self.increment
        self.i += 1
        if not self.done:
            threading.Timer(self.next_t - time.time(), self._run).start()

    def stop(self):
        self.done = True

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

    def getAmpl(self):
        self.ampl = 1.5
        return self.ampl
    def getTimeResting(self):
        self.timeResting = (5/10)*60*60
        return self.timeResting
    def getTimePulsing(self):
        self.timePulsing = 10*60
        return self.timePulsing

class ConstantProfile():
    def __init__(self):
        self.ampl = 1
        self.timeResting = 0
        self.timePulsing = 0

    def getAmpl(self):
        self.ampl = 1.5
        return self.ampl
    def getTimeResting(self):
        self.timeResting = 0
        return self.timeResting
    def getTimePulsing(self):
        self.timePulsing = 1
        return self.timePulsing

class CCCVProfile():
    def __init__(self):
        self.ampl = 0
        self.timeResting = 0
        self.timePulsing = 0

    def getAmpl(self):
        self.ampl = 1.5
        return self.ampl
    def getTimeResting(self):
        self.timeResting = 0
        return self.timeResting
    def getTimePulsing(self):
        self.timePulsing = 1
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
    interrupt = Counter(SAMPLING_RATE,idTest,devices.electLoad,"EL")
    output(1, devices.electLoad, "EL")
    
    while (True):
        startTime = time.time()
        startProfileEL(profile.getAmpl()*cell.Qn, 5, devices.electLoad)
        configELWrite(devices.electLoad)
        configELModeQuery(devices.electLoad)
        timePulsing = profile.getTimePulsing()
        print(timePulsing)
        # config the ouput
        output(1, devices.electLoad, "EL")
        while (time.time() - startTime < timePulsing):
            print("timePulsing")
            #we wait the time
            voltage = configMeasureQuery(devices.electLoad, "VOLT")
            voltage = str(round(float(voltage), 3))

            if(float(voltage) <= cell.Vmin or killThread):
                print("Voltage is too low")
                output(0, devices.electLoad, "EL")
                output(0, devices.pwrSupply, "PS")
                interrupt.stop()
                print("We turn off everything before leaving")
                exit()
            time.sleep(SAMPLING_RATE)

        timeResting = profile.getTimeResting()
        print(timeResting)
        # config the ouput
        startTime = time.time()
        output(0, devices.electLoad, "EL")
        while (time.time() - startTime < timeResting):
            print("timeResting")
            if(killThread):
                interrupt.stop()
                exit()
            #we wait the time
            time.sleep(SAMPLING_RATE)



def startTestCharge(idTest):
    #profile is always CC-CV
    #we start the time
    startTime = time.time()
    while (True):
        startProfilePS(1,devices.pwrSupply)
        timePulsing = cccvProfile.getTimePulsing()
        startMeasure(idTest,devices.pwrSupply)
        output(1,devices.pwrSupply,"PS")


def setTest(idTest):
    result=databaseBuild.getTestsId(idTest)
    print("result : " + str(result))

    if result[0][2]==1:
        startTestCharge(idTest)
    elif result[0][2]==2:
        pass
    elif result[0][2]==3:
        profile = RandomProfile()
        startTestDischarge(profile,idTest)
    elif result[0][2]==4:
        profile = PulseProfile()
        startTestDischarge(profile,idTest)
    elif result[0][2]==5:
        profile = HppcProfile()
        startTestDischarge(profile,idTest)






