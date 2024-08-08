import mysql.connector
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

databaseBool = False

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)

mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES WHERE `Database` = 'LIBS'")
databases = mycursor.fetchall()
if databases:
    databaseBool = True

if not databaseBool:
    mycursor.execute("CREATE DATABASE LIBS")
    print("Database created")

#connection to the database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="LIBS"
)

mycursor = mydb.cursor()

#creating the table
if (databaseBool == False):
    mycursor.execute("CREATE TABLE cells (id integer PRIMARY KEY AUTO_INCREMENT, name varchar(255) UNIQUE)")
    mycursor.execute("CREATE TABLE actions (id integer PRIMARY KEY AUTO_INCREMENT, name varchar(255) UNIQUE)")
    mycursor.execute(
        "CREATE TABLE tests (id integer PRIMARY KEY AUTO_INCREMENT, time timestamp, id_action integer, comment varchar(255),c_rate integer)")
    mycursor.execute(
        "CREATE TABLE measures (id integer PRIMARY KEY AUTO_INCREMENT, id_test integer, time timestamp, current float, output_voltage float, ambient_temperature float, surface_temperature float)")
    mycursor.execute("CREATE TABLE observers (id integer PRIMARY KEY AUTO_INCREMENT, name varchar(255) UNIQUE)")
    mycursor.execute("CREATE TABLE cells_relations (id_test integer, id_cell integer)")
    mycursor.execute("CREATE TABLE observers_relations (id_test integer, id_observer integer)")
    mycursor.execute(
        "CREATE TABLE measures_observers (id integer PRIMARY KEY AUTO_INCREMENT, id_measure integer, id_observer integer, v1_hat float, v2_hat float, surface_temperature float, core_temperature float, output_voltage float, soc float)")
    mycursor.execute("ALTER TABLE cells_relations ADD FOREIGN KEY (id_test) REFERENCES tests (id)")
    mycursor.execute("ALTER TABLE cells_relations ADD FOREIGN KEY (id_cell) REFERENCES cells (id)")
    mycursor.execute("ALTER TABLE observers_relations ADD FOREIGN KEY (id_test) REFERENCES tests (id)")
    mycursor.execute("ALTER TABLE observers_relationss ADD FOREIGN KEY (id_observers) REFERENCES observers (id)")
    mycursor.execute("ALTER TABLE measures_observers ADD FOREIGN KEY (id_observer) REFERENCES observers (id)")
    mycursor.execute("ALTER TABLE tests ADD FOREIGN KEY (id_action) REFERENCES actions (id)")
    mycursor.execute("ALTER TABLE measures ADD FOREIGN KEY (id_test) REFERENCES tests (id)")
    mycursor.execute("ALTER TABLE measures_observers ADD FOREIGN KEY (id_measure) REFERENCES measures (id)")
    mydb.commit()
    print("Table created")

print("Database initialized successfully")



# insert data into the table
if (databaseBool == False):
    mycursor.execute("INSERT INTO cells (name) VALUES ('BID001')")
    mycursor.execute("INSERT INTO cells (name) VALUES ('BID002')")
    mycursor.execute("INSERT INTO cells (name) VALUES ('BID003')")
    mycursor.execute("INSERT INTO cells (name) VALUES ('BID004')")
    mycursor.execute("INSERT INTO cells (name) VALUES ('BID005')")
    mycursor.execute("INSERT INTO cells (name) VALUES ('BID006')")
    mycursor.execute("INSERT INTO cells (name) VALUES ('BID007')")
    mycursor.execute("INSERT INTO cells (name) VALUES ('BID008')")
    mycursor.execute("INSERT INTO cells (name) VALUES ('BID009')")
    mycursor.execute("INSERT INTO cells (name) VALUES ('BID010')")
    mycursor.execute("INSERT INTO actions (name) VALUES ('Charge CC-CV')")
    mycursor.execute("INSERT INTO actions (name) VALUES ('Discharge Random')")
    mycursor.execute("INSERT INTO actions (name) VALUES ('Discharge Pulse')")
    mycursor.execute("INSERT INTO actions (name) VALUES ('Discharge HPPC')")
    mycursor.execute("INSERT INTO observers (name) VALUES ('Neuronal Network')")
    mycursor.execute("INSERT INTO observers (name) VALUES ('Kalman Filter')")
    mycursor.execute("INSERT INTO observers (name) VALUES ('Extended Kalman Filter')")
    mycursor.execute("INSERT INTO observers (name) VALUES ('State Observer')")
    print("Data inserted")

mydb.commit()



def startConn():
    mydbVar = mysql.connector.connect(
    host="localhost",
    user="root",
    password="")
    mydbVar = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="LIBS")
    mydbVar.commit()
    return mydbVar

#mycursor = mydb.cursor()

