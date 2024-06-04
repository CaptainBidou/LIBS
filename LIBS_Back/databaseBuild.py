import mysql.connector
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
        "CREATE TABLE tests (id integer PRIMARY KEY AUTO_INCREMENT, time timestamp, id_action integer, comment varchar(255))")
    mycursor.execute(
        "CREATE TABLE measures (id integer PRIMARY KEY AUTO_INCREMENT, id_test integer, time timestamp, current float, output_voltage float, ambient_temperature float, surface_temperature float)")
    mycursor.execute("CREATE TABLE observers (id integer PRIMARY KEY AUTO_INCREMENT, name varchar(255) UNIQUE)")
    mycursor.execute("CREATE TABLE cells_relations (id_test integer, id_cell integer)")
    mycursor.execute(
        "CREATE TABLE measures_observers (id integer PRIMARY KEY AUTO_INCREMENT, id_measure integer, id_observer integer, v1_hat float, v2_hat float, surface_temperature float, core_temperature float, output_voltage float, soc float)")
    mycursor.execute("ALTER TABLE cells_relations ADD FOREIGN KEY (id_test) REFERENCES tests (id)")
    mycursor.execute("ALTER TABLE cells_relations ADD FOREIGN KEY (id_cell) REFERENCES cells (id)")
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
    mycursor.execute("INSERT INTO actions (name) VALUES ('Charge Pulse')")
    mycursor.execute("INSERT INTO actions (name) VALUES ('Discharge Random')")
    mycursor.execute("INSERT INTO actions (name) VALUES ('Discharge Pulse')")
    mycursor.execute("INSERT INTO actions (name) VALUES ('Discharge HPPC')")
    mycursor.execute("INSERT INTO observers (name) VALUES ('Neuronal Network')")
    mycursor.execute("INSERT INTO observers (name) VALUES ('Kalman Filter')")
    mycursor.execute("INSERT INTO observers (name) VALUES ('Extended Kalman Filter')")
    mycursor.execute("INSERT INTO observers (name) VALUES ('State Observer')")
    print("Data inserted")

mydb.commit()


def createTest(id_action, comment, id_cells):
    sql = "INSERT INTO tests (time, id_action, comment) VALUES (%s, %s, %s)"
    val = (time.strftime('%Y-%m-%d %H:%M:%S'), id_action, comment)
    mycursor.execute(sql, val)
    mydb.commit()
    id_test = mycursor.lastrowid
    for id_cell in id_cells:
        sql = "INSERT INTO cells_relations (id_test, id_cell) VALUES (%s, %s)"
        val = (id_test, id_cell)
        mycursor.execute(sql, val)
        mydb.commit()
    return id_test


def createMeasure(id_test,time_test, current, output_voltage, ambient_temperature, surface_temperature):
    if(time_test == None):
        time_test = time.strftime('%Y-%m-%d %H:%M:%S')
    sql = "INSERT INTO measures (id_test, time, current, output_voltage, ambient_temperature, surface_temperature) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (
    id_test, time_test, current, output_voltage, ambient_temperature, surface_temperature)
    mycursor.execute(sql, val)
    mydb.commit()
    return mycursor.lastrowid


def createMeasureObserver(id_measure, id_observer, v1_hat, v2_hat, surface_temperature, core_temperature,
                          output_voltage, soc):
    sql = "INSERT INTO measures_observers (id_measure, id_observer, v1_hat, v2_hat, surface_temperature, core_temperature, output_voltage, soc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (id_measure, id_observer, v1_hat, v2_hat, surface_temperature, core_temperature, output_voltage, soc)
    mycursor.execute(sql, val)
    mydb.commit()
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
    if(id_last_measure == None):
        mycursor.execute("SELECT * FROM measures WHERE id_test = %s", (id_test,))
    else:
        mycursor.execute("SELECT * FROM measures WHERE id_test = %s AND id > %s", (id_test, id_last_measure))
    measures = mycursor.fetchall()
    return measures


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
