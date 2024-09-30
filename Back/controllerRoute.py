###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################
import http.server
import json
import Class.importRoute as importRoute
import Class.importDatabase as importDatabase
import samplerRoute
from threading import Thread
# import sampler
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
def handleRouteGet(route,param):
    if route == "/":
        # print(param)
        return "{}"
    if route == "/cell":
        tab = importRoute.cell.get(param)
        tab2 = []
        for a in tab :
            tab2.append(importDatabase.Cell.cell(a).toString())
        return tab2
    if route == "/action":
        tab = importRoute.action.get(param)
        tab2 = []
        for a in tab:
            tab2.append(importDatabase.Action.action(a).toString())
        return tab2
    if route == "/observer":
        tab = importRoute.observer.get(param)
        tab2 = []
        for a in tab:
            tab2.append(importDatabase.Observer.observer(a).toString())
        return tab2
    if route == "/test":
        if param == None:
            tab = importRoute.test.get(None)
        else:
            tab = importRoute.test.get(param[0])
        tab2 = []
        for a in tab:
            tab2.append(importDatabase.Test.test(a).toString())
        return tab2
    if route == "/measure":
        tab = importRoute.measure.get(param)
        tab2 = []
        for a in tab:
            tab2.append(importDatabase.Measure.measure(a).toString())
        return tab2
    if route == "/measure_observer":
        tab= importRoute.measure_observer.get(param)
        tab2 = []
        for a in tab:
            tab2.append(importDatabase.MeasureEstimator.measure_estimator(a).toString())
        return tab2
    if route == "/measure_soh":
        tab= importRoute.measure_soh.get(param)
        tab2 = []
        for a in tab:
            tab2.append(importDatabase.MeasureSoh.soh_measureStat(a).toString())
        return tab2
    if route == "/health_test":
        tab = (importRoute.health_test.get(param))
        tab2 = []
        for a in tab:
            tab2.append(importDatabase.HealthTest.health_test(a).toString())
        return tab2

    if route == "/export":
        return importDatabase.Export.export(importRoute.export.get(param)).toString()

    if route == "/currentVoltage":
        tab = importRoute.test.get(param[0])
        tab2=[]
        for a in tab:
            tab2.append(importDatabase.Test.test(a))
        test=tab2[0]
        tab = samplerRoute.getVoltageCurrent(test)
        return tab
    if route == "/arduino":
        return samplerRoute.getArduinoStatus()
    if route == "/database":
        import Class.Route.phpMyAdmin as phpMyAdmin
        print(phpMyAdmin.getStatus())
        return phpMyAdmin.getStatus()
    if route == "/device":
        return samplerRoute.getDeviceStatus()

    if route =="/temperature":
        # ambientTemp = sampler.measureAmbient()
        ambientTemp=20.2
        ambientTemp = '{"ambientTemperature":'+str(ambientTemp)+'}'
        return ambientTemp


def handleRoutePost(route,param):
    if route=="/start_test":
        # start of the sampler with the test object
        print("on affiche l'id "+str(param["id"]))
        tab = importRoute.test.get(param["id"])
        tab2 = []
        for a in tab:
            tab2.append(importDatabase.Test.test(a))
        if (tab2[0].running_bool==0):
            importRoute.test.post(param["id"],1)
        samplerRoute.killThread = False
        thread = Thread(target=samplerRoute.setTest, args=(tab2[0],))
        thread.start()
        tab2[0].running_bool = 1
        return tab2[0].toString()
    if route =="/stop_test":
        tab = importRoute.test.get(param["id"])
        tab2=[]
        for a in tab:
            tab2.append(importDatabase.Test.test(a))
        test=tab2[0]
        if(test.running_bool):
            importRoute.test.post(param["id"],0)
            samplerRoute.killThread =True
            test.running_bool = 0
        return test.toString()
    pass

def handleRoutePut(route,param):
    if route=="/test":
        return importRoute.test.put(importDatabase.Test.testConstruct(param))
    if route=="/cell":
        return importRoute.cell.put(importDatabase.Cell.newCellConstruct(param))
    if route =="/health_test":
        return importRoute.health_test.put(importDatabase.HealthTest.health_testConstruct(param))
    

def handleRouteDelete(route,param):
    if route =="/test":
        return importRoute.test.delete(param[0])
    if route =="/health_test":
        return importRoute.health_test.delete(param[0])
    pass

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
        self.send_header("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT,DELETE")
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.end_headers()

        route = self.path
        param = self.path.split("?")
        if len(param) > 1:
            param = param[1]
        else:
            param = None
        if param != None :
            paramTab=[]
            for elt in param.split("&"):
                paramTab.append(elt)
            param = paramTab
        route = route.split("?")[0]

        response = "[{}]"
        response = handleRouteGet(route,param)
        # print(response)
        
        self.wfile.write(json.dumps(response).encode())
        


    def do_OPTIONS(self):
        # pre - flight request's response HTTP status code is 200 OK
        self.send_response(200)
        # self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT,DELETE")
        self.send_header("Access-Control-Allow-Headers",
                         "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        self.end_headers()
        


    def do_POST(self):
        #CORS policy
        self.send_response(200)
        # self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT,DELETE")
        self.send_header("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        self.end_headers()
        #print the data sent by the client
        route = self.path
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = json.loads(post_data)
        response = "[{}]"
        response = handleRoutePost(route,post_data)
        self.wfile.write(json.dumps(response).encode())
        
    def do_DELETE(self):
        #CORS policy
        self.send_response(200)
        # self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT,DELETE")
        self.send_header("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        self.end_headers()
        #print the data sent by the client
        route = self.path
        param = self.path.split("?")
        if len(param) > 1:
            param = param[1]
        else:
            param = None
        if param != None :
            paramTab=[]
            for elt in param.split("&"):
                paramTab.append(elt)
            param = paramTab
        route = route.split("?")[0]

        response = "[{}]"
        response = handleRouteDelete(route,param)
        

    def do_PUT(self):
        #CORS policy
        self.send_response(200)
        # self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT,DELETE")
        self.send_header("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
        self.end_headers()
        #print the data sent by the client
        route = self.path
        content_length = int(self.headers['Content-Length'])
        param = self.rfile.read(content_length)
        param = json.loads(param)
        response = "[{}]"
        response = handleRoutePut(route,param)
        self.wfile.write(json.dumps(response).encode())
        
    

        


###################################################################


# Create an object of the above class
handler_object = MyHttpRequestHandler

my_server = http.server.HTTPServer((HOST, PORT), handler_object)
print("Server started http://%s:%s" % (HOST, PORT))
while True:
    my_server.handle_request()
