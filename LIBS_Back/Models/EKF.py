###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################
import numpy as np
import pandas as pd
import graph


###################################################################
##                   G L O B A L   C O N S T A N T               ##
###################################################################


###################################################################
##                   G L O B A L   V A R I A B L E S             ##
###################################################################
SAMPLING_RATE = 1  # seconds
R1 = 0.009818410271493
C1 = 1.563954740330107*10**4
R2 = 0.031463057438081
C2 = 3.933292323912280*10**4
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
        self.x = np.array([[0],[0],[0.5]]) # state vector
        if mode == 1:
            self.P = np.diag([0.001, 0.001, 0.01])  # covariance matrix
            self.Q = 0.000001 * np.eye(3)  # process noise
            self.R = 0.2 # measurement noise

        # elif mode == 2:
        #     self.P = np.diag([1*10**-3, 1*10**-3, 10])
        #     self.Q = np.diag([1 * 10 ** -5, 1 * 10 ** -5, 1 * 10 ** -9])  # process noise
        #     self.R = 1 * 10 ** -5
        # elif mode == 3:
        #     self.P = np.diag([0.01, 0.01, 100])
        #     self.Q = 0.01 * np.eye(3)
        #     self.R = 10
        # elif mode == 4:
        #     self.P = np.diag([0.001, 0.001, 100])  # covariance matrix
        #     self.Q = np.diag([10**-5, 10**-5, 10**-9])  # process noise
        #     self.R = 10**-5  # measurement noise

        self.A = np.array([[1-(SAMPLING_RATE/(R1*C1)), 0, 0], [0, 1-(SAMPLING_RATE/(R2*C2)), 0], [0, 0,1]])# non linear function based on the chosen model see the paper p2
        self.B = np.array([[SAMPLING_RATE/C1], [SAMPLING_RATE/C2], [-SAMPLING_RATE/(3600*Qn)]]) # see the paper p 2
        self.u = 0 # current
        self.K = None  # Kalman gain
        self.z = 0  # voltage
        self.step = 0
        self.safeX = []
        self.P = np.dot(np.dot(self.A, self.P), np.transpose(self.A)) + self.Q # extrapolated covariance matrix
        if fileToOpen is not None :
            with open('C:/LIBS/LIBS_Back/dataTest/'+fileToOpen, 'r') as file:
                self.data = pd.read_csv(file, delimiter=';')
        else:
            self.data = pd.DataFrame()# 2 columns time and voltage
            self.data['time'] = np.arange(0, 1, 1)
            self.data['voltage'] = 0
            self.data['current'] = 0


    # voc 
    def h(self,x):
        return (10**4)*((x**9)*0.140437566214432+(x**8)*-0.693293580320924+(x**7)*1.448317451181394 + (x ** 6) *-1.665299094951629 + (x ** 5)*1.148704101226141 + (x ** 4)*-0.486836353839831 + (x ** 3)*0.125420712206318 + (x ** 2)*-0.018961803736654 + x*0.001657801378501 + 0.000269333059573)
    def h_derivative(self,x):
        return (10**4)*( 9*(x**8)*0.140437566214432 + 8*(x**7)*-0.693293580320924 + 7*(x**6)*1.448317451181394 + 6*(x ** 5)*-1.665299094951629 + 5*(x ** 4)*1.148704101226141 + 4*(x ** 3)*-0.486836353839831 + 3*(x ** 2)*0.125420712206318 + 2*x*-0.018961803736654 + 0.001657801378501)

    def R0(self,x):
        return (10**3)*((x**9)*0.440568380336331+(x**8)*-2.188575118770938+(x**7)*4.662025929324535+(x**6)*-5.561277160719505+(x**5)*4.069003040512039+(x**4)*-1.878727644202677+(x**3)*0.541295950462937+(x**2)*-0.092097275963785+x*0.008056926448651-0.000160671690337)

    def R0_derivative(self,x):
        return (10**3)*(9*(x**8)*0.440568380336331+8*(x**7)*-2.188575118770938+7*(x**6)*4.662025929324535+6*(x**5)*-5.561277160719505+5*(x**4)*4.069003040512039+4*(x**3)*-1.878727644202677+3*(x**2)*0.541295950462937+2*x*-0.092097275963785+0.008056926448651)

    def g(self,x0,x1,x2,u):
        return - x0 - x1 - self.R0(x2) * u + self.h(x2)

    def dg(self):# observation matrix
        return np.array([[-1, -1, self.h_derivative(self.x[2][0])-self.R0_derivative(self.x[2][0])*self.u]])


    def predict(self):

        # Compute x_hat(k+1)
        self.x = np.dot(self.A, self.x) + self.B * self.u

        # Compute P(k+1)
        self.P = np.dot(np.dot(self.A, self.P), np.transpose(self.A)) + self.Q
        # print(self.P)

    def correction(self):
        # Compute K(k+1)

        number = np.dot(np.dot(self.dg(), self.P), np.transpose(self.dg())) + self.R
        # if number[0][0] > 7*10**302:
        #     number[0][0] = 0
        # else :
        number[0][0] = 1/number[0][0]

        self.K =  np.dot(self.P, np.transpose(self.dg()))/(np.dot(np.dot(self.dg(), self.P), np.transpose(self.dg())) + self.R)
        # print(self.K)
        # self.K.shape = (3,1)
        # print(self.K)

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
        self.safeX.append(self.x)
        while self.step < len(self.data.values):
            self.getmeasure()
            self.predict()
            self.correction()
            self.safeX.append(self.x)
        self.draw()


    def runOneStepOnline(self,z,u):
        self.z = z
        self.u = u
        self.predict()
        self.correction()
        self.safeX.append(self.x)
        # add 1 index to the np array data
        tempOffline = pd.DataFrame()  # 2 columns time and voltage
        tempOffline['time'] = np.arange(0, 1, 1)
        tempOffline['voltage'] = z
        tempOffline['current'] = u
        self.data = pd.concat([self.data, tempOffline], ignore_index=True)
        self.safeX.append(self.x)
        return [self.x,self.g(self.safeX[len(self.safeX)-1][0],self.safeX[len(self.safeX)-1][1],self.safeX[len(self.safeX)-1][2],u)]

    def draw(self):
        timeTab = []
        voltageTab = []
        currentTab = []
        socTab = []
        socEstimator = []
        gTab = []

        for i in range(len(self.data.values)):
            timeTab.append(i)
            voltageTab.append(self.data.values[i][1])
            currentTab.append(self.data.values[i][2])
            if i == 0:
                socTab.append(1)
            else:
                socTab.append(socTab[i-1]-(currentTab[i-1]*(1/(3600*Qn))))
            gTab.append(self.g(self.safeX[i][0],self.safeX[i][1],self.safeX[i][2],self.data.values[i][2]))
            socEstimator.append(self.safeX[i][2])


        graph.Graph(timeTab, socTab, socEstimator, voltageTab, currentTab, gTab,self.fileToOpen)
        # fig2, ax2 = plt.subplots()
        # ax2.plot(timeTab, socTab, label='soc')
        # ax2.plot(timeTab, socEstimator, label='socEstimator')
        # plt.xlabel('time')
        # plt.ylabel('soc')
        # ax2.legend()
        # plt.show()
        #
        # fig, ax = plt.subplots()
        # ax.plot(timeTab, voltageTab, label='voltage')
        # ax.plot(timeTab, currentTab, label='current')
        # ax.plot(timeTab, gTab, label='g')
        # plt.xlabel('time')
        # plt.ylabel('voltage/current')
        # ax.legend()
        # plt.show()
        return





