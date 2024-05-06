###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################
import pyvisa as visa
import socket
import time
import random
import random

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
RandTrest = 0
RandTime = 0
RandAmpl = 0

###################################################################
##            F U N C T I O N    D E C L A R A T I O N           ##
###################################################################
def calculIt(value):
    return float(value)*cell.Qn/100

def calculImax(It):
    return 1.1*It

def calculQtype(It):
    return round(It/cell.Qn,1)

def messageMeasureSerialize(profile,flag):
    if(profile == "Ch"):
        sendMeas = 'measPS;'+'0'
    if(profile == "Dch"):
        sendMeas = 'measEL;'+'0'
    if(profile == "DchCh"):
        sendMeas = 'measPSEL;'+'0'
    if(profile == "StopPS"):
        sendMeas = 'measPS;'+ str(round(time.time()-startTimePS,1))
    sendMeas    =   sendMeas+';' + '0' + ';' + '0' + ';' + '0' + ';' + '0' + ';' + flag.flagType
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
    
    def configPSStart(self,It):
        print(It)
        self.pwrSupply.write("SOUR:VOLTage:LEVel " + str(cell.Vmax))
        self.pwrSupply.write("SOUR:CURRent:LEVel " + str(It))
        
    
    def configELStart(self,It):
        self.electLoad.write("SOUR:FUNC CURR")
        self.electLoad.write("SOUR:CURR:LEV:IMM " + str(It))
        self.electLoad.write("SOUR:CURR:RANG 4")
        self.electLoad.write("SOUR:CURR:SLEW 0.01")
        self.electLoad.write("SOUR:CURR:VON " + str(cell.Vmin))
        self.electLoad.write("SOUR:CURR:VLIM " + str(cell.Vmax))
        self.electLoad.write("SOUR:CURR:ILIM " + str(calculImax(It)))
    
    def configELRand(self,RandAmpl):
        self.electLoad.write("SOUR:FUNC CURR")
        self.electLoad.write("SOUR:CURR:LEV:IMM " + str(RandAmpl))
        self.electLoad.write("SOUR:CURR:RANG 40")
        self.electLoad.write("SOUR:CURR:SLEW 0.01")
        self.electLoad.write("SOUR:CURR:VON " + str(cell.Vmin))
        self.electLoad.write("SOUR:CURR:VLIM " + str(cell.Vmax))
        self.electLoad.write("SOUR:CURR:ILIM 5")

    def configEL40(self,It,chargeDischarge):
        self.electLoad.write("SOUR:CURR:RANG 40")
        self.electLoad.write("SOUR:FUNC CURR")
        self.electLoad.write("SOUR:CURR:LEV:IMM " + str(It))
        self.electLoad.write("SOUR:CURR:SLEW 0.01")
        self.electLoad.write("SOUR:CURR:VON " + str(cell.Vmin))
        self.electLoad.write("SOUR:CURR:VLIM " + str(chargeDischarge.Vmax_t))
        self.electLoad.write("SOUR:CURR:ILIM " + str(calculImax(It)))

    def configPS(self,output):
        self.pwrSupply.write('OUTPut:STATe '+str(output))

    def configEL(self,output):
        self.electLoad.write('INPut:STATe '+str(output))
    
    def configPSEL(self,Output,Input):
        self.configPS(Output)
        self.configEL(Input)

    def configMeasureWrite(self,device):
        if(device == "PS"):
            self.pwrSupply.write('MEASure:VOLTage?')
            self.pwrSupply.write('MEASure:CURRent?')
        if(device == "EL"):
            self.electLoad.write('MEASure:VOLTage?')
            self.electLoad.write('MEASure:CURRent?')
    
    def configMeasureQuery(self,device,measure):
        if(device == "PS"):
            if(measure == "VOLT"):
                return self.pwrSupply.query('MEASure:VOLTage?')
            if(measure == "CURR"):
                return self.pwrSupply.query('MEASure:CURRent?')
        if(device == "EL"):
            if(measure == "VOLT"):
                return self.electLoad.query('MEASure:VOLTage?')
            if(measure == "CURR"):
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
        self.Vn = 3.6 #Nominal voltage
        self.Vmax = 4.2 #Max voltage (Charging)
        self.Vmin = 2.5 #Min voltage (Discharging)
        self.QcompPS = 0 #Capacity computed to charge
        self.QcompEL = 0 #Capacity computed to discharge
        self.QcompPSEL = 0.35*2.9
        self.Icut = self.Qn/50 #Cut current
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

    def setFlagLoadConst(self):
        self.flagLoad = "Const"
    def setFlagLoadPulse(self):
        self.flagLoad = "Pulse"
    def setFlagLoadRand(self):
        self.flagLoad = "Random"
    
    def setFlagDvcPS(self):
        self.flagDvc = "PS"
    def setFlagDvcEL(self):
        self.flagDvc = "EL"
    def setFlagDvcSEL(self):
        self.flagDvc = "PSEL"

    def setFlagType(self,profile,mode,Q_type):
        if(mode == None):
            self.flagType = profile + "-" + str(Q_type) + "C"
        else:
            self.flagType = profile + "-" + mode + "-" + str(Q_type) + "C"

    def setflagCycCh(self):
        self.flagCyc = "Ch"#flagCyc is Dch to discharge, Ch to charge and Rest to resting (RestDch, RestCh)
