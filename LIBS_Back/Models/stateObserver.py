###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


###################################################################
##                   G L O B A L   C O N S T A N T               ##
###################################################################


###################################################################
##                   G L O B A L   V A R I A B L E S             ##
###################################################################
SAMPLING_RATE = 1  # seconds
R0 = 123.445*10**-3
R1 = 16.533*10**-3
C1 = 4.378*10**3
R2 = 2.069*10**-3
C2 = 35.756*10**3
Qn = 3.08
###################################################################
##            F U N C T I O N    D E C L A R A T I O N           ##
###################################################################

###################################################################
##            S T R U C T    D E C L A R A T I O N               ##
###################################################################

class observer:
    def __init__(self,fileToOpen):
        self.A = np.array([[1-(SAMPLING_RATE/(R1*C1)), 0, 0], [0, 1-(SAMPLING_RATE/(R2*C2)), 0], [0, 0, 1]])
        self.B = np.array([[SAMPLING_RATE/C1], [SAMPLING_RATE/C2], [-SAMPLING_RATE/(3600*Qn)]])
        self.C = np.array([-1,-1,0.316])
        self.D = -R0
        self.L = (10**(-4)) * np.array([[0.496817], [-0.194432], [335.851524]])
        self.xhat = np.array([[0], [0], [0.8]])
        self.lastu = 0
        self.lastz = 0
        self.yhat = self.setYHat(0)
        self.save = []

        self.save.append([self.xhat, self.yhat])
        if fileToOpen is not None :
            with open('C:/Users/tjasr/Documents/GitHub/LIBS/LIBS_Back/datasets/'+fileToOpen, 'r') as file:
                self.data = pd.read_csv(file, delimiter=';')
                print(self.data)
        else:
            self.data = pd.DataFrame()# 2 columns time and voltage
            self.data['time'] = np.arange(0, 1, 1)
            self.data['voltage'] = 0
            self.data['current'] = 0

    def nextStep(self, z, u):
        self.xhat = self.setXHat(self.lastz, self.lastu)
        print(self.setPhiHat())
        self.lastu = u
        self.lastz = z
        self.yhat = self.setYHat(u)
        self.save.append([self.xhat[2][0], self.yhat[0]])
        return [self.xhat[2][0], self.yhat[0]]

    def setPhiHat(self):
        soc = self.xhat[2][0]
        print("h :" + str(self.h(soc)))
        return self.h(soc) - 0.316 * soc

    def setYHat(self,u):
        return np.dot(self.C,self.xhat) + self.D * u + self.setPhiHat()

    def setXHat(self,z,u):
        return np.dot(self.A,self.xhat) + self.B*u+self.L * (z-self.yhat)
    def h(self,x):
        return (x ** 6) * -22.215 + (x ** 5) * 70.560 + (x ** 4) * -89.148 + (x ** 3) * 57.312 + (x ** 2) * -19.563 + x * 3.994 + 3.142
    def runOneStepOnline(self, z, u):
        val = self.nextStep(z, u)
        print(val)
        return val



###################################################################
def test(nom):
    o = observer(nom)
    saveVoltage = [0]
    saveCurrent = [0]
    saveTime = [0]
    socTab = [1]

    socEstimator = []
    gTab = []
    socEstimator.append(o.xhat[2][0])
    gTab.append(o.yhat[0])

    for i in range(0,3000):
        val = o.nextStep(o.data.values[i][1], o.data.values[i][2])
        print(i)
        print(val)
        socEstimator.append(val[0])
        gTab.append(val[1])
        saveVoltage.append(o.data.values[i][1])
        saveCurrent.append(o.data.values[i][2])
        socTab.append(socTab[i-1]-(saveCurrent[i-1]*(1/(3600*Qn))))
        saveTime.append(i)

    fig2, ax2 = plt.subplots()

    ax2.plot(saveTime, socTab, label='soc')
    ax2.plot(saveTime, socEstimator, label='socEstimator')
    plt.xlabel('time')
    plt.ylabel('soc')
    ax2.legend()
    plt.show()

    fig, ax = plt.subplots()
    ax.plot(saveTime, saveVoltage, label='voltage')
    ax.plot(saveTime, saveCurrent, label='current')
    ax.plot(saveTime, gTab, label='g')
    plt.xlabel('time')
    plt.ylabel('voltage/current')
    ax.legend()
    plt.show()

test("BID001_hppc.txt")