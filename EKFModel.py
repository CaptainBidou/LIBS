###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################
import numpy as np
import pandas as pd


###################################################################
##                   G L O B A L   C O N S T A N T               ##
###################################################################


###################################################################
##                   G L O B A L   V A R I A B L E S             ##
###################################################################
SAMPLING_RATE = 1  # seconds
R0 = 123.445 *10**-3
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


class EKF:
    def __init__(self,fileToOpen,mode):
        self.fileToOpen = fileToOpen
        self.x = np.array([[0],[0],[0.8]]) # state vector
        if mode == 1:
            self.P = np.diag([0.1, 0.1, 10 ** 3])  # covariance matrix
            self.Q = 10 ** -6 * np.eye(3)  # process noise
            self.R = 2500 # measurement noise
        elif mode == 2:
            self.P = np.diag([1*10**-3, 1*10**-3, 10])
            self.Q = np.diag([1 * 10 ** -5, 1 * 10 ** -5, 1 * 10 ** -9])  # process noise
            self.R = 1 * 10 ** -5
        elif mode == 3:
            self.P = np.diag([0.01, 0.01, 100])
            self.Q = 0.01 * np.eye(3)
            self.R = 10
        elif mode == 4:
            self.P = np.diag([0.001, 0.001, 100])  # covariance matrix
            self.Q = np.diag([10**-5, 10**-5, 10**-9])  # process noise
            self.R = 10**-5  # measurement noise

        self.A = np.array([[1-(SAMPLING_RATE/(R1*C1)), 0, 0], [0, 1-(SAMPLING_RATE/(R2*C2)), 0], [0, 0, 1]])# non linear function based on the chosen model see the paper p2
        self.B = np.array([[SAMPLING_RATE/C1], [SAMPLING_RATE/C2], [-SAMPLING_RATE/(3600*Qn)]]) # see the paper p 2
        self.u = 0 # current
        self.K = None  # Kalman gain
        self.z = 0  # voltage
        self.step = 0
        self.safeX = []
        if fileToOpen is not None :
            with open('C:/Users/tjasr/Documents/GitHub/LIBS/LIBS_Back/datasets/'+fileToOpen, 'r') as file:
                self.data = pd.read_csv(file, delimiter=';')
        else:
            self.data = pd.DataFrame()# 2 columns time and voltage
            self.data['time'] = np.arange(0, 1, 1)
            self.data['voltage'] = 0
            self.data['current'] = 0



    def h(self,x):
        return (x ** 6) * -22.215 + (x ** 5) * 70.560 + (x ** 4) * -89.148 + (x ** 3) * 57.312 + (x ** 2) * -19.563 + x * 3.994 + 3.142
    def h_derivative(self,x):
        return 3.994 + x * -19.563 * 2 + (x**2) * 57.312 * 3 + (x**3) * -89.148 * 4 + (x**4) * 70.560 * 5 + (x**5) * -22.215 * 6

    def g(self,x0,x1,x2,u):
        return - x0 - x1 - R0*u + self.h(x2)

    def dg(self):# observation matrix
        return np.array([[-1, -1, self.h_derivative(self.x[2][0])]])


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
    def runOneStepOnline(self,z,u):
        self.z = float(z)
        self.u = float(u)
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
        return [self.x,self.g(self.safeX[len(self.safeX)-1][0],self.safeX[len(self.safeX)-1][1],self.safeX[len(self.safeX)-1][2],self.u)]
    


###################################################################
##                   G L O B A L   V A R I A B L E S             ##
###################################################################
ekf = EKF(None,1)