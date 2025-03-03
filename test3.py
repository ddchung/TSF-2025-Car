import cv2
import rc_car_api

import lane_follower
import frame_client
import correct_fov
import white_balance

def calculate_move(frame):
    # Calculate lane lines and steering angle
    lane_lines = lane_follower.detect_lane(frame)
    steering_angle = lane_follower.compute_steering_angle(frame, lane_lines)

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

while True:
    frame = frame_client.recv()
    if frame is None:
        break
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    frame = correct_fov.correct(frame)
    frame = white_balance.automatic_white_balance(frame)
    if lane_follower.SHOW_FRAME:
        cv2.imshow("frame", frame)

    steering_angle, should_move = calculate_move(frame)

    rc_car_api.set_steering_angle(steering_angle - 90)
    
    key = cv2.waitKey(1)
    if key == ord('w') and should_move:
        rc_car_api.start_move_forward(30)
    
    if key == ord('s') and should_move:
        rc_car_api.start_move_backward(30)

    if key == ord(' '):
        rc_car_api.stop_move()
    
    if key == ord('q'):
        break

cv2.destroyAllWindows()
