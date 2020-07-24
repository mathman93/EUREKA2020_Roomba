import serial
import time
import random
from copy import copy

global Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200)

phase = random.randint(0,360)
threshold = 360
previousTime = time.time()

while True:

	try:
	
		currentTime = time.time()
		timeDifference = currentTime - previousTime
		phase = timeDifference * 90
		print (phase)

		if phase >= threshold:
			phase = 0
			message = "Received"
			Xbee.write(message.encode())
			print("Pulse")


		if Xbee.inWaiting() > 0:
			message = Xbee.read(Xbee.inWaiting()).decode()
			print(message)
			if 0 <= phase <= 180:
				phase -= 10
			if 180 < phase <= threshold:
				phase += 10


		previousTime = copy(currentTime)


	except KeyboardInterrupt:
		print("Process Interrupted")
		break

Xbee.close()