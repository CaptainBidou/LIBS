import json
import mysql.connector

def request(sql, data):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="LIBS"
    )
    mycursor = mydb.cursor()
    mycursor.execute(sql, data)
    myresult = mycursor.fetchall()
    mydb.commit()
    mydb.close()
    return myresult
def requestInsert(sql,data):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="LIBS"
    )
    mycursor = mydb.cursor()
    mycursor.execute(sql, data)
    myresult = mycursor.fetchall()
    mydb.commit()
    mydb.close()
    return mycursor.lastrowid

def getStatus():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    mycursor = mydb.cursor()
    # verif that libs exists
    mycursor.execute("SHOW DATABASES")
    databases = mycursor.fetchall()
    for database in databases:
        if database[0] == "libs":
            return True
    return False
