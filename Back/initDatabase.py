import mysql.connector
import json

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)

mycursor = mydb.cursor()
# delete libs
mycursor.execute("DROP DATABASE IF EXISTS LIBS")


mycursor.execute("CREATE DATABASE LIBS")

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="LIBS"
)

mycursor = mydb.cursor()

# cells : id autoincrement primary key, name varchar(255), soc float
# cells_relations : id_test foreign key,id_cell foreign key
# observers : id autoincrement primary key, name varchar(255), function varchar(255)
# observers_relations : id_test foreign key,id_observer foreign key
# actions : id autoincrement primary key, name varchar(255), brief varchar(255), function varchar(255), chargeBool boolean, crate_bool boolean
# measures_soh : id autoincrement primary key, id_test foreign key, id_cell foreign key, voc float, r0 float, soc float, time timestamp autofill
# tests : id autoincrement primary key, time timestamp autofill, id_action foreign key, comment varchar(255), c_rate float, running_bool boolean
# measures : id autoincrement primary key, id_test foreign key, time timestamp autofill, current float, output_voltage float, ambient_temperature float,surface_temperature_plus float, surface_temperature_minus float 
# measures_observers : id autoincrement primary key, id_observer foreign key, surface_temperature float,core_temperature float,output_voltage float, soc float
# tests_relations : id_test foreign key, id_health_test foreign key,time_resting float
# health_tests : id autoincrement primary key, comment varchar(255), time timestamp autofill



