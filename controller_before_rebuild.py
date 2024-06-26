###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################
import pyvisa as visa
import socket
import time
import random
import databaseBuild
import EKFModel
import stateObserver
import sendMessage


###################################################################
##                   G L O B A L   C O N S T A N T               ##
###################################################################
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 5000  # Port to listen on (non-privileged ports are > 1023)
PWRSUPPLY = 'USB0::0x2EC7::0x6700::802259073777170159::INSTR'
ELECTLOAD = 'USB0::0x1AB1::0x0E11::DL3A250700137::INSTR'



###################################################################
##                   G L O B A L   V A R I A B L E S             ##
###################################################################
startTimePS = None
cell = None
RandAmpl = 0
RandTime = 0
RandTrest = 0
hppc = None
id_test = None
timePulsing = 0
ekf = EKFModel.EKF(None,1)

###################################################################
##            F U N C T I O N    D E C L A R A T I O N           ##
###################################################################
def calculIt(value):
    return float(value) * cell.Qn / 100


def calculImax(It):
    return 1.1 * It


def calculQtype(It):
    return round(It / cell.Qn, 1)


def messageMeasureSerialize(profile, flag):
    if (profile == "Ch"):
        sendMeas = 'measPS;' + '0'
    if (profile == "Dch"):
        sendMeas = 'measEL;' + '0'
    if (profile == "DchCh"):
        sendMeas = 'measPSEL;' + '0'
    if (profile == "StopPS"):
        sendMeas = 'measPS;' + str(round(time.time() - startTimePS, 1))
    sendMeas = sendMeas + ';' + '0' + ';' + '0' + ';' + '0' + ';' + '0' + ';' + flag.flagType
    return sendMeas


###################################################################
##            S T R U C T    D E C L A R A T I O N               ##
###################################################################


