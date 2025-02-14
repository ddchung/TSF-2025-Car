import cv2
import rc_car_api
import sys

import lane_follower

import blue_detect

for x in range(len(sys.argv)):
    if sys.argv[x] == "-r":
        x += 1
        lane_follower.REG_OF_INT = float(sys.argv[x])
    if sys.argv[x] == "-lg":
        x += 1
        lane_follower.LOWER_GREEN_HSV = int(sys.argv[x])
    if sys.argv[x] == "-ug":
        x += 1
        lane_follower.UPPER_GREEN_HSV = int(sys.argv[x])
    if sys.argv[x] == "-sf":
        lane_follower.SHOW_FRAME = True
    if sys.argv[x] == "-sh":
        lane_follower.SHOW_HSV = True
    if sys.argv[x] == "-sm":
        lane_follower.SHOW_MASKED = True
    if sys.argv[x] == "-se":
        lane_follower.SHOW_CROPPED_EDGES = True
    if sys.argv[x] == "-sl":
        lane_follower.SHOW_LINES = True
    if sys.argv[x] == "-sll":
        lane_follower.SHOW_LANE_LINES = True
    if sys.argv[x] == "-sq":
        qr_detect.SHOW_QR_CODES = True

# start webcam
cap = cv2.VideoCapture(0)

cap.set(3, 480)
cap.set(4, 240)

def calculate_move(frame):
    # Calculate lane lines and steering angle
    lane_lines = lane_follower.detect_lane(frame)
    steering_angle = lane_follower.compute_steering_angle(frame, lane_lines)
    
    new_angle = blue_detect.follow_blue(frame)
    #if new_angle != None:
    #    steering_angle = new_angle

    # Calculate whether or not we should move
    # Placeholder for now
    should_move = True

    if lane_lines is not None:
        frame = lane_follower.display_lines(frame, lane_lines, line_width=10)
        frame = lane_follower.display_heading_line(frame, steering_angle)
    
    if lane_follower.SHOW_LANE_LINES:
        cv2.imshow("lane_lines", frame)

    return [steering_angle, should_move]


steering_angle = 90

rc_car_api.initCar()

while True:
    success, frame = cap.read()
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    if not success:
        break
    if lane_follower.SHOW_FRAME:
        cv2.imshow("frame", frame)

    steering_angle, should_move = calculate_move(frame)

    rc_car_api.setSteeringAngle(steering_angle - 90)
    
    key = cv2.waitKey(1)
    if key == ord('w') and should_move:
        rc_car_api.moveForward(1, time=1)
    
    if key == ord('s') and should_move:
        rc_car_api.moveBackward(1, time=1)
    
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
