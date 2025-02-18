# data collector for lane navigation

import cv2
import rc_car_api
import frame_client
import numpy as np
import correct_fov
import steering_line
import white_balance
import threading
import time
import os

SHOULD_SAVE = True
DATASET_DIR = "lane_nav_data"
os.makedirs(DATASET_DIR, exist_ok=True)

def process_frame(image):
    height, _ = image.shape[:2]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = (50, 40, 40)
    upper_green = (125, 255, 255)
    mask = cv2.inRange(hsv, lower_green, upper_green)
    white = 255 * np.ones_like(image)
    white = cv2.bitwise_and(white, white, mask=mask)
    white = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)
    image = white[int(height/2):, :]
    image = cv2.GaussianBlur(image, (3, 3), 0)
    image = cv2.resize(image, (200, 66))
    # image = image / 255
    return image

def save_frame(frame, angle):
    global DATASET_DIR
    filename = f"{DATASET_DIR}/frame_{angle + 90}_{len(os.listdir(DATASET_DIR))}.jpg"
    frame = process_frame(frame)
    cv2.imwrite(filename, frame)
    print(f"Saved {filename}")

angle = 0
while True:
    frame = frame_client.recv()
    if frame is None:
        break
    frame = white_balance.automatic_white_balance(frame)
    frame = correct_fov.correct(frame)
    org_frame = frame.copy()
    length_factor = abs(angle) / 75 + 1 # 1.4 @ |30|, 1 @ 0
    frame = steering_line.draw_steering_curve(frame, angle, length=135 * length_factor)
    cv2.putText(frame, f"Angle: {angle}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("frame", frame)

    rc_car_api.set_steering_angle(angle)

    key = cv2.waitKey(1) & 0xFF
    key = chr(key)
    if key == 'q':
        break
    elif key == 'a':
        angle -= 1
    elif key == 'd':
        angle += 1
    elif key == ' ':
        rc_car_api.stop_move()
    elif key == 's':
        rc_car_api.start_move_backward(40)
        if SHOULD_SAVE:
            save_frame(org_frame, angle)
        time.sleep(0.5)
        rc_car_api.stop_move()
    elif key == 'w':
        rc_car_api.start_move_forward(40)
        if SHOULD_SAVE:
            save_frame(org_frame, angle)
        time.sleep(0.5)
        rc_car_api.stop_move()
