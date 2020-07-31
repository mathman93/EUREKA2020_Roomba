import serial
import time
import random
from copy import copy

global Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200)

threshold = 360
previousTime = time.time()
currentTime = time.time()
timer = time.time()
if (time.time() - timer) > 1:
	timer += 1.0
heading = int(input("Enter desired heading: "))
frequency = 15
strength = .6
phase = heading

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
			if 0 <= phase <= 180:
				heading -= strength * phase
			if 180 < phase <= threshold:
				heading += strength * (threshold - phase)
			timer = timeDifference
			phase = heading + (timer * frequency)
			print("The heading is")
			print(phase)

	except KeyboardInterrupt:
		print("Process Interrupted")
		break

Xbee.close()