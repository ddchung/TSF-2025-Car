# Model prediction from webcam

import cv2
import tensorflow as tf
import numpy as np
import rc_car_api
from white_balance import automatic_white_balance
import correct_fov
import os
import sys

SHOULD_SAVE = False
DIR = "lane_nav_data"
if SHOULD_SAVE:
    if not os.path.exists(DIR):
        os.mkdir(DIR)

file = None

if len(sys.argv) > 1:
    file = sys.argv[1]
    try:
        file = int(file)
    except:
        pass

if file is None:
    import frame_client

def save(frame, angle):
    global DIR
    num = len(os.listdir(DIR))
    cv2.imwrite(f"{DIR}/ai_frame_{angle}_{num}.jpg", frame)
    print(f"Saved {DIR}/ai_frame_{angle}_{num}.jpg")

steering_model = tf.keras.models.load_model("lane_nav_model_final.keras")
def predict_steering(image):
    height, _ = image.shape[:2]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # cv2.imshow("hsv", hsv)
    lower_green = (50, 40, 40)
    upper_green = (100, 255, 230)
    mask = cv2.inRange(hsv, lower_green, upper_green)
    white = 255 * np.ones_like(image)
    white = cv2.bitwise_and(white, white, mask=mask)
    white = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("white", white)
    top = int(height/2)
    bottom = height
    # bottom = int(height-(height/8))
    image = white[top:bottom, :]
    image = cv2.GaussianBlur(image, (3, 3), 0)
    # cv2.imshow("cropped", image)
    image = cv2.resize(image, (200, 66))
    # cv2.imshow("resized", image)
    image = image / 255
    black_and_white = mask.copy()
    # crop out top half
    black_and_white = black_and_white[int(height/2):, :]
    black_and_white = cv2.resize(black_and_white, (200, 66))
    image = np.asarray([image])
    steering = steering_model.predict(image, verbose = 0)
    if SHOULD_SAVE:
        save(black_and_white, int(steering))
    cv2.imshow("black and white", black_and_white)
    steering -= 90
    if abs(steering) > 20:
        steering *= 1.5
    return int(steering)

if file is not None:
    cap = cv2.VideoCapture(file)

while True:
    if file is None:
        frame = frame_client.recv()
        if frame is None:
            break
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        ok, frame = cap.read()
        if not ok:
            break
    frame = correct_fov.correct(frame)
    frame = automatic_white_balance(frame)

    img2 = frame.copy()
    angle = predict_steering(frame)

    h, w = img2.shape[:2]
    x1 = int(w/2)
    y1 = int(h)
    x2 = int(x1 + h/2 * np.tan(np.radians(angle)))
    y2 = int(h/2)

    try:
        cv2.line(img2, (x1, y1), (x2, y2), (0, 255, 0), 5)
    except:
        pass

    rc_car_api.set_steering_angle(angle)

    cv2.imshow("frame", img2)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    if key == ord('w'):
        rc_car_api.start_move_forward(50)
    if key == ord('s'):
        rc_car_api.start_move_backward(50)
    if key == ord(' '):
        rc_car_api.stop_move()

cv2.destroyAllWindows()
