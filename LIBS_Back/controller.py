###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################
import socket
import databaseBuild
import sampler
import json
from threading import Thread

###################################################################
##                   G L O B A L   C O N S T A N T               ##
###################################################################
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 5000  # Port to listen on (non-privileged ports are > 1023)

###################################################################
##                   G L O B A L   V A R I A B L E S             ##
###################################################################
response = "Hello World"
thread = None
SonPID = None
###################################################################
##            F U N C T I O N    D E C L A R A T I O N           ##
###################################################################

###################################################################
##            S T R U C T    D E C L A R A T I O N               ##
###################################################################

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # can access by http://127.0.0.1:5000
        s.bind((HOST, PORT))  #Start TCP communication
        s.listen()  # Waiting some query of the client
        conn, addr = s.accept()  #Accept query of the  client
        print("Waiting for a connection")
        with conn:

            data = conn.recv(1024)  #Read data sent by client

            msg = data.decode("utf-8")  #Decode binary to string
            print("msg :"+msg)
            #msg is a json { "id": 1, "data": { ... } }
            msg = json.loads(msg)
            #AttributeError: 'dict' object has no attribute 'id'
            msg = type('obj', (object,), msg)()

            id = msg.id

            # data = msg.data.decode("utf-8")
            data = json.loads(str(msg.data))
            data = type('obj', (object,), data)()
            print(data)


            response = None

            if id == 1:
                # Get the actions from the database
                # data = {}
                # dataRepsonse = [{‘id’:,’Name’:}]
                response = databaseBuild.getActions()
                pass

            elif id == 2:
                # Get the cells from the database
                # data = {}
                # dataRepsonse = [{‘id’:,’Name’:}]
                response = databaseBuild.getCells()
                pass
            elif id == 3:
                # Get the observers from the database
                # data = {}
                # dataRepsonse = [{‘id’:,’Name’:}]
                response = databaseBuild.getObservers()
                pass
            elif id == 4:
                # Get the Measures from the database / we can put null for the id_last_measure and we will have all the measures
                # data = {‘id_test’:,'id_last_measure':}
                # dataRepsonse = [{‘Time’,’Current’,’Voltage’}]
                response  = databaseBuild.getMeasures(data.id_test, data.id_last_measure)

                pass
            elif id == 5:
                # Create an observer
                # data = {‘Name’:,’Comment’:}
                # dataRepsonse = [{‘id’:,’Name’:}]
                response = databaseBuild.createObserver(data.name, data.comment)
                response = databaseBuild.getObservers()
                pass
            elif id == 10:
                # Create a test
                # data = {'id_action':,'comment':,cells:[]}
                # dataRepsonse = {‘id’:}
                print(data.id_action)
                response = databaseBuild.createTest(data.id_action, data.comment, data.cells)
                pass

            elif id == 11:
                # Start a test
                # data = {'id_test':,observer:[]}
                # call the sampler
                # dataRepsonse = boolean
                # create a thread for the test
                sampler.killThread = False
                thread = Thread(target=sampler.setTest, args=(data.id_test,))
                thread.start()
                response = True
                pass

            elif id == 12:
                # Stop a test
                # data = {'id_test':}
                # stop the sampler
                # dataRepsonse = boolean
                #sampler.interrupt.stop()
                sampler.killThread = True
                thread2 = Thread(target=sampler.exitProg)
                thread2.start()
                thread2.join()
                response = True
                pass
            else:
                break

            conn.sendall(json.dumps(response).encode())



