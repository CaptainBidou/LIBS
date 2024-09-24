import Class.Database.Model.ModelAbstract as ModelAbstract
import numpy as np
import pandas as pd

class EKF(ModelAbstract.Model):
    def __init__(self):
        self.Qn = 3.08
        self.SAMPLING_RATE = 1
        self.R1 = 0.009818410271493
        self.C1 = 1.563954740330107*10**4
        self.R2 = 0.031463057438081
        self.C2 = 3.933292323912280*10**3
        self.x = np.array([[0],[0],[0.5]]) # state vector
        
        self.P = np.diag([0.001, 0.001, 0.01])  # covariance matrix
        self.Q = 0.000001 * np.eye(3)  # process noise
        self.R = 0.2 # measurement noise

        self.A = np.array([[1-(self.SAMPLING_RATE/(self.R1*self.C1)), 0, 0], [0, 1-(self.SAMPLING_RATE/(self.R2*self.C2)), 0], [0, 0, 1]])# non linear function based on the chosen model see the paper p2
        self.B = np.array([[self.SAMPLING_RATE/self.C1], [self.SAMPLING_RATE/self.C2], [-self.SAMPLING_RATE/(3600*self.Qn)]]) # see the paper p 2
        self.u = 0 # current
        self.K = None  # Kalman gain
        self.z = 0  # voltage
        self.step = 0
        self.safeX = []
        self.data = pd.DataFrame()# 2 columns time and voltage
        self.data['time'] = np.arange(0, 1, 1)
        self.data['voltage'] = 0
        self.data['current'] = 0

    def toString(self):
        return "EKF"

    def h(self,x):
        return (10**4)*((x**9)*0.140437566214432+(x**8)*-0.693293580320924+(x**7)*1.448317451181394 + (x ** 6) *-1.665299094951629 + (x ** 5)*1.148704101226141 + (x ** 4)*-0.486836353839831 + (x ** 3)*0.125420712206318 + (x ** 2)*-0.018961803736654 + x*0.001657801378501 + 0.000269333059573)
    def h_derivative(self,x):
        return (10**4)*( 9*(x**8)*0.140437566214432 + 8*(x**7)*-0.693293580320924 + 7*(x**6)*1.448317451181394 + 6*(x ** 5)*-1.665299094951629 + 5*(x ** 4)*1.148704101226141 + 4*(x ** 3)*-0.486836353839831 + 3*(x ** 2)*0.125420712206318 + 2*x*-0.018961803736654 + 0.001657801378501)

    def R0(self,x):
        return (10**3)*((x**9)*0.440568380336331+(x**8)*-2.188575118770938+(x**7)*4.662025929324535+(x**6)*-5.561277160719505+(x**5)*4.069003040512039+(x**4)*-1.878727644202677+(x**3)*0.541295950462937+(x**2)*-0.092097275963785+x*0.008056926448651-0.000160671690337)

    def R0_derivative(self,x):
        return (10**3)*(9*(x**8)*0.440568380336331+8*(x**7)*-2.188575118770938+7*(x**6)*4.662025929324535+6*(x**5)*-5.561277160719505+5*(x**4)*4.069003040512039+4*(x**3)*-1.878727644202677+3*(x**2)*0.541295950462937+2*x*-0.092097275963785+0.008056926448651)

    def g(self,x0,x1,x2,u):
        return - x0 - x1 - self.R0(x2)*u + self.h(x2)

    def dg(self):# observation matrix
        return np.array([[-1, -1, self.h_derivative(self.x[2][0])-self.R0_derivative(self.x[2][0])*self.u]])


    def predict(self):

        # Compute x_hat(k+1)
        self.x = np.dot(self.A, self.x) + self.B*self.u

        # Compute P(k+1)
        self.P = np.dot(np.dot(self.A, self.P), np.transpose(self.A)) + self.Q

    def correction(self):
        # Compute K(k+1)

        number = np.dot(np.dot(self.dg(), self.P), np.transpose(self.dg())) + self.R
        if number[0][0] > 7*10**302:
            number[0][0] = 0
        else :
            number[0][0] = 1/number[0][0]

        self.K = (number[0][0]) * np.dot(self.P, np.transpose(self.dg()))
        self.K.shape = (3,1)

        # Compute x(k+1)
        self.x = self.x + self.K * (self.z - self.g(self.x[0][0],self.x[1][0],self.x[2][0],self.u))

        # Compute P(k+1)
        ikdg = np.eye(3) - np.dot(self.K, self.dg())
        self.P = np.dot(np.dot(ikdg, self.P), np.transpose(ikdg))+ self.K * self.R * np.transpose(self.K)

    def getmeasure(self):
        self.z = self.data.values[self.step][1]
        self.u = self.data.values[self.step][2]
        self.step += 1
        # print(self.step)


    def runOffline(self):
        while self.step < len(self.data.values):
            self.getmeasure()
            self.predict()
            self.correction()
            self.safeX.append(self.x)
        self.draw()

    def runOneStep(self,z,u,charge):
        self.z = float(z)
        self.u = float(u)
        if charge :
            u = -1*u
        self.predict()
        self.correction()
        self.safeX.append(self.x)
        # add 1 index to the np array data
        tempOffline = pd.DataFrame()  # 2 columns time and voltage
        tempOffline['time'] = np.arange(0, 1, 1)
        tempOffline['voltage'] = self.z
        tempOffline['current'] = self.u
        self.data = pd.concat([self.data, tempOffline], ignore_index=True)
        self.safeX.append(self.x)
        result = [self.x,self.g(self.safeX[len(self.safeX)-1][0],self.safeX[len(self.safeX)-1][1],self.safeX[len(self.safeX)-1][2],self.u)]
        return float(result[1][0]),float(result[0][2][0])
    
    