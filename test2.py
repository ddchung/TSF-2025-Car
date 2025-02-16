# Model prediction from webcam

import cv2
from tensorflow import keras
import numpy as np
import rc_car_api

# Load the model
model = keras.models.load_model("lane_navigation_final.keras")

cap = cv2.VideoCapture(0)
cap.set(3, 480)
cap.set(4, 240)

def img_preprocess(image):
    print("preprocess", flush=True)
    height, _ = image.shape[:2]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = (50, 40, 40)
    upper_green = (85, 255, 255)
    mask = cv2.inRange(hsv, lower_green, upper_green)
    white = 255 * np.ones_like(image)
    white = cv2.bitwise_and(white, white, mask=mask)
    white = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)
    image = white[int(height/4):, :]
    image = cv2.GaussianBlur(image, (3, 3), 0)
    image = cv2.resize(image, (200, 66))
    image = image / 255
    print("image shape", image.shape, flush=True)
    return image

while True:
    ret, frame = cap.read()
    if not ret:
        break
    # frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    img2 = frame.copy()
    frame = img_preprocess(frame)
    frame = np.asarray([frame])
    steering_angle = model.predict(frame)

    # draw predicted angle

    # -90 to 90
    angle = steering_angle[0][0] - 90

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

cap.release()
cv2.destroyAllWindows()
