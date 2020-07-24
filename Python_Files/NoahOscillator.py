import serial
import time
import random
from copy import copy

global Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200)

phase = random.randint(0,360)
threshold = 360
previousTime = time.time()
currentTime = time.time()

while True:

	try:
	
		previousTime = copy(currentTime)
		currentTime = time.time()
		timeDifference = currentTime - previousTime
		phase += 5

		if phase >= threshold:
			phase = 0
			message = "Received"
			Xbee.write(message.encode())
			print("Pulse")


		if Xbee.inWaiting() > 0:
			message = Xbee.read(Xbee.inWaiting()).decode()
			print(message)
			if 0 <= phase <= 180:
				phase -= phase
			if 180 < phase <= threshold:
				phase += (360 - phase)


	except KeyboardInterrupt:
		print("Process Interrupted")
		break

Xbee.close()