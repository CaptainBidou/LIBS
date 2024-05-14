import time
import databaseBuild
import controller

SAMPLING_RATE = 1

cell = controller.Cell()
devices = controller.MeasuringDevice(controller.HOST, controller.PORT, controller.PWRSUPPLY, controller.ELECTLOAD)
devices.initialisation()



def startMeasurePS(idTest):
    #wait 1s
    time.sleep(SAMPLING_RATE)
    # send request to the ps
    voltPwrSupply = str(round(float(devices.configMeasureQuery("PS", "VOLT")), 3))
    cell.QcompPS = cell.QcompPS + float(devices.configMeasureQuery("PS", "CURR")) / 3600
    ampePwrSupply = str(round(float(devices.configMeasureQuery("PS", "CURR")), 3))
    cell.QcompPS = round(float(cell.QcompPS), 8)

    #send result to the database
    databaseBuild.createMeasure(idTest, time.time(), ampePwrSupply, voltPwrSupply, 0, 0)


def startMeasureEL(idTest):
    #wait 1s
    time.sleep(SAMPLING_RATE)
    # send request to the el
    voltElectLoad = str(round(float(devices.configMeasureQuery("EL", "VOLT")), 3))
    ampeElectLoad = str(round(float(devices.configMeasureQuery("EL", "CURR")), 3))
    cell.QcompEL = cell.QcompEL + float(devices.configMeasureQuery("EL", "CURR")) / 3600
    cell.QcompEL = round(float(cell.QcompEL), 8)

    #send result to the database
    databaseBuild.createMeasure(idTest, time.time(), ampeElectLoad, voltElectLoad, 0, 0)