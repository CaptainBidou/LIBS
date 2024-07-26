###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################
import numpy as np
import keras 
from keras import *
import matplotlib.pyplot as plt
###################################################################
##                   G L O B A L   C O N S T A N T               ##
###################################################################

###################################################################
##                   G L O B A L   V A R I A B L E S             ##
###################################################################

###################################################################
##            F U N C T I O N    D E C L A R A T I O N           ##
###################################################################
def prepareDataset():
    with open('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/datasets/Random/BID001_RANDCh_29052024.txt', 'r') as file:
        dataB1 = np.loadtxt(file, delimiter='\t', skiprows=1, usecols=(1,2), dtype=float)

    with open('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/datasets/Random/BID002_RANDCH_30052024.txt', 'r') as file:
        dataB2 = np.loadtxt(file, delimiter=';', skiprows=1, usecols=(1,2), dtype=float)

    with open('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/datasets/Random/BID003_RANDCh_30052024.txt', 'r') as file:
        dataB3 = np.loadtxt(file, delimiter=';', skiprows=1, usecols=(1,2), dtype=float)
    entree = []
    sortie = []
    entree.append([dataB1[0][0],dataB1[0][1]])
    entree.append([dataB1[1][0],dataB1[1][1]])
    sortie.append([1-(dataB1[1][1]*(1/(3600*3.08))),dataB1[1][0]])
    for i in range(2,len(dataB1)):
        entree.append([dataB1[i][0],dataB1[i][1]])
        sortie.append([(sortie[len(sortie)-1][0]-(dataB1[i][1]*(1/(3600*3.08)))),dataB1[i][0]])

    entree.pop()
    entree.append([dataB2[0][0],dataB2[0][1]])
    entree.append([dataB2[1][0],dataB2[1][1]])
    sortie.append([1-(dataB2[1][1]*(1/(3600*3.08))),dataB2[1][0]])
    for i in range(len(dataB2)):
        entree.append([dataB2[i][0],dataB2[i][1]])
        sortie.append([(sortie[len(sortie)-1][0]-(dataB2[i][1]*(1/(3600*3.08)))),dataB2[i][0]])

    entree.pop()
    entree.append([dataB3[0][0],dataB3[0][1]])
    entree.append([dataB3[1][0],dataB3[1][1]])
    sortie.append([1-(dataB3[1][1]*(1/(3600*3.08))),dataB3[1][0]])
    for i in range(len(dataB3)):
        entree.append([dataB3[i][0],dataB3[i][1]])
        sortie.append([(sortie[len(sortie)-1][0]-(dataB3[i][1]*(1/(3600*3.08)))),dataB3[i][0]])

    entree.pop()

    entree = np.array(entree)
    sortie = np.array(sortie)

    return entree,sortie