mycursor.execute("CREATE TABLE health_tests (id INT AUTO_INCREMENT PRIMARY KEY, comment VARCHAR(255), time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
mycursor.execute("CREATE TABLE cells (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), soc FLOAT)")
mycursor.execute("CREATE TABLE observers (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), function VARCHAR(255))")
mycursor.execute("CREATE TABLE actions (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), brief VARCHAR(255), function VARCHAR(255), chargeBool BOOLEAN, crate_bool BOOLEAN)")
mycursor.execute("CREATE TABLE tests (id INT AUTO_INCREMENT PRIMARY KEY, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, id_action INT, comment VARCHAR(255), c_rate FLOAT, running_bool BOOLEAN, FOREIGN KEY (id_action) REFERENCES actions(id))")
mycursor.execute("CREATE TABLE cells_relations (id_test INT, id_cell INT, FOREIGN KEY (id_test) REFERENCES tests(id), FOREIGN KEY (id_cell) REFERENCES cells(id))")
mycursor.execute("CREATE TABLE observers_relations (id_test INT, id_observer INT, FOREIGN KEY (id_test) REFERENCES tests(id), FOREIGN KEY (id_observer) REFERENCES observers(id))")
mycursor.execute("CREATE TABLE measures_soh (id INT AUTO_INCREMENT PRIMARY KEY, id_test INT, id_cell INT, voc FLOAT, ia FLOAT, vb FLOAT, ib FLOAT, r0 FLOAT, soc FLOAT, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (id_test) REFERENCES tests(id), FOREIGN KEY (id_cell) REFERENCES cells(id))")
mycursor.execute("CREATE TABLE measures (id INT AUTO_INCREMENT PRIMARY KEY,id_cell INT, id_test INT, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, current FLOAT, output_voltage FLOAT, ambient_temperature FLOAT, surface_temperature_plus FLOAT, surface_temperature_minus FLOAT, FOREIGN KEY (id_test) REFERENCES tests(id), FOREIGN KEY (id_cell) REFERENCES cells(id))")
mycursor.execute("CREATE TABLE measures_observers (id INT AUTO_INCREMENT PRIMARY KEY,id_measure INT, id_observer INT, surface_temperature FLOAT, core_temperature FLOAT, output_voltage FLOAT, soc FLOAT, FOREIGN KEY (id_observer) REFERENCES observers(id),FOREIGN KEY (id_measure) REFERENCES measures(id))")
mycursor.execute("CREATE TABLE tests_relations (id_test INT, id_health_test INT, time_resting FLOAT, FOREIGN KEY (id_test) REFERENCES tests(id), FOREIGN KEY (id_health_test) REFERENCES health_tests(id))")


# cells : Id: auto,name:BID001,soc:1 
# cells : Id: auto,name:BID002,soc:1
# cells : Id: auto,name:BID003,soc:1
# cells : Id: auto,name:BID004,soc:1
# cells : Id: auto,name:BID005,soc:1
# cells : Id: auto,name:BID006,soc:1
# cells : Id: auto,name:BID007,soc:1
# cells : Id: auto,name:BID008,soc:1
# cells : Id: auto,name:BID009,soc:1
# cells : Id: auto,name:BID010,soc:1
# cells : Id: auto,name:BID011,soc:1

# actions : Id: auto,name:Constant Current-Constant Voltage,brief:CCCV,function:CCCV,chargeBool:1,crate_bool:1
# actions : Id: auto,name:Constant discharge,brief:ConstantDch,function:Constant,chargeBool:0,crate_bool:1
# actions : Id: auto,name:Dynamic stress test,brief:DST,function:DST,chargeBool:0,crate_bool:0
# actions : Id: auto,name:Hybrid pulse power characterization,brief:HPPC,function:HPPC,chargeBool:0,crate_bool:0
# actions : Id: auto,name:Pulse discharge,brief:PulseDch,function:Pulse,chargeBool:0,crate_bool:1
# actions : Id: auto,name:Random discharge,brief:RandomDch,function:Random,chargeBool:0,crate_bool:0
# actions : Id: auto,name:Random dybnamic stress test,brief:RandomDST,function:RandomDST,chargeBool:0,crate_bool:0

# observers : id: auto,name : observer, function: Observer
# observers : id: auto,name : Neural network dynamic,function : FNN
# observers : id: auto, name : Extended kalman filter, function : EKF



mycursor.execute("INSERT INTO cells (name, soc) VALUES ('BID001', 1)")
mycursor.execute("INSERT INTO cells (name, soc) VALUES ('BID002', 1)")
mycursor.execute("INSERT INTO cells (name, soc) VALUES ('BID003', 1)")
mycursor.execute("INSERT INTO cells (name, soc) VALUES ('BID004', 1)")
mycursor.execute("INSERT INTO cells (name, soc) VALUES ('BID005', 1)")
mycursor.execute("INSERT INTO cells (name, soc) VALUES ('BID006', 1)")
mycursor.execute("INSERT INTO cells (name, soc) VALUES ('BID007', 1)")
mycursor.execute("INSERT INTO cells (name, soc) VALUES ('BID008', 1)")
mycursor.execute("INSERT INTO cells (name, soc) VALUES ('BID009', 1)")
mycursor.execute("INSERT INTO cells (name, soc) VALUES ('BID010', 1)")
mycursor.execute("INSERT INTO cells (name, soc) VALUES ('BID011', 1)")

mycursor.execute("INSERT INTO observers (name, function) VALUES ('observer', 'Observer')")
mycursor.execute("INSERT INTO observers (name, function) VALUES ('Neural network dynamic', 'FNN')")
mycursor.execute("INSERT INTO observers (name, function) VALUES ('Extended kalman filter', 'EKF')")

mycursor.execute("INSERT INTO actions (name, brief, function, chargeBool, crate_bool) VALUES ('Constant Current-Constant Voltage', 'CCCV', 'CCCV', 1, 1)")
mycursor.execute("INSERT INTO actions (name, brief, function, chargeBool, crate_bool) VALUES ('Constant discharge', 'CDch', 'Constant', 0, 1)")
mycursor.execute("INSERT INTO actions (name, brief, function, chargeBool, crate_bool) VALUES ('Dynamic stress test', 'DST', 'DST', 0, 0)")
mycursor.execute("INSERT INTO actions (name, brief, function, chargeBool, crate_bool) VALUES ('Hybrid pulse power characterization', 'HPPC', 'HPPC', 0, 0)")
mycursor.execute("INSERT INTO actions (name, brief, function, chargeBool, crate_bool) VALUES ('Pulse discharge', 'PDch', 'Pulse', 0, 1)")
mycursor.execute("INSERT INTO actions (name, brief, function, chargeBool, crate_bool) VALUES ('Random pulse discharge', 'RPDch', 'Random', 0, 0)")
mycursor.execute("INSERT INTO actions (name, brief, function, chargeBool, crate_bool) VALUES ('Random stress discharge', 'RSDch', 'RDST', 0, 0)")
mycursor.execute("INSERT INTO actions (name, brief, function, chargeBool, crate_bool) VALUES ('Multi pulse discharge', 'MPDch', 'MPD', 0, 0)")
mycursor.execute("INSERT INTO actions (name, brief, function, chargeBool, crate_bool) VALUES ('Dynamic pulse discharge', 'DPDch', 'DPD', 0, 0)")

mydb.commit()
