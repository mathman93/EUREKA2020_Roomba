import serial
import time
import random

global Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200)

phase = random.randint(0,360)
threshold = 360
previousTime = time.time()

while True:

	try:
	
		currentTime = time.time()
		timeDifference = currentTime - previousTime

		if phase >= threshold:
			phase = 0
			message = "Received"
			Xbee.write(message.encode())
			print("Pulse")


		if Xbee.inWaiting() > 0:
			message = Xbee.read(Xbee.inWaiting()).decode()
			print(message)
			

	previousTime = currentTime


	except KeyboardInterrupt:
		print("Process Interrupted")
		break

Xbee.close()