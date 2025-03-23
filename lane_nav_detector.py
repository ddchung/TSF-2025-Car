# Model prediction from webcam

import cv2
import tensorflow as tf
import numpy as np

steering_model = tf.keras.models.load_model("lane_nav_model_final.keras")
def predict_steering(image):
    # get image shape
    height, _ = image.shape[:2]

    # filter for green
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = (50, 40, 40)
    upper_green = (100, 255, 230)
    mask = cv2.inRange(hsv, lower_green, upper_green)

    white = 255 * np.ones_like(image)
    white = cv2.bitwise_and(white, white, mask = mask)
    white = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)

    # crop out top half
    top = int(height/2)
    bottom = height
    image = white[top:bottom, :]

    # blur for reduced noise
    image = cv2.GaussianBlur(image, (3, 3), 0)

    # resize to model input size
    image = cv2.resize(image, (200, 66))
    image = image / 255

    # predict steering angle
    image = np.asarray([image])
    steering = steering_model.predict(image, verbose = 0)

    steering -= 90
    return int(steering)

if __name__ == "__main__":
    import rc_car_api
    import correct_fov
    import white_balance
    import frame_client
    while True:
        frame = frame_client.recv()
        if frame is None:
            break

        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        frame = correct_fov.correct(frame)
        frame = white_balance.automatic_white_balance(frame)

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
            rc_car_api.start_move_forward(70)
        if key == ord('s'):
            rc_car_api.start_move_backward(50)
        if key == ord(' '):
            rc_car_api.stop_move()

    cv2.destroyAllWindows()