########################################################################

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
   
    def handlerChDch(self,profile,mode,flag,value,measuringDevice,cdParameters):

        It = calculIt(value)
        #print(It)
        Q_type = calculQtype(It)

        if(profile == "Ch" and mode == "Const"): #Configuring Charge in constant mode
            flag.setFlagSourConst()
            flag.setFlagDvcPS()
            measuringDevice.configPSStart(It) 

        elif(profile == "Ch" and mode == "Pulse"): #Configuring Charge in constant mode
            flag.setFlagSourPulse()
            flag.setFlagDvcPS()
            measuringDevice.configPSStart(It)
            print(measuringDevice.pwrSupply.query("CURR? MIN"))#for what ?

        elif(profile == "Dch" and mode == "Const"): #Configuring Discharge in constant mode
            flag.setFlagLoadConst()
            flag.setFlagDvcEL()
            measuringDevice.configELStart(It)
            
        elif(profile == "Dch" and mode == "Pulse"): #Configuring Discharge in pulse mode
            flag.setFlagLoadPulse()
            flag.setFlagDvcEL()
            measuringDevice.configELStart(It)
            modeElectLoad = measuringDevice.electLoad.query('SOUR:FUNC?')#for what ? Nothing


        elif(profile == "Dch" and mode == "Random"):
            flag.setFlagLoadRand()
            flag.setFlagDvcEL()
            measuringDevice.configELRand(random.uniform(0.1,1.5))


        elif(profile == "DchCh" and mode[0:5] == "Cycle"): #Configuring Discharge in pulse mode
            N = int(mode[5])
            profile += "-Cyc"
            mode = None
            #TODO : create a function 
            cdParameters.Tdch = 600 #(Qn*sf/It)*3600 #In seconds
            cdParameters.Tch = 600#(Qn*sf/It)*3600 #In seconds

            cdParameters.Trest = cdParameters.Tch
            print(cdParameters.Trest)
            measuringDevice.configPSStart(It)
            measuringDevice.configEL40(It,cdParameters)
            flag.setFlagDvcPSEL() 
            flag.setflagCycCh()
        else :
            return None 
            
        flag.setFlagType(profile,mode,Q_type)    
        return messageMeasureSerialize(profile,flag).encode()
  
