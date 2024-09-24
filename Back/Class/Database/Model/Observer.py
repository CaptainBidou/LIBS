import Class.Database.Model.ModelAbstract as ModelAbstract

###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################
import numpy as np


###################################################################
##                   G L O B A L   C O N S T A N T               ##
###################################################################

###################################################################
##            S T R U C T    D E C L A R A T I O N               ##
###################################################################

class Observer(ModelAbstract.Model):
    def __init__(self):
        self.Qn = 3.08
        self.SAMPLING_RATE = 1
        self.R0 = 0.085870708508781
        self.R1 = 0.009818410271493
        self.C1 = 1.563954740330107*10**4
        self.R2 = 0.031463057438081
        self.C2 = 3.933292323912280*10**3
        self.A = np.array([[1-(self.SAMPLING_RATE/(self.R1*self.C1)), 0, 0], [0, 1-(self.SAMPLING_RATE/(self.R2*self.C2)), 0], [0, 0, 1]])
        self.B = np.array([[self.SAMPLING_RATE/self.C1], [self.SAMPLING_RATE/self.C2], [-self.SAMPLING_RATE/(3600*self.Qn)]])
        self.C = np.array([-1,-1,0.859368465423472])
        self.D = -self.R0
        self.L = (10**(-4)) * np.array([[0.496817], [-0.194432], [335.851524]])
        self.xhat = np.array([[0], [0], [0.5]])
        self.lastu = 0
        self.lastz = 0
        self.yhat = self.setYHat(0)
        self.save = []
        self.save.append([self.xhat, self.yhat])
        self.data = {}
        self.data['time'] = np.arange(0, 1, 1)
        self.data['voltage'] = 0
        self.data['current'] = 0

    def toString(self):
        return "observer"

    def runOneStep(self, z, u,charge):
        self.xhat = self.setXHat(self.lastz, self.lastu)
        self.lastu = float(u)
        self.lastz = float(z)
        if charge:
            self.lastu=-self.lastu

        self.yhat = self.setYHat(self.lastu)
        self.save.append([self.xhat[2][0], self.yhat[0]])
        data= [self.xhat[2][0], self.yhat[0]]
        return float(data[1]),float(data[0])

    def setPhiHat(self):
        soc = self.xhat[2][0]
        print("h :" + str(self.h(soc)))
        return self.h(soc) - 0.859368465423472 * soc

    def setYHat(self,u):
        return np.dot(self.C,self.xhat) + self.D * u + self.setPhiHat()

    def setXHat(self,z,u):
        return np.dot(self.A,self.xhat) + self.B*u+self.L * (z-self.yhat)
    def h(self,x):
       return (10**4)*((x**9)*0.140437566214432+(x**8)*-0.693293580320924+(x**7)*1.448317451181394 + (x ** 6) *-1.665299094951629 + (x ** 5)*1.148704101226141 + (x ** 4)*-0.486836353839831 + (x ** 3)*0.125420712206318 + (x ** 2)*-0.018961803736654 + x*0.001657801378501 + 0.000269333059573)
