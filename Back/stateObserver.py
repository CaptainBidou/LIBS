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
R0 = 0.085870708508781
R1 = 0.009818410271493
C1 = 1.563954740330107*10**4
R2 = 0.031463057438081
C2 = 3.933292323912280*10**3
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
            with open('C:/Users/tjasr/Desktop/LIBS-prod/LIBS/Back/datasets/Hppc/BID004_HPPC_02062024.txt', 'r') as file:
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
       return (10**4)*((x**9)*0.140437566214432+(x**8)*-0.693293580320924+(x**7)*1.448317451181394 + (x ** 6) *-1.665299094951629 + (x ** 5)*1.148704101226141 + (x ** 4)*-0.486836353839831 + (x ** 3)*0.125420712206318 + (x ** 2)*-0.018961803736654 + x*0.001657801378501 + 0.000269333059573)

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


# test('C:/Users/tjasr/Desktop/LIBS-prod/LIBS/Back/datasets/Hppc/BID004_HPPC_02062024.txt')
