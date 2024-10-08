# request the http://ufsc1.local:3000/api/datasources/proxy/uid/c3617d79-52d4-4dc4-bb64-da35041d54fe/query?db=uana&q=

###################################################################
##                   I M P O R T    P A C K A G E                ##
###################################################################
import requests
import json
# ['time', 'bmu1.main.SoC', 'bmu1.main.cmuSeries', 'bmu1.main.current', 'bmu1.main.deltaVoltage', 'bmu1.main.maxTemp', 'bmu1.main.maxVolt', 
# 'bmu1.main.minTemp', 'bmu1.main.minVolt', 'bmu1.main.power', 'bmu1.main.status', 'bmu1.main.tiemh', 'bmu1.main.timem', 'bmu1.main.times',
# 'bmu1.main.vPack', 'bmu1.main.warning', 'bmu1.s1.t1', 'bmu1.s1.t2', 'bmu1.s1.t3', 'bmu1.s1.t4', 'bmu1.s1.t5', 'bmu1.s1.t6', 'bmu1.s1.t7',
# 'bmu1.s1.t8', 'bmu1.s1.v1', 'bmu1.s1.v10', 'bmu1.s1.v11', 'bmu1.s1.v12', 'bmu1.s1.v13', 'bmu1.s1.v14', 'bmu1.s1.v15', 'bmu1.s1.v16', 'bmu1.s1.v2',
# 'bmu1.s1.v3', 'bmu1.s1.v4', 'bmu1.s1.v5', 'bmu1.s1.v6', 'bmu1.s1.v7', 'bmu1.s1.v8', 'bmu1.s1.v9', 'canCount', 'canStatus', 'timeStamp']

###################################################################
##                   G L O B A L   C O N S T A N T               ##
###################################################################
URL="http://ufsc1.local:8888/chronograf/v1/sources/0/proxy"


###################################################################
##            S T R U C T    D E C L A R A T I O N               ##
###################################################################
class req():
    def __init__(self,q):
        self.url = URL
        self.q = q
    def post(self):
        try:
            # date is a timestamp
            self.q = self.q + ' FROM "uana"."autogen"."bms" order by time desc limit 1 '
            print(self.q)
            r = requests.post(self.url, json={"db":"uana","query":self.q })
            return r.json()
        except:
            print("Error in request")
            return None


###################################################################
##            F U N C T I O N    D E C L A R A T I O N           ##
###################################################################
def get_data(q):
    r = req(q)
    data = r.post()
    return data

###################################################################

def measure(slot):
    q = "SELECT bmu1.s1.v"+str(slot)+", bmu1.s1.t"+str(slot)+" "
    obj =  get_data(q)
    print(obj)
    objet = {}
    objet["voltage"] = obj["results"][0]["series"][0]["values"][0][1]
    objet["temperature"] = obj["results"][0]["series"][0]["values"][0][2]
    return objet


def measure_soh():
    q = "SELECT bmu1.s1.v1, bmu1.s1.v2, bmu1.s1.v3, bmu1.s1.v4, bmu1.s1.v5, bmu1.s1.v6, bmu1.s1.v7, bmu1.s1.v8 "
    obj =  get_data(q)
    print(obj)
    objet = {}
    objet["v1"]= obj["results"][0]["series"][0]["values"][0][1]
    objet["v2"]= obj["results"][0]["series"][0]["values"][0][2]
    objet["v3"]= obj["results"][0]["series"][0]["values"][0][3]
    objet["v4"]= obj["results"][0]["series"][0]["values"][0][4]
    objet["v5"]= obj["results"][0]["series"][0]["values"][0][5]
    objet["v6"]= obj["results"][0]["series"][0]["values"][0][6]
    objet["v7"]= obj["results"][0]["series"][0]["values"][0][7]
    objet["v8"]= obj["results"][0]["series"][0]["values"][0][8]
    return objet
