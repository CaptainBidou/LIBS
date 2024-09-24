import serial
import time
arduino = None


try:
	arduino = serial.Serial(port='COM6', baudrate=115200, timeout=0.2)
	time.sleep(2)
	
	
except serial.serialutil.SerialException:
	print("Arduino not connected")
	exit()



# arduino = serial.Serial(port='COM6', baudrate=115200, timeout=0.1)

# arduino = serial.Serial(port='COM6', baudrate=115200, timeout=0.1) 

def parser(string):
	# add every ascii value of the char of the string 
	value = 0
	for i in string:
		value += ord(i)
	
	return str(value)
		

def write_read(x): 
	arduino.write(x) 
	time.sleep(0.3) 
	data = arduino.readline() 
	return data 

def send_data(data):
	result = write_read(bytes(parser(data),"utf-8"))
	stringRes = result.decode('utf-8')
	print(stringRes)
	floatRes = float(stringRes)
	return floatRes


# send_data("relay1=off\n")
# send_data("relay2=off\n")

if __name__ == '__main__':
	while True:
		data = input("Enter data to send: ") 
		if data == 'exit':
			break
		else:
			send_data(data)
			