class MeasuringDevice():
    def __init__(self, host, port, pwrsuplly, electload):
        self.host = host
        self.port = port
        self.pwrSupply = None
        self.electLoad = None
        self.pwrSupply_info = None
        self.electLoad_info = None
        self.pwrSupplyId = pwrsuplly
        self.electLoadId = electload

    def initialisation(self):
        rm = visa.ResourceManager()
        print(rm.list_resources())
        self.pwrSupply = rm.open_resource(self.pwrSupplyId)
        self.electLoad = rm.open_resource(self.electLoadId)
        self.pwrSupply_info = self.pwrSupply.query('*IDN?')
        self.electLoad_info = self.electLoad.query('*IDN?')

    def configPSStart(self, It):
        print(It)
        self.pwrSupply.write("SOUR:VOLTage:LEVel " + str(cell.Vmax))
        self.pwrSupply.write("SOUR:CURRent:LEVel " + str(It))

    def configELStart(self, It):
        self.electLoad.write("SOUR:FUNC CURR")
        self.electLoad.write("SOUR:CURR:LEV:IMM " + str(It))
        self.electLoad.write("SOUR:CURR:RANG 40")
        self.electLoad.write("SOUR:CURR:SLEW 0.001")
        self.electLoad.write("SOUR:CURR:VON " + str(cell.Vmin))
        self.electLoad.write("SOUR:CURR:VLIM " + str(cell.Vmax))
        self.electLoad.write("SOUR:CURR:ILIM " + str(calculImax(It)))

    def configELRand(self, RandAmpl):
        self.electLoad.write("SOUR:FUNC CURR")
        self.electLoad.write("SOUR:CURR:LEV:IMM " + str(RandAmpl*cell.Qn))
        self.electLoad.write("SOUR:CURR:RANG 40")
        self.electLoad.write("SOUR:CURR:SLEW 0.001")
        self.electLoad.write("SOUR:CURR:VON " + str(cell.Vmin))
        self.electLoad.write("SOUR:CURR:VLIM " + str(cell.Vmax))
        self.electLoad.write("SOUR:CURR:ILIM 5")

    def configELStep(self):
        self.electLoad.write("SOUR:FUNC CURR")
        self.electLoad.write("SOUR:CURR:LEV:IMM " + str(hppc.increment()*cell.Qn))
        self.electLoad.write("SOUR:CURR:RANG 40")
        self.electLoad.write("SOUR:CURR:SLEW 0.001")
        self.electLoad.write("SOUR:CURR:VON " + str(cell.Vmin))
        self.electLoad.write("SOUR:CURR:VLIM " + str(cell.Vmax))
        self.electLoad.write("SOUR:CURR:ILIM 5")

    def configEL40(self, It, chargeDischarge):
        self.electLoad.write("SOUR:CURR:RANG 40")
        self.electLoad.write("SOUR:FUNC CURR")
        self.electLoad.write("SOUR:CURR:LEV:IMM " + str(It))
        self.electLoad.write("SOUR:CURR:SLEW 0.01")
        self.electLoad.write("SOUR:CURR:VON " + str(cell.Vmin))
        self.electLoad.write("SOUR:CURR:VLIM " + str(chargeDischarge.Vmax_t))
        self.electLoad.write("SOUR:CURR:ILIM " + str(calculImax(It)))

    def configPS(self, output):
        self.pwrSupply.write('OUTPut:STATe ' + str(output))

    def configEL(self, output):
        self.electLoad.write('INPut:STATe ' + str(output))

    def configPSEL(self, Output, Input):
        self.configPS(Output)
        self.configEL(Input)

    def configMeasureWrite(self, device):
        if (device == "PS"):
            self.pwrSupply.write('MEASure:VOLTage?')
            self.pwrSupply.write('MEASure:CURRent?')
        if (device == "EL"):
            self.electLoad.write('MEASure:VOLTage?')
            self.electLoad.write('MEASure:CURRent?')

    def configMeasureQuery(self, device, measure):
        if (device == "PS"):
            if (measure == "VOLT"):
                return self.pwrSupply.query('MEASure:VOLTage?')
            if (measure == "CURR"):
                return self.pwrSupply.query('MEASure:CURRent?')
        if (device == "EL"):
            if (measure == "VOLT"):
                return self.electLoad.query('MEASure:VOLTage?')
            if (measure == "CURR"):
                return self.electLoad.query('MEASure:CURRent?')

    def configPSStatusQuery(self):
        return self.pwrSupply.query('STATus:QUEStionable:CONDition?')

    def configELStatusQuery(self):
        return self.electLoad.query('STAT:QUES:COND?')

    def configELModeQuery(self):
        return self.electLoad.query('SOUR:FUNC?')

    def configELWrite(self):
        self.electLoad.write('STAT:QUES:ENAB 32271')


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

