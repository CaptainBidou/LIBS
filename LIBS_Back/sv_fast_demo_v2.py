###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################
import pyvisa as visa
import socket
import time

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


###################################################################
##            F U N C T I O N    D E C L A R A T I O N           ##
###################################################################
def calculIt(value):
    return float(value)*Cell.Qn/100

def calculImax(It):
    return 1.1*It

def calculQtype(It):
    return round(It/Cell.Qn,1)

def messageMeasureSerialize(profile,flag):
    if(profile == "Ch"):
        sendMeas = 'measPS;'
    if(profile == "Dch"):
        sendMeas = 'measEL;'
    sendMeas    =   sendMeas+ '0' + ';' + '0' + ';' + '0' + ';' + '0' + ';' + '0' + ';' + flag.flagType
    return sendMeas


###################################################################
##            S T R U C T    D E C L A R A T I O N               ##
###################################################################
class MeasuringDevice():
    def __init__(self, host, port, pwrsuplly, electload):
        self.host = host
        self.port = port
        self.pwrSupply=None
        self.electLoad=None
        self.pwrSupply_info=None
        self.electLoad_info=None
        self.pwrSupplyId = pwrsuplly
        self.electLoadId = electload

    def initialisation(self):
        rm = visa.ResourceManager()
        print(rm.list_resources())
        self.pwrSupply = rm.open_resource(self.pwrSupplyId)
        self.electLoad = rm.open_resource(self.electLoadId)
        self.pwrSupply_info = self.pwrSupply.query('*IDN?')
        self.electLoad_info = self.electLoad.query('*IDN?')
    
    def configPS(self,It):
        self.pwrSupply.write("SOUR:VOLTage:LEVel " + str(Cell.Vmax))
        self.pwrSupply.write("SOUR:CURRent:LEVel " + str(It))
    
    def configEL(self,It):
        self.electLoad.write("SOUR:FUNC CURR")
        self.electLoad.write("SOUR:CURR:LEV:IMM " + str(It))
        self.electLoad.write("SOUR:CURR:RANG 4")
        self.electLoad.write("SOUR:CURR:SLEW 0.01")
        self.electLoad.write("SOUR:CURR:VON " + str(Cell.Vmin))
        self.electLoad.write("SOUR:CURR:VLIM " + str(Cell.Vmax))
        self.electLoad.write("SOUR:CURR:ILIM " + str(calculImax(It)))
        


class Cell():
    def __init__(self):
        # LIB: NCR18650BD
        self.Qn = 2.9 #Rated capacity
        self.Vn = 3.6 #Nominal voltage
        self.Vmax = 4.2 #Max voltage (Charging)
        self.Vmin = 2.5 #Min voltage (Discharging)
        self.QcompPS = 0 #Capacity computed to charge
        self.QcompEL = 0 #Capacity computed to discharge
        self.QcompPSEL = 0.35*2.9
        self.Icut = self.qn/50 #Cut current


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

    def setFlagLoadConst(self):
        self.flagLoad = "Const"
    def setFlagLoadPulse(self):
        self.flagLoad = "Pulse"
    
    def setFlagDvcPS(self):
        self.flagDvc = "PS"
    def setFlagDvcEL(self):
        self.flagDvc = "EL"

    def setFlagType(self,profile,mode,Q_type):
        self.flagType = profile + "-" + mode + "-" + str(Q_type) + "C"


# Description of the battery model

class ChargeDischarge():
    def __init__(self):
        self.Tdch = 0 # Discharge time
        self.Tch = 0 # Charge time
        self.Trest = 0 #Resting time
        self.N = 0 # Number of cycles
        self.Nc = 0 #number of cycle counts
        self.Vmax_t = 4.5
        self.Vmin_t = 3.0
        self.Imax_t = 0.5
        self.sf = 0.25 #safe factor 
   
    def configChDch(self,profile,mode,flag,value,measuringDevice):

        It = calculIt(value)
        Q_type = calculQtype(It)

        if(profile == "Ch" and mode == "Const"): #Configuring Charge in constant mode
            flag.setFlagSourConst()
            flag.setFlagDvcPS()
            measuringDevice.configPS(It) 

        if(profile == "Ch" and mode == "Pulse"): #Configuring Charge in constant mode
            flag.setFlagSourPulse()
            flag.setFlagDvcPS()
            measuringDevice.configPS(It)
            print(measuringDevice.pwrSupply.query("CURR? MIN"))#for what ?

        if(profile == "Dch" and mode == "Const"): #Configuring Discharge in constant mode
            flag.setFlagLoadConst()
            flag.setFlagDvcEL()
            measuringDevice.configEL(It)
            
        if(profile == "Dch" and mode == "Pulse"): #Configuring Discharge in pulse mode
            flag.setFlagLoadPulse()
            flag.setFlagDvcEL()
            measuringDevice.configEL(It)
            modeElectLoad = measuringDevice.electLoad.query('SOUR:FUNC?')#for what ?
        
        flag.setFlagType(profile,mode,Q_type)    
        return messageMeasureSerialize(profile,flag).encode()

