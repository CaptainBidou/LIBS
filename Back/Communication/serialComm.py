import serial
import time
arduino = None


try:
	arduino = serial.Serial(port='COM6', baudrate=115200, timeout=0.1)
except serial.serialutil.SerialException:
	print("Arduino not connected")
	exit()



# arduino = serial.Serial(port='COM6', baudrate=115200, timeout=0.1)

# arduino = serial.Serial(port='COM6', baudrate=115200, timeout=0.1) 
def write_read(x): 
	arduino.write(bytes(x, 'utf-8')) 
	time.sleep(0.05) 
	data = arduino.readline() 
	return data 

def send_data(data):
	result = write_read(data)
	stringRes = result.decode('utf-8')
	print(stringRes)
	floatRes = float(stringRes)
	return floatRes

if __name__ == '__main__':
	while True:
			send_data("5")
			time.sleep(1)
			