class Flag():
    def __init__(self):
        self.flagStt = "Waiting"
        self.flagDvc = "None"
        self.flagLoad = "None"
        self.flagSour = "None"
        self.flagType = "None"
        self.flagCyc = "None"

    #TODO : complete the flag class with methods to change the flags according to the state of the flag in the code below

    def setFlagSourConst(self):
        self.flagSour = "Const"

    def setFlagSourPulse(self):
        self.flagSour = "Pulse"

    def setFlagSourRand(self):
        self.flagSour = "Random"

    def setFlagSourStep(self):
        self.flagSour = "Step"

    def setFlagLoadConst(self):
        self.flagLoad = "Const"

    def setFlagLoadPulse(self):
        self.flagLoad = "Pulse"

    def setFlagLoadRand(self):
        self.flagLoad = "Random"

    def setFlagLoadStep(self):
        self.flagLoad = "Step"

    def setFlagDvcPS(self):
        self.flagDvc = "PS"

    def setFlagDvcEL(self):
        self.flagDvc = "EL"

    def setFlagDvcSEL(self):
        self.flagDvc = "PSEL"

    def setFlagType(self, profile, mode, Q_type):
        if (mode == None):
            self.flagType = profile + "-" + str(Q_type) + "C"
        else:
            self.flagType = profile + "-" + mode + "-" + str(Q_type) + "C"

    def setflagCycCh(self):
        self.flagCyc = "Ch"  #flagCyc is Dch to discharge, Ch to charge and Rest to resting (RestDch, RestCh)


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

    def handlerChDch(self, profile, mode, flag, value, measuringDevice, cdParameters):

        It = calculIt(value)
        print(It)
        Q_type = calculQtype(It)

        if (profile == "Ch" and mode == "Const"):  #Configuring Charge in constant mode
            flag.setFlagSourConst()
            flag.setFlagDvcPS()
            measuringDevice.configPSStart(It)

        elif (profile == "Ch" and mode == "Pulse"):  #Configuring Charge in constant mode
            flag.setFlagSourPulse()
            flag.setFlagDvcPS()
            measuringDevice.configPSStart(It)
            print(measuringDevice.pwrSupply.query("CURR? MIN"))  #for what ?

        elif (profile == "Dch" and mode == "Const"):  #Configuring Discharge in constant mode
            flag.setFlagLoadConst()
            flag.setFlagDvcEL()
            measuringDevice.configELStart(It)

        elif (profile == "Dch" and mode == "Pulse"):  #Configuring Discharge in pulse mode
            flag.setFlagLoadPulse()
            flag.setFlagDvcEL()
            measuringDevice.configELStart(It)


        elif (profile == "Dch" and mode == "Random"):
            flag.setFlagLoadRand()
            flag.setFlagDvcEL()
            measuringDevice.configELRand(random.uniform(0.1, 1.5))

        elif (profile == "Dch" and mode == "Step"):
            flag.setFlagLoadStep()
            flag.setFlagDvcEL()
            measuringDevice.configELStep()


        elif (profile == "DchCh" and mode[0:5] == "Cycle"):  #Configuring Discharge in pulse mode
            N = int(mode[5])
            profile += "-Cyc"
            mode = None
            #TODO : create a function
            cdParameters.Tdch = 600  #(Qn*sf/It)*3600 #In seconds
            cdParameters.Tch = 600  #(Qn*sf/It)*3600 #In seconds

            cdParameters.Trest = cdParameters.Tch
            print(cdParameters.Trest)
            measuringDevice.configPSStart(It)
            measuringDevice.configEL40(It, cdParameters)
            flag.setFlagDvcPSEL()
            flag.setflagCycCh()
        else:
            return None

        flag.setFlagType(profile, mode, Q_type)
        return messageMeasureSerialize(profile, flag).encode()


########################################################################
class Hppc():
    def __init__(self):
        self.step = 0
        self.ampl = [0.25, 0.5, 1.0, 1.5]

    def increment(self):
        record = self.ampl[self.step]
        self.step = self.step + 1
        if (self.step == 4):
            self.step = 0
        return record

########################################################################

#instanciate the classes
measuringDevice = MeasuringDevice(HOST, PORT, PWRSUPPLY, ELECTLOAD)
cdParameters = ChargeDischarge()
cell = Cell()
flag = Flag()
hppc = Hppc()
#start the databaseBuild.py file


#initialise the measuring devices
measuringDevice.initialisation()