#instanciate the classes
measuringDevice = MeasuringDevice(HOST, PORT, PWRSUPPLY, ELECTLOAD)
cdParameters = ChargeDischarge()
cell = Cell()
flag = Flag()


#initialise the measuring devices
measuringDevice.initialisation()

# print the information of the measuring devices
print(measuringDevice.pwrSupply_info)
print(measuringDevice.electLoad_info)


while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #TODO : change it into a function
        s.bind((HOST, PORT)) #Start TCP communication
        s.listen() # Waiting some query of the client 
        conn, addr = s.accept() #Accept query of the  client

        with conn:
            data = conn.recv(1024) #Read data sent by client

            #TODO : change it into a function 
            msg_nodeRed = data.decode("utf-8") #Decode binary to string
            infos = msg_nodeRed.split(';')

            profile = infos[0] #Ch - charge, Dch - discharge, Start, Stop, Meas
            value = infos[1] #Percentual of currente based on Qn (It = values*Qn/100)
            mode = infos[2] #Constant or Pulsed or Cycled
            

            #Ch / Dch  -  Pulse / Const
            sendMeasure = cdParameters.configChDch(profile,mode,flag,value,measuringDevice)
            conn.sendall(sendMeasure)   

            if(profile == "DchCh" and mode[0:5] == "Cycle"):
                N = int(mode[5])
                It = float(value)*Qn/100
                Tdch = 600 #(Qn*sf/It)*3600 #In seconds
                Tch = 600#(Qn*sf/It)*3600 #In seconds
                Trest = Tch
                print(Trest)
                Imax = 1.1*It


                
                measuringDevice.configPS(It)
                
                electLoad.write("SOUR:CURR:RANG 40")
                electLoad.write("SOUR:FUNC CURR")
                electLoad.write("SOUR:CURR:LEV:IMM " + str(It))
                electLoad.write("SOUR:CURR:SLEW 0.01")
                electLoad.write("SOUR:CURR:VON " + str(Vmin))
                electLoad.write("SOUR:CURR:VLIM " + str(Vmax_t))
                electLoad.write("SOUR:CURR:ILIM " + str(Imax))

                Q_type = round(It/Qn,1)

                flagDvc = "PSEL"
                flagCyc = "Ch" #flagCyc is Dch to discharge, Ch to charge and Rest to resting (RestDch, RestCh)

                flagType = "DchCh-Cyc" + "-" + str(Q_type) + "C"
                sendMeasPS = 'measPSEL;'+ '0' + ';' + '0' + ';' + '0' + ';' + str(QcompPSEL) + ';' + '0' + ';' + flagType
                conn.sendall(sendMeasPS.encode())

            #Conditions to charge moment (PS = Power supply)
            if(profile == "StartPS" and (flagSour == "Const" or flagSour == "Pulse")):
                flagStt = "StartPS"
                startTimePS = time.time()
                if(flagSour == "Pulse"):
                    startTimePulsePS = time.time()
                    stateSignal = True
            
            if(profile == "StopPS"):
                flagStt = "StopPS"
                flagSour = "None"
                flagLoad = "None"
                flagDvc = "None"
                flagType = "None"
                pwrSupply.write('OUTPut:STATe 0')
                sendMeasPS = 'measPS;'+ str(round(time.time()-startTimePS,1)) + ';' + str(0) + ';' + str(0) + ';' + str(0) + ';' + str(0) + ';' + flagType
                conn.sendall(sendMeasPS.encode())

            if(flagStt == "StartPS" and flagDvc == "PS" and profile == "Meas"):
                elapsedTimePS = time.time() - startTimePS
                
                voltPwrSupply = pwrSupply.query('MEASure:VOLTage?')
                voltPwrSupply = str(round(float(voltPwrSupply),3))

                ampePwrSupply = pwrSupply.query('MEASure:CURRent?')

                QcompPS = QcompPS + float(ampePwrSupply)/3600

                ampePwrSupply = str(round(float(ampePwrSupply),3))
                QcompPS = round(float(QcompPS),8)

                if(elapsedTimePS >= 2 and flagSour == "Const"):
                    pwrSupply.write('OUTPut:STATe 1')
                    if(elapsedTimePS >=25):
                        ImeasCut = pwrSupply.query('MEASure:CURRent?')
                        if(float(ImeasCut) <= Icut): #QcompPS >= Qn or
                            pwrSupply.write('OUTPut:STATe 0')
                            flagStt = "StopPS"
                            voltPwrSupply = '0'
                            ampePwrSupply = '0'
                            QcompPS = 0

                if(elapsedTimePS >= 2 and flagSour == "Pulse"):
                    if(stateSignal == True):
                        pwrSupply.write('OUTPut:STATe 1')
                    elif(stateSignal == False):
                        pwrSupply.write('OUTPut:STATe 0')
                    pulseWidth = time.time() - startTimePulsePS
                    if(pulseWidth >= 300):
                        stateSignal = not stateSignal
                        startTimePulsePS = time.time()
                    if(QcompPS >= Qn): 
                        pwrSupply.write('OUTPut:STATe 0')
                        flagStt = "StopPS"
                        QcompPS = 0
                        voltPwrSupply = '0'
                        ampePwrSupply = '0'
                        modePwrSupply = '0'
                 
                modePwrSupply = pwrSupply.query('STATus:QUEStionable:CONDition?')
                sendMeasPS = 'measPS;'+ str(round(elapsedTimePS,0)) + ';' + voltPwrSupply.split('\n')[0] + ';' + ampePwrSupply.split('\n')[0] + ';' + modePwrSupply.split('\n')[0] + ';' + str(QcompPS) + ';' + flagType
                conn.sendall(sendMeasPS.encode())

            #Conditions to discharge moment (EL = Eletronic Load)
            if(profile == "StartEL" and (flagLoad == "Const" or flagLoad == "Pulse")):
                flagStt = "StartEL"
                electLoad.write('STAT:QUES:ENAB 32271')
                modeElectLoad = electLoad.query('SOUR:FUNC?')
                startTimeEL = time.time()
                if(flagLoad == "Pulse"):
                    startTimePulseEL = time.time()
                    stateSignal = True
            
            if(profile == "StopEL"):
                flagStt = "StopEL"
                flagLoad = "None"
                flagDvc = "None"
                flagType = "None"
                electLoad.write('INPut:STATe 0')
                modeElectLoad = 'Off\n'
                sendMeasEL = 'measEL;'+ str(round(time.time()-startTimeEL,1)) + ';' + str(0) + ';' + str(0) + ';' + str(0) + ';' + str(0) + ';' + modeElectLoad.split('\n')[0] + ';' + flagType
                conn.sendall(sendMeasEL.encode())

            if(flagStt == "StartEL" and flagDvc == "EL" and profile == "Meas"):
                elapsedTimeEL = time.time() - startTimeEL
                voltElectLoad = electLoad.query('MEASure:VOLTage?')
                voltElectLoad = str(round(float(voltElectLoad),3))

                ampeElectLoad = electLoad.query('MEASure:CURRent?')

                QcompEL = QcompEL + float(ampeElectLoad)/3600

                ampeElectLoad = str(round(float(ampeElectLoad),3))
                QcompEL = round(float(QcompEL),8)

                if(elapsedTimeEL >= 2 and flagLoad == "Const"):
                    electLoad.write('INPut:STATe 1')
                    if(float(voltElectLoad) <= Vmin): # QcompEL >= 0.65*Qn or  QcompEL >= Qn or
                        electLoad.write('INPut:STATe 0')
                        flagStt = "StopEL"
                        QcompEL = 0
                        voltElectLoad = '0'
                        ampeElectLoad = '0'
                        modeElectLoad = 'Off\n'
                        # time.sleep(0.2)

                if(elapsedTimeEL >= 2 and flagLoad == "Pulse"):
                    if(stateSignal == True):
                        electLoad.write('INPut:STATe 1')
                    elif(stateSignal == False):
                        electLoad.write('INPut:STATe 0')
                    pulseWidth = time.time() - startTimePulseEL
                    if(pulseWidth >= 300):
                        stateSignal = not stateSignal
                        startTimePulseEL = time.time()
                    if(float(voltElectLoad) <= Vmin): 
                        electLoad.write('INPut:STATe 0')
                        flagStt = "StopEL"
                        QcompEL = 0
                        voltElectLoad = '0'
                        ampeElectLoad = '0'
                        modeElectLoad = 'Off\n'
                        # time.sleep(0.2)

                statusElectLoad = electLoad.query('STAT:QUES:COND?')
                modeElectLoad = electLoad.query('SOUR:FUNC?')
                sendMeasEL = 'measEL;'+ str(round(elapsedTimeEL,0)) + ';' + voltElectLoad.split('\n')[0] + ';' + ampeElectLoad.split('\n')[0] + ';' + statusElectLoad.split('\n')[0] + ';' + str(QcompEL) + ';' + modeElectLoad.split('\n')[0] + ';' + flagType
                conn.sendall(sendMeasEL.encode())

            #Conditions to Cycle test (PSEL = Eletronic Load): Single cycle: Dch->Rest->Ch->Rest
            if(profile == "StartPSEL"):
                flagStt = "StartPSEL"
                startTimePSEL = time.time()
                DchTimer = 0
                ChTimer = 0
                RestDchTimer = 0
                RestChTimer = 0
                voltPS = 0
                voltES = 0
                voltPSEL = 0
                ampPS = 0
                ampES = 0
                ampPSEL = 0

            if(profile == "StopPSEL"):
                flagStt = "StopPSEL"
                flagLoad = "None"
                flagDvc = "None"
                flagType = "None"
                flagCyc = "None"
                Nc = 0
                QcompPSEL = QcompPSEL
                pwrSupply.write('OUTPut:STATe 0')
                electLoad.write('INPut:STATe 0')

            if(flagStt == "StartPSEL" and flagDvc == "PSEL" and profile == "Meas"):
                #Start discharge
                elapsedTimePSEL = time.time() - startTimePSEL
                if((time.time()-startTimePSEL > 5)  and Nc<2):
                    #Start Charge
                    if(flagCyc == "Ch"):
                        pwrSupply.write('OUTPut:STATe 1')
                        electLoad.write('INPut:STATe 0')
                        ChTimer = time.time()
                        flagCyc = "RCh" #-->Run Ch
                    if(flagCyc == "RCh" and (time.time()-ChTimer > Tch)):
                        flagCyc = "RestCh"
                        ChTimer = 0
                        pwrSupply.write('OUTPut:STATe 0')
                    #Start resting charge
                    if(flagCyc == "RestCh"):
                        pwrSupply.write('OUTPut:STATe 0')
                        electLoad.write('INPut:STATe 0')
                        RestChTimer = time.time()
                        flagCyc = "RRestCh" #-->Run RestCh
                    if(flagCyc == "RRestCh" and time.time()-RestChTimer > Trest):
                        flagCyc = "Dch"
                        RestChTimer = 0
                    if(flagCyc == "Dch"):
                        pwrSupply.write('OUTPut:STATe 0')
                        electLoad.write('INPut:STATe 1')
                        DchTimer = time.time()
                        flagCyc = "RDch" #-->Run Dch
                    if(flagCyc == "RDch" and (time.time()-DchTimer > Tdch or float(voltPSEL)<= Vmin)):
                        flagCyc = "RestDch"
                        DchTimer = 0
                        electLoad.write('INPut:STATe 0')
                    #Start resting discharge
                    if(flagCyc == "RestDch"):
                        pwrSupply.write('OUTPut:STATe 0')
                        electLoad.write('INPut:STATe 0')
                        RestDchTimer = time.time()
                        flagCyc = "RRestDch" #-->Run RestDch
                    if(flagCyc == "RRestDch" and time.time()-RestDchTimer > Trest):
                        flagCyc = "Ch"
                        RestDchTimer = 0
                        Nc += 1
                        print(Nc)
                elif(Nc>=2):
                    print("Acabou")
                    pwrSupply.write('OUTPut:STATe 0')
                    electLoad.write('INPut:STATe 0')
                    flagStt = "StopPSEL"
                    flagCyc = "Done"
                    Nc = 0
                # Measures
                voltPS = pwrSupply.query('MEASure:VOLTage?')
                ampPS = pwrSupply.query('MEASure:CURRent?')

                voltEL = electLoad.query('MEASure:VOLTage?')
                ampEL = electLoad.query('MEASure:CURRent?')

                if(flagCyc == "Dch" or flagCyc == "RDch" or flagCyc == "RestDch"  or flagCyc == "RRestDch"):
                    voltPSEL = str(round(float(voltEL),3))
                    ampPSEL = str(round(float(ampEL),3))
                elif(flagCyc == "Ch" or flagCyc == "RCh" or flagCyc == "RestCh"  or flagCyc == "RRestCh"):
                    voltPSEL = str(round(float(voltPS),3))
                    ampPSEL = str(round(-float(ampPS),3))

                QcompPSEL = QcompPSEL - float(ampPSEL)/3600
                QcompPSEL = round(float(QcompPSEL),8)

                sendMeasPSEL = 'measPSEL;'+str(round(elapsedTimePSEL,1))+';'+voltPSEL.split('\n')[0]+';'+ampPSEL.split('\n')[0]+';'+str(QcompPSEL)+';'+flagCyc+';'+ flagType
                conn.sendall(sendMeasPSEL.encode())