########################################################################



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
            if profile == "Dch" or profile =="Ch":
                print(profile)
                sendMeasure = cdParameters.handlerChDch(profile,mode,flag,value,measuringDevice,cdParameters)
                if sendMeasure != None:
                    conn.sendall(sendMeasure)   

            #Conditions to charge moment (PS = Power supply)
            if(profile == "StartPS" and (flag.flagSour == "Const" or flag.flagSour == "Pulse")):
                flag.flagStt = "StartPS"
                startTimePS = time.time()
                if(flag.flagSour == "Pulse"):
                    startTimePulsePS = time.time()
                    stateSignal = True
            
            if(profile == "StopPS"):
                flag.flagStt = "StopPS"
                flag.flagSour = "None"
                flag.flagLoad = "None"
                flag.flagDvc = "None"
                flag.flagType = "None"
                measuringDevice.configPS(0)
                conn.sendall(messageMeasureSerialize(profile,flag).encode())

            if(flag.flagStt == "StartPS" and flag.flagDvc == "PS" and profile == "Meas"):
                elapsedTimePS = time.time() - startTimePS
                voltPwrSupply = str(round(float(measuringDevice.configMeasureQuery("PS","VOLT")),3))
                cell.QcompPS = cell.QcompPS + float(measuringDevice.configMeasureQuery("PS","CURR"))/3600
                ampePwrSupply = str(round(float(measuringDevice.configMeasureQuery("PS","CURR")),3))
                cell.QcompPS = round(float(cell.QcompPS),8)

                if(elapsedTimePS >= 2 and flag.flagSour == "Const"):
                    measuringDevice.configPS(1)
                    if(elapsedTimePS >=25):
                        if(float(measuringDevice.configMeasureQuery("PS","CURR")) <= cell.Icut): #QcompPS >= Qn or
                            measuringDevice.configPS(0)
                            flag.flagStt = "StopPS"
                            voltPwrSupply = '0'
                            ampePwrSupply = '0'
                            cell.QcompPS = 0

                if(elapsedTimePS >= 2 and flag.flagSour == "Pulse"):
                    if(stateSignal == True):
                        measuringDevice.configPS(1)
                    elif(stateSignal == False):
                        measuringDevice.configPS(0)
                    pulseWidth = time.time() - startTimePulsePS
                    if(pulseWidth >= 300):
                        stateSignal = not stateSignal
                        startTimePulsePS = time.time()
                    if(cell.QcompPS >= cell.Qn): 
                        measuringDevice.configPS(0)
                        flag.flagStt = "StopPS"
                        cell.QcompPS = 0
                        voltPwrSupply = '0'
                        ampePwrSupply = '0'
                        modePwrSupply = '0'
                 
                #TODO : make a function for the serialisation 
                modePwrSupply = measuringDevice.configPSStatusQuery()
                sendMeasPS = 'measPS;'+ str(round(elapsedTimePS,0)) + ';' + voltPwrSupply.split('\n')[0] + ';' + ampePwrSupply.split('\n')[0] + ';' + modePwrSupply.split('\n')[0] + ';' + str(cell.QcompPS) + ';' + flag.flagType
                conn.sendall(sendMeasPS.encode())

            #Conditions to discharge moment (EL = Eletronic Load)
            if(profile == "StartEL" and (flag.flagLoad == "Const" or flag.flagLoad == "Pulse" or flag.flagLoad == "Random")):
                flag.flagStt = "StartEL"
                measuringDevice.configELWrite()
                modeElectLoad = measuringDevice.configELModeQuery()
                startTimeEL = time.time()
                if(flag.flagLoad == "Pulse"):
                    startTimePulseEL = time.time()
                    stateSignal = True

                if(flag.flagLoad == "Random"):
                    print("I choose the valors randomly")
                    startTimeRandEL = time.time()
                    stateSignal = True 
                    #RandTrest = round(random.uniform(15*60,30*60))#generate random number between and 15*60 and 30*60
                    RandTime = round(random.uniform(30,120))#generate random number between and 30 and 120
                    print("Time pulse :" + str(RandTime))
                    

            if(profile == "StopEL"):
                flag.flagStt = "StopEL"
                flag.flagLoad = "None"
                flag.flagDvc = "None"
                flag.flagType = "None"
                measuringDevice.configEL(0)
                modeElectLoad = 'Off\n'

                #TODO : make a function for the serialisation
                sendMeasEL = 'measEL;'+ str(round(time.time()-startTimeEL,1)) + ';' + str(0) + ';' + str(0) + ';' + str(0) + ';' + str(0) + ';' + modeElectLoad.split('\n')[0] + ';' + flag.flagType
                conn.sendall(sendMeasEL.encode())

            if(flag.flagStt == "StartEL" and flag.flagDvc == "EL" and profile == "Meas"):
                elapsedTimeEL = time.time() - startTimeEL
                voltElectLoad = measuringDevice.configMeasureQuery("EL","VOLT")
                voltElectLoad = str(round(float(voltElectLoad),3))

                ampeElectLoad = measuringDevice.configMeasureQuery("EL","CURR")

                cell.QcompEL = cell.QcompEL + float(ampeElectLoad)/3600

                ampeElectLoad = str(round(float(ampeElectLoad),3))
                cell.QcompEL = round(float(cell.QcompEL),8)

                if(elapsedTimeEL >= 2 and flag.flagLoad == "Const"):
                    measuringDevice.configEL(1)
                    if(float(voltElectLoad) <= cell.Vmin): # QcompEL >= 0.65*Qn or  QcompEL >= Qn or
                        measuringDevice.configEL(0)
                        flag.flagStt = "StopEL"
                        cell.QcompEL = 0
                        voltElectLoad = '0'
                        ampeElectLoad = '0'
                        modeElectLoad = 'Off\n'
                        # time.sleep(0.2)

                if(elapsedTimeEL >= 2 and flag.flagLoad == "Pulse"):
                    if(stateSignal == True):
                        measuringDevice.configEL(1)
                    elif(stateSignal == False):
                        measuringDevice.configEL(0)
                    pulseWidth = time.time() - startTimePulseEL
                    if(pulseWidth >= 300):
                        stateSignal = not stateSignal
                        startTimePulseEL = time.time()

                    if(float(voltElectLoad) <= cell.Vmin): 
                        measuringDevice.configEL(0)
                        flag.flagStt = "StopEL"
                        cell.QcompEL = 0
                        voltElectLoad = '0'
                        ampeElectLoad = '0'
                        modeElectLoad = 'Off\n'
                        # time.sleep(0.2)
                
                if (elapsedTimeEL >= 2 and flag.flagLoad == "Random"):#Resting time ??
                    if(stateSignal == True):
                        measuringDevice.configEL(1)
                    elif(stateSignal == False):
                        measuringDevice.configEL(0)
                    pulseWidth = time.time() - startTimeRandEL
                    if(pulseWidth >= RandTime and stateSignal == True):
                        stateSignal = not stateSignal
                        startTimeRandEL = time.time()
                        #RandAmpl=random.uniform(0.1,1.5)
                        RandTrest = round(random.uniform(5*60,10*60))#generate random number between and 15*60 and 30*60
                        #RandTime = round(random.uniform(30,120))#generate random number between and 30 and 120
                        print("Trest :" +str(RandTrest))
                        measuringDevice.configELRand(RandAmpl)
                    if(pulseWidth >= RandTrest and stateSignal == False):
                        stateSignal = not stateSignal
                        startTimeRandEL = time.time()
                        RandAmpl=random.uniform(0.1,1.5)
                        #RandTrest = round(random.uniform(15*60,30*60))#generate random number between and 15*60 and 30*60
                        RandTime = round(random.uniform(30,120))#generate random number between and 30 and 120
                        measuringDevice.configELRand(RandAmpl)
                        print("Time pulse :" + str(RandTime))
                    if(float(voltElectLoad) <= cell.Vmin):
                        measuringDevice.configEL(0)
                        flag.flagStt = "StopEL"
                        cell.QcompEL = 0
                        voltElectLoad = '0'
                        ampeElectLoad = '0'
                        modeElectLoad = 'Off\n'
                        # time.sleep(0.2)


                statusElectLoad = measuringDevice.configELStatusQuery()
                modeElectLoad = measuringDevice.configELModeQuery()
                #TODO : make a function for the serialisation
                sendMeasEL = 'measEL;'+ str(round(elapsedTimeEL,0)) + ';' + voltElectLoad.split('\n')[0] + ';' + ampeElectLoad.split('\n')[0] + ';' + statusElectLoad.split('\n')[0] + ';' + str(cell.QcompEL) + ';' + modeElectLoad.split('\n')[0] + ';' + flag.flagType
                conn.sendall(sendMeasEL.encode())
        
            # #Conditions to Cycle test (PSEL = Eletronic Load): Single cycle: Dch->Rest->Ch->Rest
            # if(profile == "StartPSEL"):
            #     flag.flagStt = "StartPSEL"
            #     startTimePSEL = time.time()
            #     DchTimer = 0
            #     ChTimer = 0
            #     RestDchTimer = 0
            #     RestChTimer = 0
            #     voltPS = 0
            #     voltES = 0
            #     voltPSEL = 0
            #     ampPS = 0
            #     ampES = 0
            #     ampPSEL = 0

            # if(profile == "StopPSEL"):
            #     flag.flagStt = "StopPSEL"
            #     flag.flagLoad = "None"
            #     flag.flagDvc = "None"
            #     flag.flagType = "None"
            #     flag.flagCyc = "None"
            #     Nc = 0
            #     QcompPSEL = QcompPSEL
            #     measuringDevice.configPSEL(0,0)

            # if(flag.flagStt == "StartPSEL" and flag.flagDvc == "PSEL" and profile == "Meas"):
            #     #Start discharge
            #     elapsedTimePSEL = time.time() - startTimePSEL
            #     if((time.time()-startTimePSEL > 5)  and Nc<2):
            #         #Start Charge
            #         if(flag.flagCyc == "Ch"):
            #             measuringDevice.configPSEL(1,0)
            #             ChTimer = time.time()
            #             flag.flagCyc = "RCh" #-->Run Ch
            #         if(flag.flagCyc == "RCh" and (time.time()-ChTimer > Tch)):
            #             flag.flagCyc = "RestCh"
            #             ChTimer = 0
            #             measuringDevice.configPS(0)
            #         #Start resting charge
            #         if(flag.flagCyc == "RestCh"):
            #             measuringDevice.configPSEL(0,0)
            #             RestChTimer = time.time()
            #             flag.flagCyc = "RRestCh" #-->Run RestCh
            #         if(flag.flagCyc == "RRestCh" and time.time()-RestChTimer > Trest):
            #             flag.flagCyc = "Dch"
            #             RestChTimer = 0
            #         if(flag.flagCyc == "Dch"):
            #             measuringDevice.configPSEL(0,1)
            #             DchTimer = time.time()
            #             flag.flagCyc = "RDch" #-->Run Dch
            #         if(flag.flagCyc == "RDch" and (time.time()-DchTimer > Tdch or float(voltPSEL)<= Vmin)):
            #             flag.flagCyc = "RestDch"
            #             DchTimer = 0
            #             measuringDevice.configPSEL(0,0)
            #         #Start resting discharge
            #         if(flag.flagCyc == "RestDch"):
            #             measuringDevice.configPSEL(0,0)
            #             RestDchTimer = time.time()
            #             flag.flagCyc = "RRestDch" #-->Run RestDch
            #         if(flag.flagCyc == "RRestDch" and time.time()-RestDchTimer > Trest):
            #             flag.flagCyc = "Ch"
            #             RestDchTimer = 0
            #             Nc += 1
            #             print(Nc)
            #     elif(Nc>=2):
            #         print("Acabou")
            #         measuringDevice.configPSEL(0,0)
            #         flag.flagStt = "StopPSEL"
            #         flag.flagCyc = "Done"
            #         Nc = 0

            #     # Measures
            #     measuringDevice.configMeasureWrite("PS")
            #     measuringDevice.configMeasureWrite("EL")

            #     if(flag.flagCyc == "Dch" or flag.flagCyc == "RDch" or flag.flagCyc == "RestDch"  or flag.flagCyc == "RRestDch"):
            #         voltPSEL = str(round(float(voltEL),3))
            #         ampPSEL = str(round(float(ampEL),3))
            #     elif(flag.flagCyc == "Ch" or flag.flagCyc == "RCh" or flag.flagCyc == "RestCh"  orflag. flagCyc == "RRestCh"):
            #         voltPSEL = str(round(float(voltPS),3))
            #         ampPSEL = str(round(-float(ampPS),3))

            #     QcompPSEL = QcompPSEL - float(ampPSEL)/3600
            #     QcompPSEL = round(float(QcompPSEL),8)

            #     sendMeasPSEL = 'measPSEL;'+str(round(elapsedTimePSEL,1))+';'+voltPSEL.split('\n')[0]+';'+ampPSEL.split('\n')[0]+';'+str(QcompPSEL)+';'+flagCyc+';'+ flagType
            #     conn.sendall(sendMeasPSEL.encode())






