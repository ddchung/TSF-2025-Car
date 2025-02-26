# Model prediction from webcam

import cv2
import tensorflow as tf
import tflite_runtime.interpreter as tflite
import numpy as np
import rc_car_api
import frame_client
from white_balance import automatic_white_balance
import correct_fov
import platform

# steering_model = tf.keras.models.load_model("lane_nav_output/lane_nav_model_final.keras")
try:
    steering_model = tflite.Interpreter(model_path="lane_nav_edgetpu.tflite", experimental_delegates=[tflite.load_delegate('libedgetpu.so.1')])
except:
    steering_model = tflite.Interpreter(model_path="lane_nav.tflite")
steering_model.allocate_tensors()
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
    image = white[int(height/2):, :]
    image = cv2.GaussianBlur(image, (3, 3), 0)
    # cv2.imshow("cropped", image)
    image = cv2.resize(image, (66, 200))
    image = np.expand_dims(image, axis=(-1))
    # cv2.imshow("resized", image)
    # image = image / 255
    # cv2.imshow("processed", image)
    image = np.asarray([image])
    # steering = steering_model.predict(image, verbose = 0)
    input_details = steering_model.get_input_details()
    output_details = steering_model.get_output_details()
    steering_model.set_tensor(input_details[0]['index'], image)
    steering_model.invoke()
    steering = steering_model.get_tensor(output_details[0]['index'])
    steering = steering[0][0]
    return (steering - 90) 

while True:
    frame = frame_client.recv()
    # frame = cv2.imread("/Users/tin/Desktop/fisheye.png")
    # frame = correct_fov.correct(frame)
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    # # crop out bottom part
    # h, w = frame.shape[:2]
    # frame = frame[:int(h*0.7), :]
    frame = correct_fov.correct(frame)
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
        rc_car_api.start_move_forward(40)
    if key == ord('s'):
        rc_car_api.start_move_backward(50)
    if key == ord(' '):
        rc_car_api.stop_move()

cv2.destroyAllWindows()
