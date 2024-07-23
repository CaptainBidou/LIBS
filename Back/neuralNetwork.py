import numpy as np
import keras 
from keras import *
import pandas as pd
import matplotlib.pyplot as plt



with open('C:/Users/tjasr/Documents/GitHub/LIBS/LIBS_Back/datasets/Random/BID001_RANDCh_29052024.txt', 'r') as file:
    dataB1 = pd.read_csv(file, delimiter='\t')

with open('C:/Users/tjasr/Documents/GitHub/LIBS/LIBS_Back/datasets/Random/BID002_RANDCh_30052024.txt', 'r') as file:
    dataB2 = pd.read_csv(file, delimiter=';')

with open('C:/Users/tjasr/Documents/GitHub/LIBS/LIBS_Back/datasets/Random/BID002_RANDCh_30052024.txt', 'r') as file:
    dataB3 = pd.read_csv(file, delimiter=';')
# entree = [[],[]...]
# the first column is the voltage and the second is the current

entree = []
sortie = [1]

for i in range(len(dataB1.values)):
    entree.append([dataB1.values[i][1],dataB1.values[i][2]])
    sortie.append(sortie[len(sortie)-1]-(dataB1.values[i][2]*(1/(3600*3.08))))

sortie.pop()
sortie.append(1)

for i in range(len(dataB2.values)):
    entree.append([dataB2.values[i][1],dataB2.values[i][2]])
    sortie.append(sortie[len(sortie)-1]-(dataB2.values[i][2]*(1/(3600*3.08))))

sortie.pop()
sortie.append(1)

for i in range(len(dataB3.values)):
    entree.append([dataB3.values[i][1],dataB3.values[i][2]])
    sortie.append(sortie[len(sortie)-1]-(dataB3.values[i][2]*(1/(3600*3.08))))

sortie.pop()

entree = np.array(entree)
sortie = np.array(sortie)





try :
    model = keras.models.load_model('C:/Users/tjasr/Documents/GitHub/LIBS/LIBS_Back/Models/FNN/BID001_BID002_BID003_2-20-3.keras')
    model.compile(loss='mean_squared_error',optimizer='adam')
    while True:
        model.fit(entree,sortie,epochs=2)
        model.save('C:/Users/tjasr/Documents/GitHub/LIBS/LIBS_Back/Models/FNN/BID001_BID002_BID003_2-20-3.keras')
    

except ValueError as e:
    model = Sequential()

    model.add(layers.Dense(units=20,input_shape=[2]))
    model.add(layers.Dense(units=1))

    model.compile(loss='mean_squared_error',optimizer='adam')
    model.fit(entree,sortie,epochs=2)

    model.save('C:/Users/tjasr/Documents/GitHub/LIBS/LIBS_Back/Models/FNN/BID001_BID002_BID003_2-20-3.keras')

# with open('C:/Users/tjasr/Documents/GitHub/LIBS/LIBS_Back/datasets/Random/BID004_RANDCh_30052024.txt', 'r') as file:
#     data = pd.read_csv(file, delimiter=';')

# SOCFNN=[]
# SOC=[1]
# TIME=[]
# y=0
# for i in range(len(data.values)):
#     print(model.predict(np.array([[data.values[i][1],data.values[i][2]]])))
#     SOCFNN.append(model.predict(np.array([[data.values[i][1],data.values[i][2]]]))[0][0])
#     SOC.append(SOC[len(SOC)-1]-(data.values[i][2]*(1/(3600*3.08))))
#     TIME.append(y)
#     y=y+1
# SOC.pop()


# fig2, ax2 = plt.subplots()
# ax2.plot(TIME, SOC, label='soc')
# ax2.plot(TIME, SOCFNN, label='socEstimator')
# plt.xlabel('time')
# plt.ylabel('soc')
# # the ordonnate of the graph have to show only 0 to 1 values
# plt.ylim(0, 1.1)
# plt.title("FNN SOC estimation")
# ax2.legend()
# plt.show()