# ekf = EKF(None,1)
# data = ekf.runOneStepOnline(1,1)
# x = data[0]
# g = data[1]
# print(x)
# print(g)

# ekf = EKF("BID002.txt",1)
# ekf.runOffline()
# ekf = EKF("BID002.txt",2)
# ekf.runOffline()
# ekf = EKF("BID002.txt",3)
# ekf.runOffline()
# ekf = EKF("BID002.txt",4)
# ekf.runOffline()
#
# ekf = EKF("BID003.txt",1)
# ekf.runOffline()
# ekf = EKF("BID003.txt",2)
# ekf.runOffline()
# ekf = EKF("BID003.txt",3)
# ekf.runOffline()
#
#
# ekf = EKF("BID004.txt",1)
# ekf.runOffline()
# ekf = EKF("BID004.txt",2)
# ekf.runOffline()
# ekf = EKF("BID004.txt",3)
# ekf.runOffline()
#
# ekf = EKF("HPPC.txt", 1)
# ekf.runOffline()
# ekf = EKF("HPPC.txt",2)
# ekf.runOffline()
# ekf = EKF("HPPC.txt",3)
# ekf.runOffline()
# ekf = EKF("HPPC.txt",4)
# ekf.runOffline()


import os
for root, dirs, files in os.walk("C:/LIBS/LIBS_Back/dataTest/"):
    for file in files:
        if file.endswith(".txt"):
            ekf = EKF(file, 1)
            ekf.runOffline()
