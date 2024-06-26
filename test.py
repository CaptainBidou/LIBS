import time
import sampler
import threading
from threading import Thread


def letThread():
    print("awake")
    exit()



while True :
    time.sleep(0.001)
    threadCounter = Thread(target=letThread, args=())
    threadCounter.start()
