import socket
import json
import time
import http.client
###################################################################
##                   G L O B A L   C O N S T A N T               ##
###################################################################
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 5000  # Port to listen on (non-privileged ports are > 1023)

# def request(id, data):
#     for res in socket.getaddrinfo(HOST, PORT):
#         with socket.socket(res[0], socket.SOCK_STREAM) as s:
#             s.connect(res[4])
#             s.sendall(json.dumps({"id": id, "data": data}).encode())
#             data = s.recv(1024)
#             s.close()
#     return json.loads(data.decode())

def request(id, data):
    conn = http.client.HTTPConnection(HOST, PORT)
    conn.request("POST", "/", json.dumps({"id": id, "data": data}))
    response = conn.getresponse()
    return json.loads(response.read().decode())


#cellsTab = request(10, '{"id_action":5,"comment":"comment","cells":[1]}')
#print(cellsTab)
start = request(11,'{"id_test":6}')
print(start)
time.sleep(10)
start = request(12,'{"id_test":6}')
print(start)