# print the information of the measuring devices
print(measuringDevice.pwrSupply_info)
print(measuringDevice.electLoad_info)

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        #TODO : change it into a function

        s.bind((HOST, PORT))  #Start TCP communication
        s.listen()  # Waiting some query of the client
        conn, addr = s.accept()  #Accept query of the  client

        with conn:
            data = conn.recv(1024)  #Read data sent by client

            #TODO : change it into a function 
            msg_nodeRed = data.decode("utf-8")  #Decode binary to string
            infos = msg_nodeRed.split(';')
            profile = infos[0]  #Ch - charge, Dch - discharge, Start, Stop, Meas
            value = infos[1]  #Percentual of currente based on Qn (It = values*Qn/100)
            mode = infos[2]  #Constant or Pulsed or Cycled

            #Ch / Dch  -  Pulse / Const
            if profile == "Dch" or profile == "Ch":
                print(profile)
                sendMeasure = cdParameters.handlerChDch(profile, mode, flag, value, measuringDevice, cdParameters)
                if (profile == "Dch" and mode == "Pulse"):  #Configuring Discharge in pulse mode
                    timePulsing = (5/float(value))*60*60
                    #timePulsing = 20
                    print(timePulsing)
                if sendMeasure != None:
                    conn.sendall(sendMeasure)

                    #Conditions to charge moment (PS = Power supply)
            if (profile == "StartPS" and (flag.flagSour == "Const" or flag.flagSour == "Pulse")):
                flag.flagStt = "StartPS"
                startTimePS = time.time()
                if (flag.flagSour == "Pulse"):
                    startTimePulsePS = time.time()
                    stateSignal = True

            if (profile == "StopPS"):
                flag.flagStt = "StopPS"
                flag.flagSour = "None"
                flag.flagLoad = "None"
                flag.flagDvc = "None"
                flag.flagType = "None"
                measuringDevice.configPS(0)
                conn.sendall(messageMeasureSerialize(profile, flag).encode())

            if (flag.flagStt == "StartPS" and flag.flagDvc == "PS" and profile == "Meas"):
                elapsedTimePS = time.time() - startTimePS
                voltPwrSupply = str(round(float(measuringDevice.configMeasureQuery("PS", "VOLT")), 3))
                cell.QcompPS = cell.QcompPS + float(measuringDevice.configMeasureQuery("PS", "CURR")) / 3600
                ampePwrSupply = str(round(float(measuringDevice.configMeasureQuery("PS", "CURR")), 3))
                cell.QcompPS = round(float(cell.QcompPS), 8)

                if (elapsedTimePS >= 2 and flag.flagSour == "Const"):
                    measuringDevice.configPS(1)
                    if (elapsedTimePS >= 25):
                        if (float(measuringDevice.configMeasureQuery("PS", "CURR")) <= cell.Icut):  #QcompPS >= Qn or
                            measuringDevice.configPS(0)
                            sendMessage.send_message() #If works, shows for Tomas
                            flag.flagStt = "StopPS"
                            voltPwrSupply = '0'
                            ampePwrSupply = '0'
                            cell.QcompPS = 0

                if (elapsedTimePS >= 2 and flag.flagSour == "Pulse"):
                    if (stateSignal == True):
                        
                        measuringDevice.configPS(1)
                    elif (stateSignal == False):
                        measuringDevice.configPS(0)
                    pulseWidth = time.time() - startTimePulsePS
                    if (pulseWidth >= 300):
                        stateSignal = not stateSignal
                        startTimePulsePS = time.time()
                    if (cell.QcompPS >= cell.Qn):
                        measuringDevice.configPS(0)
                        sendMessage.send_message()
                        flag.flagStt = "StopPS"
                        cell.QcompPS = 0
                        voltPwrSupply = '0'
                        ampePwrSupply = '0'
                        modePwrSupply = '0'


                #TODO : make a function for the serialisation 
                modePwrSupply = measuringDevice.configPSStatusQuery()
                data = ekf.runOneStepOnline(float(voltPwrSupply.split('\n')[0]),-float(ampePwrSupply.split('\n')[0]))
                x = data[0]
                g = data[1]
                #print(x)
                #print(g)
                sendMeasPS = 'measPS;' + str(round(elapsedTimePS, 0)) + ';' + voltPwrSupply.split('\n')[0] + ';' + \
                             ampePwrSupply.split('\n')[0] + ';' + modePwrSupply.split('\n')[0] + ';' + str(
                    cell.QcompPS) + ';' + flag.flagType + ';' + str(x[2][0])+ ';'+ str(g[0])
                #databaseBuild.createMeasure(id_test, round(elapsedTimePS, 0), ampePwrSupply.split('\n')[0],
                                            #voltPwrSupply.split('\n')[0], 0, 0)

                conn.sendall(sendMeasPS.encode())

            #Conditions to discharge moment (EL = Eletronic Load)
            if (profile == "StartEL" and (
                    flag.flagLoad == "Const" or flag.flagLoad == "Pulse" or flag.flagLoad == "Random" or flag.flagLoad == "Step")):
                flag.flagStt = "StartEL"
                measuringDevice.configELWrite()
                modeElectLoad = measuringDevice.configELModeQuery()
                startTimeEL = time.time()

                if (flag.flagLoad == "Pulse"):
                    startTimePulseEL = time.time()
                    stateSignal = True

                if (flag.flagLoad == "Random"):
                    startTimeRandEL = time.time()
                    stateSignal = True
                    #RandAmpl = random.uniform(0.1,1.5)#generate random number between and 0.1 and 1.5
                    #RandTrest = random.uniform(15*60,30*60)#generate random number between and 15*60 and 30*60
                    RandTime = round(random.uniform(30, 120))  #generate random number between and 30 and 120
                    print("time pulsing : " + str(RandTime))

                if (flag.flagLoad == "Step"):
                    startTimeStepEL = time.time()
                    stateSignal = True

                    # time.sleep(0.2)

            if (profile == "StopEL"):
                hppc.step = 0 
                flag.flagStt = "StopEL"
                flag.flagLoad = "None"
                flag.flagDvc = "None"
                flag.flagType = "None"
                measuringDevice.configEL(0)
                modeElectLoad = 'Off\n'

                #TODO : make a function for the serialisation
                sendMeasEL = 'measEL;' + str(round(time.time() - startTimeEL, 1)) + ';' + str(0) + ';' + str(
                    0) + ';' + str(0) + ';' + str(0) + ';' + modeElectLoad.split('\n')[0] + ';' + flag.flagType
                #databaseBuild.createMeasure(id_test, round(time.time() - startTimeEL, 1), 0, 0, 0, 0)
                conn.sendall(sendMeasEL.encode())

            if (flag.flagStt == "StartEL" and flag.flagDvc == "EL" and profile == "Meas"):
                elapsedTimeEL = time.time() - startTimeEL
                voltElectLoad = measuringDevice.configMeasureQuery("EL", "VOLT")
                voltElectLoad = str(round(float(voltElectLoad), 3))

                ampeElectLoad = measuringDevice.configMeasureQuery("EL", "CURR")

                cell.QcompEL = cell.QcompEL + float(ampeElectLoad) / 3600

                ampeElectLoad = str(round(float(ampeElectLoad), 3))
                cell.QcompEL = round(float(cell.QcompEL), 8)

                if (elapsedTimeEL >= 2 and flag.flagLoad == "Const"):
                    measuringDevice.configEL(1)
                    if (float(voltElectLoad) <= cell.Vmin):  # QcompEL >= 0.65*Qn or  QcompEL >= Qn or
                        measuringDevice.configEL(0)
                        sendMessage.send_message()
                        flag.flagStt = "StopEL"
                        cell.QcompEL = 0
                        voltElectLoad = '0'
                        ampeElectLoad = '0'
                        modeElectLoad = 'Off\n'
                        # time.sleep(0.2)

                if (elapsedTimeEL >= 2 and flag.flagLoad == "Pulse"):
                    if (stateSignal == True):
                        measuringDevice.configEL(1)
                    elif (stateSignal == False):
                        measuringDevice.configEL(0)
                    pulseWidth = time.time() - startTimePulseEL
                    if ((pulseWidth >= 900 and stateSignal == False) or (pulseWidth >= timePulsing and stateSignal == True)):
                        stateSignal = not stateSignal
                        startTimePulseEL = time.time()

                    if (float(voltElectLoad) <= cell.Vmin):
                        measuringDevice.configEL(0)
                        sendMessage.send_message()
                        flag.flagStt = "StopEL"
                        cell.QcompEL = 0
                        voltElectLoad = '0'
                        ampeElectLoad = '0'
                        modeElectLoad = 'Off\n'
                        # time.sleep(0.2)

                if (elapsedTimeEL >= 2 and flag.flagLoad == "Random"):  #Resting time ?? + Amplitude not found
                    if (stateSignal == True):
                        measuringDevice.configEL(1)
                    elif (stateSignal == False):
                        measuringDevice.configEL(0)
                    pulseWidth = time.time() - startTimeRandEL
                    if (pulseWidth >= RandTime and stateSignal == True):
                        stateSignal = not stateSignal
                        startTimeRandEL = time.time()
                        RandTrest = round(
                            random.uniform(5 * 60, 10 * 60))  #generate random number between and 15*60 and 30*60
                        print("time resting : " + str(RandTrest))
                    if (pulseWidth >= RandTrest and stateSignal == False):
                        stateSignal = not stateSignal
                        startTimeRandEL = time.time()
                        RandTime = round(random.uniform(30, 120))  #generate random number between and 30 and 12
                        RandAmpl = random.uniform(0.1, 1.5)  #generate random number between and 0.1 and 1.5
                        print("Amplitude : "+str(RandAmpl))
                        print("time pulsing : " + str(RandTime))
                        measuringDevice.configELRand(RandAmpl)
                    if (float(voltElectLoad) <= cell.Vmin):
                        measuringDevice.configEL(0)
                        sendMessage.send_message()
                        flag.flagStt = "StopEL"
                        cell.QcompEL = 0
                        voltElectLoad = '0'
                        ampeElectLoad = '0'
                        modeElectLoad = 'Off\n'
                        # time.sleep(0.2)

                if (elapsedTimeEL >= 2 and flag.flagLoad == "Step"):
                    if (stateSignal == True):
                        measuringDevice.configEL(1)
                    elif (stateSignal == False):
                        measuringDevice.configEL(0)
                    pulseWidth = time.time() - startTimeStepEL
                    if (pulseWidth >= 10*60 and stateSignal == False):
                        stateSignal = not stateSignal
                        startTimeStepEL = time.time()
                        measuringDevice.configELStep()

                    elif(pulseWidth >= 55 and stateSignal == True):
                        stateSignal = not stateSignal
                        startTimeStepEL = time.time()


                    if (float(voltElectLoad) <= cell.Vmin):
                        measuringDevice.configEL(0)
                        sendMessage.send_message()
                        flag.flagStt = "StopEL"
                        cell.QcompEL = 0
                        voltElectLoad = '0'
                        ampeElectLoad = '0'
                        modeElectLoad = 'Off\n'
                        # time.sleep(0.2)

                statusElectLoad = measuringDevice.configELStatusQuery()
                modeElectLoad = measuringDevice.configELModeQuery()
                #TODO : make a function for the serialisation
                data = ekf.runOneStepOnline(float(voltElectLoad.split('\n')[0]),float(ampeElectLoad.split('\n')[0]))
                x = data[0]
                g = data[1]
                #print(x)
                #print(g)
                sendMeasEL = 'measEL;' + str(round(elapsedTimeEL, 0)) + ';' + voltElectLoad.split('\n')[0] + ';' + \
                             ampeElectLoad.split('\n')[0] + ';' + statusElectLoad.split('\n')[0] + ';' + str(
                    cell.QcompEL) + ';' + modeElectLoad.split('\n')[0] + ';' + flag.flagType+ ';' + str(x[2][0])+ ';'+ str(g[0])
                #databaseBuild.createMeasure(id_test, round(elapsedTimeEL, 0), ampeElectLoad.split('\n')[0],
                                            #voltElectLoad.split('\n')[0], 0, 0)
                conn.sendall(sendMeasEL.encode())