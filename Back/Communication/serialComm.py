import serial
import time
arduino = None


try:
	arduino = serial.Serial(port='COM6', baudrate=115200, timeout=0.1)
	time.sleep(2)
	
	
except serial.serialutil.SerialException:
	print("Arduino not connected")
	exit()



# arduino = serial.Serial(port='COM6', baudrate=115200, timeout=0.1)

# arduino = serial.Serial(port='COM6', baudrate=115200, timeout=0.1) 
def write_read(x): 
	arduino.write(x) 
	time.sleep(0.9) 
	data = arduino.readline() 
	return data 

def send_data(data):
	result = write_read(bytes(data,encoding='utf-8'))
	stringRes = result.decode('utf-8')
	print(stringRes)
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
			
