import os
import EKF

for root, dirs, files in os.walk("C:/Users/tjasr/Documents/GitHub/LIBS/LIBS_Back/datasets/Random/"):
    for file in files:
        if file.endswith(".txt"):
            ekf = EKF("Random/"+file, 1)
            ekf.runOffline()