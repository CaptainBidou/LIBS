import numpy as np
import keras 
from keras import *
import pandas as pd
import matplotlib.pyplot as plt
import queue

SIZE = 40

q = queue.Queue(maxsize=SIZE)
for i in range(SIZE):
    q.put(0)

model = keras.models.load_model('C:/Users/tjasr/Documents/GitHub/LIBS/LIBS_Back/Models/FNN/BID001_BID002_BID003_20-20-3QUEUE.keras')
with open('C:/Users/tjasr/Documents/GitHub/LIBS/LIBS_Back/datasets/Random/BID004_RANDCh_30052024.txt', 'r') as file:
    data = np.loadtxt(file, delimiter=';', skiprows=1, usecols=(1,2), dtype=float)

SOCFNN=[]
SOC=[1]
TIME=[]
y=0
for i in range(len(data)):
    # print(model.predict(np.array([[data.values[i][1],data.values[i][2]]])))
    q.get()
    q.put(data[i][0])
    q.get()
    q.put(data[i][1])
    entree = []
    for i in range(SIZE):
        entree.append(q.get())
        q.put(entree[len(entree)-1])
    entree = np.array([entree])

    SOCFNN.append(model.predict(entree)[0][0])
    SOC.append(SOC[len(SOC)-1]-(data[i][1]*(1/(3600*3.08))))
    TIME.append(y)
    y=y+1
SOC.pop()


fig2, ax2 = plt.subplots()
ax2.plot(TIME, SOC, label='soc')
ax2.plot(TIME, SOCFNN, label='socEstimator')
plt.xlabel('time')
plt.ylabel('soc')
# the ordonnate of the graph have to show only 0 to 1 values
plt.ylim(0, 1.1)
plt.title("FNN SOC estimation")
ax2.legend()
plt.show()