def prepareDatasetDynamic():
    with open('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/datasets/Random/BID001_RANDCh_29052024.txt', 'r') as file:
        dataB1 = np.loadtxt(file, delimiter='\t', skiprows=1, usecols=(1,2), dtype=float)

    with open('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/datasets/Random/BID002_RANDCH_30052024.txt', 'r') as file:
        dataB2 = np.loadtxt(file, delimiter=';', skiprows=1, usecols=(1,2), dtype=float)

    with open('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/datasets/Random/BID003_RANDCh_30052024.txt', 'r') as file:
        dataB3 = np.loadtxt(file, delimiter=';', skiprows=1, usecols=(1,2), dtype=float)

    entreeSafe = []
        
    entree = []
    sortie = []
    entreeQueue=queue(20)
    entree.append([dataB1[0][0],dataB1[0][1]])
    entreeQueue.put(dataB1[0][0],dataB1[0][1])
    entreeQueue.get(entreeSafe)
    entree.append([dataB1[1][0],dataB1[1][1]])
    entreeQueue.put(dataB1[1][0],dataB1[1][1])
    entreeQueue.get(entreeSafe)
    sortie.append([1-(dataB1[1][1]*(1/(3600*3.08))),dataB1[1][0]])
    
    for i in range(2,len(dataB1)):
        entree.append([dataB1[i][0],dataB1[i][1]])
        entreeQueue.put(dataB1[i][0],dataB1[i][1])
        entreeQueue.get(entreeSafe)
        sortie.append([(sortie[len(sortie)-1][0]-(dataB1[i][1]*(1/(3600*3.08)))),dataB1[i][0]])

    entree.pop()
    entreeSafe.pop()
    entreeQueue=queue(20)

    entree.append([dataB2[0][0],dataB2[0][1]])
    entreeQueue.put(dataB2[0][0],dataB2[0][1])
    entreeQueue.get(entreeSafe)
    entree.append([dataB2[1][0],dataB2[1][1]])
    entreeQueue.put(dataB2[1][0],dataB2[1][1])
    entreeQueue.get(entreeSafe)
    sortie.append([1-(dataB2[1][1]*(1/(3600*3.08))),dataB2[1][0]])
    for i in range(len(dataB2)):
        entree.append([dataB2[i][0],dataB2[i][1]])
        entreeQueue.put(dataB2[i][0],dataB2[i][1])
        entreeQueue.get(entreeSafe)
        sortie.append([(sortie[len(sortie)-1][0]-(dataB2[i][1]*(1/(3600*3.08)))),dataB2[i][0]])

    entree.pop()
    entreeSafe.pop()
    entreeQueue=queue(20)


    entree.append([dataB3[0][0],dataB3[0][1]])
    entreeQueue.put(dataB3[0][0],dataB3[0][1])
    entreeQueue.get(entreeSafe)
    entree.append([dataB3[1][0],dataB3[1][1]])
    entreeQueue.put(dataB3[1][0],dataB3[1][1])
    entreeQueue.get(entreeSafe)
    sortie.append([1-(dataB3[1][1]*(1/(3600*3.08))),dataB3[1][0]])
    for i in range(len(dataB3)):
        entree.append([dataB3[i][0],dataB3[i][1]])
        entreeQueue.put(dataB3[i][0],dataB3[i][1])
        entreeQueue.get(entreeSafe)
        sortie.append([(sortie[len(sortie)-1][0]-(dataB3[i][1]*(1/(3600*3.08)))),dataB3[i][0]])

    entree.pop()
    entreeSafe.pop()

    entreeSafe = np.array(entreeSafe)
    sortie = np.array(sortie)

    # write into a file
    with open('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/FNN/data_save_ENTREE.txt', 'w') as file:
        for i in range(len(entreeSafe)):
            file.write(str(entreeSafe[i]))

    with open('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/FNN/data_save_SORTIE.txt', 'w') as file:
        for i in range(len(sortie)):
            file.write(str(sortie[i]))

    

    return entreeSafe,sortie




def createModel(entree,sortie,epochs,name):
    model = Sequential()

    model.add(layers.Flatten(input_shape=(20, 2)))
    model.add(layers.Dense(units=20))
    model.add(layers.Dense(units=2))

    model.compile(loss='mean_squared_error',optimizer='adam')
    for i in range(epochs):
        print(i)
        model.fit(entree,sortie,epochs=1)
        model.save('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/FNN/'+name+'.keras')
    return model


###################################################################
##            S T R U C T    D E C L A R A T I O N               ##
###################################################################


        



