###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################
import http.server
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
response = {"Hello":"World"}
thread = None
SonPID = None
###################################################################
##            F U N C T I O N    D E C L A R A T I O N           ##
###################################################################

###################################################################
##            S T R U C T    D E C L A R A T I O N               ##
###################################################################

#http server
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        #CORS policy
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST")
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.end_headers()

        # self.wfile.write(response.encode())#dict has not attribute encode
        self.wfile.write(json.dumps(response).encode())


    def do_OPTIONS(self):
        # pre - flight request's response HTTP status code is 200 OK
        self.send_response(200)
        # self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT")
        self.send_header("Access-Control-Allow-Headers",
                         "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        self.end_headers()


    def do_POST(self):
        #CORS policy
        self.send_response(200)
        # self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT")
        self.send_header("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        self.end_headers()
        #print the data sent by the client
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
       # print(post_data)
        #post_data is a binary data b'{"id":1,"data":{"nothing":"nothing"}}'

        post_data = json.loads(post_data)
        id = post_data["id"]
        #print(id)
        data= post_data["data"]
        #print(post_data["data"])

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
           # try :
            response = databaseBuild.getMeasures(data["id_test"], data["id_last_measure"])
            #except IndexError as e:
                #print("Catch error :")
                #print(str(e))
                #sampler.initDevice(sampler.devices)
                #response = []
                #sampler.interrupt = Thread(target=sampler.Counter, args=(sampler.SAMPLING_RATE,sampler.IDTEST,sampler.devices.electLoad,"EL",))
                #sampler.interrupt.start()
            pass
        elif id == 5:
            # Create an observer
            # data = {‘Name’:,’Comment’:}
            # dataRepsonse = [{‘id’:,’Name’:}]
            response = databaseBuild.createObserver(data["name"], data["comment"])
            response = databaseBuild.getObservers()
            pass
        elif id == 6:
            # get the test
            # data = {‘id_test’:}
            # dataRepsonse = [{‘id’:,’id_action’:,’comment’:,’cells’:[]}]
            response = databaseBuild.getTest(data["id_test"])
            pass
        elif id == 7:
            # get the tests
            # data = {}
            # dataRepsonse = [{‘id’:,’id_action’:,’comment’:,’cells’:[]}]
            response = databaseBuild.getTests()
            temp = []
            for i in response:
                i = databaseBuild.getTest(i[0])
                temp.append(i)
            response = temp
            
            pass
        elif id ==8 :
            # export dataset 
            # data = {‘id_test’:}
            # dataRepsonse = file
            response = databaseBuild.exportDataset(data)
            pass

        elif id == 10:
            # Create a test
            # data = {'id_action':,'comment':,cells:[]}
            # dataRepsonse = {‘id’:}

            response = databaseBuild.createTest(data["id_action"], data["comment"], data["cells"],data["cRate"],data["observers"])
            print(response)
            pass
        elif id == 11:
            # Start a test
            # data = {'id_test':,observer:[]}
            # call the sampler
            # dataRepsonse = boolean
            # create a thread for the test
            sampler.killThread = False
            thread = Thread(target=sampler.setTest, args=(data["id_test"],data["id_test"]))
            thread.start()
            response = True
            pass
        elif id == 12:
            # Stop a test
            # data = {'id_test':}
            # stop the sampler
            # dataRepsonse = boolean
            # sampler.interrupt.stop()
            sampler.killThread = True
            thread2 = Thread(target=sampler.exitProg)
            thread2.start()
            thread2.join()
            response = True
            pass
        else:
            exit()

        self.wfile.write(json.dumps(response, indent=4, sort_keys=True, default=str).encode())



###################################################################


# Create an object of the above class
handler_object = MyHttpRequestHandler

my_server = http.server.HTTPServer((HOST, PORT), handler_object)
print("Server started http://%s:%s" % (HOST, PORT))
while True:
    my_server.handle_request()
