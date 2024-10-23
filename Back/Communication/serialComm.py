import serial
import time
arduino = None


try:
	arduino = serial.Serial(port='COM8', baudrate=115200, timeout=0.1)
	time.sleep(2)
	
	
except serial.serialutil.SerialException:
	print("Arduino not connected")



# arduino = serial.Serial(port='COM6', baudrate=115200, timeout=0.1)

# arduino = serial.Serial(port='COM6', baudrate=115200, timeout=0.1) 

def parser(string):
	# add every ascii value of the char of the string 
	if string == "relay1=on\n":
		value = 2
	elif string == "relay1=off\n":
		value = 0
	elif string == "relay2=on\n":
		value = 3
	elif string == "relay2=off\n":
		value = 1
	elif string == "surfaceTemperaturePlus?\n":
		value = 5
	elif string == "surfaceTemperatureMinus?\n":
		value = 6
	elif string == "ambientTemperature?\n":
		value = 4
	
	return value 
		

def write_read(x): 
	time.sleep(0.05)
	arduino.write(x) 
	time.sleep(0.05) 
	data = arduino.readline() 
	return data 

def send_data(data):

	result = write_read(bytes(str(parser(data)), 'utf-8'))
	stringRes = result.decode('utf-8')
	# print(stringRes)
	floatRes = float(stringRes)
	return floatRes


send_data("relay1=off\n")
send_data("relay2=off\n")
if __name__ == '__main__':
	while True:
		data = input("Enter data to send: ") 
		if data == 'exit':
			break
		else:
			send_data(data)
			
