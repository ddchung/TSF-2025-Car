# Model prediction from webcam

import cv2
import tensorflow as tf
import numpy as np
import rc_car_api
# import frame_client
from white_balance import automatic_white_balance
from correct_fov import defish

steering_model = tf.keras.models.load_model("lane_navigation_final.keras")
def predict_steering(image):
    height, _ = image.shape[:2]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = (50, 20, 40)
    upper_green = (125, 255, 255)
    mask = cv2.inRange(hsv, lower_green, upper_green)
    white = 255 * np.ones_like(image)
    white = cv2.bitwise_and(white, white, mask=mask)
    white = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)
    image = white[int(height/2):, :]
    image = cv2.GaussianBlur(image, (3, 3), 0)
    image = cv2.resize(image, (200, 66))
    image = image / 255
    cv2.imshow("processed", image)
    image = np.asarray([image])
    steering = steering_model.predict(image, verbose = 0)
    return steering - 90

while True:
    # frame = frame_client.recv()
    frame = cv2.imread("/Users/tin/Desktop/fisheye.png")
    frame = defish(frame)
    frame = automatic_white_balance(frame)
    if frame is None:
        break

    img2 = frame.copy()
    angle = predict_steering(frame)

    h, w = img2.shape[:2]
    x1 = int(w/2)
    y1 = h
    x2 = int(x1 + h/2 * np.tan(np.radians(angle)))
    y2 = int(h/2)

    cv2.line(img2, (x1, y1), (x2, y2), (0, 255, 0), 5)

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
