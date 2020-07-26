import serial
import time
import random
from copy import copy
import math

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
		phase += timeDifference * 60

		if phase >= threshold:
			phase = 0
			message = "Received"
			Xbee.write(message.encode())
			print("Pulse")


		if Xbee.inWaiting() > 0:
			message = Xbee.read(Xbee.inWaiting()).decode()
			print(message)
			phase = -math.sin((phase / 360) * (2 * math.pi)) * (360 / 2 * math.pi)


	except KeyboardInterrupt:
		print("Process Interrupted")
		break

Xbee.close()
