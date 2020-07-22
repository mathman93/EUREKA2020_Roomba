import serial
import time
import random

global Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200)

phase = random.randint(0,360)
threshold = 360
sendTime = time.time()

while True:

	try:
	
		currentTime = time.time()
		timeDifference = currentTime - sendTime
		#phase += timeDifference * 45

		if phase >= threshold:
			phase = 0
			message = "Received"
			Xbee.write(message.encode())
			print("Pulse")
			timeSent = time.time()


		if Xbee.inWaiting() > 0:
			message = Xbee.read(Xbee.inWaiting()).decode()
			print(message)
			timeReceived = time.time()
			
		if phase >= 0 and phase <= 90:
			phase += 270
		if phase > 90 and phase <= 180:
			phase += 180
		if phase > 180 and phase <= 270:
			phase += 90
		if phase > 270 and phase <= 320:
			phase += 40
		if phase > 320 and phase <= 350:
			phase += 10
		if phase > 350 and phase <= 358:
			phase += 2
		if phase > 350:
			phase += .5




	except KeyboardInterrupt:
		print("Process Interrupted")
		break

Xbee.close()