def createTest(id_action, comment, id_cells,crate,id_obs):
    sql = "INSERT INTO tests (time, id_action, comment, c_rate) VALUES (%s, %s, %s, %s)"
    val = (time.strftime('%Y-%m-%d %H:%M:%S'), id_action, comment, crate)
    mycursor.execute(sql, val)
    mydb.commit()
    id_test = mycursor.lastrowid
    for id_cell in id_cells:
        sql = "INSERT INTO cells_relations (id_test, id_cell) VALUES (%s, %s)"
        val = (id_test, id_cell)
        mycursor.execute(sql, val)
        mydb.commit()
    for id_ob in id_obs:
        sql = "INSERT INTO observers_relations (id_test, id_observer) VALUES (%s, %s)"
        val = (id_test, id_ob)
        mycursor.execute(sql, val)
        mydb.commit()

    return id_test


def createMeasure(id_test,time_test, current, output_voltage, ambient_temperature, surface_temperature):
    mydbVar=startConn()
    mydbCurs = mydbVar.cursor()
    time_test = time.strftime('%Y-%m-%d %H:%M:%S')
    sql = "INSERT INTO measures (id_test, time, current, output_voltage, ambient_temperature, surface_temperature) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (
    id_test, time_test, current, output_voltage, ambient_temperature, surface_temperature)
    mydbCurs.execute(sql, val)
    mydbVar.commit()
    #mydbCurs.lastrowid
    mydbCurs.close()
    mydbVar.close()
    return mydbCurs.lastrowid


def createMeasureObserver(id_measure, id_observer, v1_hat, v2_hat, surface_temperature, core_temperature,
                          output_voltage, soc):
    mydbVar=startConn()
    mydbCurs = mydbVar.cursor()
    sql = "INSERT INTO measures_observers (id_measure, id_observer, v1_hat, v2_hat, surface_temperature, core_temperature, output_voltage, soc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (id_measure, id_observer, v1_hat, v2_hat, surface_temperature, core_temperature, output_voltage, soc)
    mydbCurs.execute(sql, val)
    mydbVar.commit()
    mydbCurs.close()
    mydbVar.close()
    return mycursor.lastrowid


def getObservers():
    mycursor.execute("SELECT * FROM observers")
    observers = mycursor.fetchall()
    return observers


def getCells():
    mycursor.execute("SELECT * FROM cells")
    cells = mycursor.fetchall()
    return cells


def getActions():
    mycursor.execute("SELECT * FROM actions")
    actions = mycursor.fetchall()
    return actions


def getTests():
    mycursor.execute("SELECT * FROM tests")
    tests = mycursor.fetchall()
    return tests

def getMeasures(id_test, id_last_measure):
    global mydb
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="LIBS")
    global mycursor
    mycursor = mydb.cursor()

    if(id_last_measure == None):
        mycursor.execute("SELECT * FROM measures WHERE id_test = %s", (id_test))
    else:
        mycursor.execute("SELECT * FROM measures WHERE id_test = %s AND id > %s", (id_test, id_last_measure,))

    measures = mycursor.fetchall()
    #convert time into string 
    cpyMes = []
    for mes in measures:
        listCopy = list(mes)

        mycursor.execute("SELECT * FROM measures_observers WHERE id_measure = %s",(int(listCopy[0]),))
        obsMes = mycursor.fetchall()
        obsCopy = list(obsMes)

        if(len(obsCopy)== 0):
            time.sleep(0.0001)
            mydb.commit()
            mycursor.execute("SELECT * FROM measures_observers WHERE id_measure = %s",(int(listCopy[0]),))
            obsMes = mycursor.fetchall()
            obsCopy = list(obsMes)
            if(len(obsCopy)== 0):
                obsCopy=[(0,0,0,0,0,0,0,0,0)]

        
        tab = json.dumps({'id':listCopy[0],'id_test':listCopy[1],'time':str(listCopy[2]),'current':listCopy[3],
                          'output_voltage':listCopy[4],'ambient_temperature':listCopy[5],'surface_temperature':listCopy[6],'estimator_surface_temperature':obsCopy[0][5],'estimator_core_temperature':obsCopy[0][6]
                          ,'estimator_voltage':obsCopy[0][7],'estimator_soc':obsCopy[0][8]})
        cpyMes.append(tab)




    
    return cpyMes


def drawGraph():
    #datasets/BID002.txt
    #csv file :
        #time;voltage;current;idk;idk
    fig, ax = plt.subplots()
    with open('C:/Users/tjasr/Documents/GitHub/LIBS/LIBS_Back/datasetsBID002_CycRand_08052024.csv', 'r') as file:
        data = pd.read_csv(file, delimiter=';')
    timeTab = []
    voltageTab = []
    currentTab = []
    for i in range(len(data.values)):
        timeTab.append(i)
        voltageTab.append(data.values[i][1])
        currentTab.append(data.values[i][2])
    ax.plot(timeTab, voltageTab, label='voltage')
    ax.plot(timeTab, currentTab, label='current')
    plt.xlabel('time')
    plt.ylabel('voltage/current')
    ax.legend()
    plt.show()
    return



