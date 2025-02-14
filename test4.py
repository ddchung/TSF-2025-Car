import cv2
import numpy as np
import sys
import rc_car_api
import pins

num = sys.argv[1]
num = int(num)

cap = cv2.VideoCapture(num)

cap.set(3,480)
cap.set(4,240)

angle = 0

while True:
	ok, img = cap.read()
	if not ok:
		break
	img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
	cv2.imshow("img",img)
	c = cv2.waitKey(1)
	if c == ord('q'):
		break
	if c == ord('w'):
		rc_car_api.moveForward(1, time=0.5)
	if c == ord('s'):
		rc_car_api.moveBackward(1, time=0.5)
	if c == ord('a'):
		rc_car_api.setSteeringAngle(-35)
	if c == ord('r'):
		rc_car_api.setSteeringAngle(0)
	if c == ord('d'):
		rc_car_api.setSteeringAngle(40)
	if c == ord('h'):
		pins.setHeadlights(True)
	if c == ord('t'):
		pins.setTaillights(True)
	if c == ord('n'):
		pins.setHeadlights(False)
		pins.setTaillights(False)


#rc_car_api.moveForward(1, time=1)
#rc_car_api.moveBackward(1, time=1)
#rc_car_api.setSteeringAngle(-90 0 90)
