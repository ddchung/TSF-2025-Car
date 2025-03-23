import cv2
import sys
import rc_car_api
import frame_client
import white_balance
import correct_fov

if len(sys.argv) > 1:
	num = sys.argv[1]
else:
	num = 0
num = int(num)

cap = cv2.VideoCapture(num)

cap.set(3,480)
cap.set(4,240)

angle = 0
speed = 0
while True:
	frame = frame_client.recv()
	if frame is None:
		break
	frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
	frame = correct_fov.correct(frame)
	img = white_balance.automatic_white_balance(frame)
	cv2.imshow("img",img)
	c = cv2.waitKey(1)
	if c == ord('q'):
		break
	if c == ord('w'):
		speed += 10
		if speed > 100:
			speed = 100
		rc_car_api.start_move_forward(speed)
	if c == ord('s'):
		speed -= 10
		if speed < -100:
			speed = -100
		rc_car_api.start_move_backward(-speed)
	if c == ord('a'):
		angle -= 10
		rc_car_api.set_steering_angle(angle)
	if c == ord('d'):
		angle += 10
		rc_car_api.set_steering_angle(angle)
	if c == ord(' '):
		speed = 0
		angle = 0
		rc_car_api.set_steering_angle(angle)
		rc_car_api.stop_move()
	if c == ord('h'):
		rc_car_api.set_light(0, 100)
	if c == ord('t'):
		rc_car_api.set_light(1, 100)
	if c == ord('x'):
		rc_car_api.set_light(3, 100)
	if c == ord('n'):
		rc_car_api.set_light(0, 0)
		rc_car_api.set_light(1, 0)
		rc_car_api.set_light(3, 0)