class fnn():
    def __init__(self,file):
        self.model = keras.models.load_model(file)
        self.queue = queue(20)

    def runOneStepDynamicOnline(self,volt,current):
        self.queue.put(volt,current)
        return self.runOneStepDynamic(self.queue.q,20)

    def runOneStep(self,volt,current):
        entree = np.array([[float(volt),float(current)]])
        return self.model.predict(entree)
    
    def runOneStepDynamic(self,queueVal,size):
        entree = []
        for i in range(size):
            entree.append(queueVal[i])
        entree = np.array([entree])
        return self.model.predict(entree)

    def graph(self,fileTest):
        with open(fileTest, 'r') as file:
            # data = np.loadtxt(file, delimiter=';', skiprows=1, usecols=(1,2), dtype=float)
            data = np.loadtxt(file, delimiter='\t', skiprows=1, usecols=(0,1), dtype=float)
        volt=[]
        current=[]
        soc=[]
        socEstimator=[]
        voltEstimator=[]
        time=[]
        volt.append(data[0][0])
        current.append(data[0][1])
        time.append(0)
        volt.append(data[1][0])
        current.append(data[1][1])
        time.append(1)
        soc.append(1-(current[1]*(1/(3600*3.08))))
        val = fnn.runOneStep(volt[1],current[1])
        socEstimator.append(val[0][0])
        voltEstimator.append(val[0][1])
        for i in range(len(data)):
            time.append(i)
            volt.append(data[i][0])
            current.append(data[i][1])
            soc.append(soc[i]-(current[i]*(1/(3600*3.08))))
            val = fnn.runOneStep(volt[i],current[i])
            socEstimator.append(val[0][0])
            voltEstimator.append(val[0][1])


        volt.pop()
        current.pop()
        time.pop()


        # Write into a file : soc, socEstimator, voltage, current, g
        # with open('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/FNN/data_save.txt', 'w') as file:
        #     for i in range(len(soc)):
        #         file.write(str(time[i]) + ';' + str(volt[i]) + ';' + str(current[i]) + ';' + str(soc[i]) + ';' + str(socEstimator[i]) + ';' + str(voltEstimator[i]) + '\n')

        fig2, ax2 = plt.subplots()
        ax2.plot(time, soc, label='soc')
        ax2.plot(time, socEstimator, label='socEstimator')
        plt.xlabel('time')
        plt.ylabel('soc')
        ax2.legend()
        plt.show()

        fig, ax = plt.subplots()
        ax.plot(time, volt, label='voltage')
        ax.plot(time, current, label='current')
        ax.plot(time, voltEstimator, label='g')
        plt.xlabel('time')
        plt.ylabel('voltage/current')
        ax.legend()
        plt.show()

    def graphDynamic(self,fileTest):
        with open(fileTest, 'r') as file:
            data = np.loadtxt(file, delimiter=';', skiprows=1, usecols=(1,2), dtype=float)
            # data = np.loadtxt(file, delimiter='\t', skiprows=1, usecols=(0,1), dtype=float)
        volt=[]
        current=[]
        soc=[]
        socEstimator=[]
        voltEstimator=[]
        time=[]
        queueVal = queue(20)
        volt.append(data[0][0])
        current.append(data[0][1])
        queueVal.put(data[0][0],data[0][1])
        time.append(0)
        volt.append(data[1][0])
        current.append(data[1][1])
        queueVal.put(data[1][0],data[1][1])
        time.append(1)
        soc.append(1-(current[1]*(1/(3600*3.08))))
        val = fnn.runOneStepDynamic(queueVal.q,20)
        socEstimator.append(val[0][0])
        voltEstimator.append(val[0][1])
        for i in range(len(data)):
            time.append(i)
            volt.append(data[i][0])
            current.append(data[i][1])
            queueVal.put(data[i][0],data[i][1])
            soc.append(soc[i]-(current[i]*(1/(3600*3.08))))
            val = fnn.runOneStepDynamic(queueVal.q,20)
            socEstimator.append(val[0][0])
            voltEstimator.append(val[0][1])


        volt.pop()
        current.pop()
        time.pop()


        # Write into a file : soc, socEstimator, voltage, current, g
        # with open('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/FNN/data_save.txt', 'w') as file:
        #     for i in range(len(soc)):
        #         file.write(str(time[i]) + ';' + str(volt[i]) + ';' + str(current[i]) + ';' + str(soc[i]) + ';' + str(socEstimator[i]) + ';' + str(voltEstimator[i]) + '\n')

        fig2, ax2 = plt.subplots()
        ax2.plot(time, soc, label='soc')
        ax2.plot(time, socEstimator, label='socEstimator')
        plt.xlabel('time')
        plt.ylabel('soc')
        ax2.legend()
        plt.show()

        fig, ax = plt.subplots()
        ax.plot(time, volt, label='voltage')
        ax.plot(time, current, label='current')
        ax.plot(time, voltEstimator, label='g')
        plt.xlabel('time')
        plt.ylabel('voltage/current')
        ax.legend()
        plt.show()
            

class queue():
    def __init__(self,size):
        self.size = size
        self.q = []
        for i in range(size):
            self.q.append([0,0])
    def put(self,volt,current):
        self.q.pop()
        self.q.insert(0,[volt,current])
    def get(self,tab):
        tabtemp = []
        for i in range(self.size):
            tabtemp.append(self.q[i])
        tab.append(tabtemp)
        return tab

###################################################################
##                   G L O B A L   V A R I A B L E S             ##
###################################################################
fnn = fnn('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/FNN/DYNAMIC_BID001_BID002_BID003_20-20-2.keras')
#fnn.graphDynamic('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/datasets/Random/BID004_RANDCh_30052024.txt')


# entree,sortie = prepareDatasetDynamic()
# createModel(entree,sortie,100,'DYNAMIC_BID001_BID002_BID003_20-20-2')