def addDataset():
    #datasets/BID002.txt
    #0: time, 1: voltage, 2: current
    with open('LIBS_Back/datasets/BID002.txt', 'r') as file:
        data = pd.read_csv(file, delimiter=';')
    #choose the action
    actions = getActions()
    print("Choose the action:")
    for action in actions:
        print(action)
    action = int(input())
    #choose the cells
    cells = getCells()
    print("Choose the cell:")
    for cell in cells:
        print(cell)
    cell = int(input())
    #comment
    print("Enter a comment:")
    comment = input()
    #create the test
    id_test = createTest(action, comment, [cell])

    for i in range(len(data.values)):
        createMeasure(id_test,data.values[i][0], data.values[i][2], data.values[i][1], 0, 0)
    return
def createObserver(name):
    sql = "INSERT INTO observers (name) VALUES (%s)"
    val = (name,)
    mycursor.execute(sql, val)
    mydb.commit()
    return mycursor.lastrowid

def getTest(id_test):
    
    con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="LIBS")
    cur = con.cursor()


    #get the test the action with the name the cell with the name the observers with the name
    # test = {"id":id_test, "time":time, "action":action, "comment":comment, "cells":[cell,cell,...]}
    cur.execute("SELECT * FROM tests WHERE id = %s", (id_test,))
    test = cur.fetchall()
    test = test[0]
    print(test)
    cur.execute("SELECT * FROM actions WHERE id = %s", (test[2],))
    action = cur.fetchall()
    action = action[0]
    print(action)

    cur.execute("SELECT * FROM cells_relations WHERE id_test = %s", (id_test,))
    cells = cur.fetchall()
    cellsTab = []
    print(cells)

    for cell in cells:
        cur.execute("SELECT * FROM cells WHERE id = %s", (cell[1],))
        cellsTab.append(cur.fetchall()[0])
    
    cur.execute("SELECT * FROM observers_relations WHERE id_test = %s", (id_test,))
    observers = cur.fetchall()
    observersTab = []

    for ob in observers:
        cur.execute("SELECT * FROM observers WHERE id = %s", (ob[1],))
        observersTab.append(cur.fetchall()[0])
    
    test = {"id":test[0], "time":str(test[1]), "action":{"id_action":action[0],"name":action[1]},
             "comment":test[3], "cells":cellsTab, "cRate":test[4],
             "observers":observersTab}
    return test


def getDataset(idTest):
    time = []
    voltage = []
    current = []
    # get the data of the test idTest
    mycursor.execute("SELECT output_voltage,current FROM measures WHERE id_test = %s ORDER BY ID ASC", (idTest,))
    measures = mycursor.fetchall()
    compteur = 0
    for measure in measures:
        time.append(compteur)
        compteur += 1
        voltage.append(measure[0])
        current.append(measure[1])
    return [time, voltage, current]


def exportDataset(idTest):
    #0: time, 1: voltage, 2: current

    #create the file 
    # f = open('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/datasets/'+str(idTest)+'.txt', 'w')

    blob = ""
    data = getDataset(idTest)
    for i in range(len(data[0])):
        blob += str(data[0][i])+';'+str(data[1][i])+';'+str(data[2][i])+'\n'

    # with open('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/datasets/'+str(idTest)+'.txt', 'w') as file:
    #     for i in range(len(data[0])):
    #         file.write(str(data[0][i])+';'+str(data[1][i])+';'+str(data[2][i])+'\n')
    # blob = open('C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/datasets/'+str(idTest)+'.txt', 'r').read()
    return blob


def createCell(name):
    sql = "INSERT INTO cells (name) VALUES (%s)"
    val = (name,)
    mycursor.execute(sql, val)
    mydb.commit()
    return mycursor.lastrowid

def importDataset(id_action, comment,cRate, cells,file,separator):
    idTest = createTest(id_action, comment, cells,cRate,[])
    #file = time;voltage;current;idk;idk
    data = np.loadtxt(file, delimiter=separator, skiprows=1, usecols=(1,2), dtype=float)
    voltage = []
    current = []
    for i in range(len(data)):
        voltage.append(data[i][0])
        current.append(data[i][1])
        createMeasure(idTest, time.strftime('%Y-%m-%d %H:%M:%S'), current[i], voltage[i], 0, 0)
    return idTest

def getAccuracy():
    #need to take every soc measures for each observer and compare them to the real soc
    #return the accuracy of each observer

    sql = "SELECT soc FROM measures_observers group by id_observer"
    mycursor.execute(sql)
    socs = mycursor.fetchall()

    sql = "SELECT soc FROM measures"


# importDataset(1, "comment",0.25, [1,2,3], 'C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back/datasets/TestChCn/BID002_ChConst050_04062024.txt', ';')

