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
heading = int(input("Enter desired heading (integers only)."))
cycleLength = 360
frequency = 15

time1 = time.time() - (time.time() % cycleLength)

while True:

	try:
	
		previousTime = copy(currentTime)
		currentTime = time.time()
		timeDifference = currentTime - previousTime
		phase += timeDifference * 60

		timer = time.time() - time1
		phase = heading + (timer * frequency)

		if phase >= threshold:
			phase = 0
			message = "Received"
			Xbee.write(message.encode())
			print("Pulse")
			ptint ("Phase: %f" % phase)
			time1 += cycleLength


		if Xbee.inWaiting() > 0:
			message = Xbee.read(Xbee.inWaiting()).decode()
			print(message)
			if 0 <= phase <= 180:
				heading -= phase
			if 180 < phase <= threshold:
				heading += (threshold - phase)
			if heading >= 360:
                heading -= 360
                time1 += cycleLength
                print("The heading is: %f" % heading)
            if heading <= 0:
                heading += 360
                time1 -= cycleLength
                print("Heading: %f" % heading)
            print("Phase: %f" % phase)

	except KeyboardInterrupt:
		print("Process Interrupted")
		break

Xbee.close()