# Full pipeline demo

import frame_client
import white_balance
import correct_fov
import cv2
import lane_nav_detector
import traffic_sign_detection
import numpy as np


def get_frame():
    frame = frame_client.recv()
    if frame is None:
        return None
    
    cv2.imshow("camera", frame)

    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

    cv2.imshow("rotated", frame)

    frame = correct_fov.correct(frame)

    cv2.imshow("corrected", frame)

    frame = white_balance.automatic_white_balance(frame)

    cv2.imshow("white balanced", frame)

    return frame

def lane_nav(frame):
    angle = lane_nav_detector.predict_steering(frame)

    # draw steering angle on the frame
    
    new = frame.copy()

    h, w = new.shape[:2]

    x1 = int(w/2)
    y1 = int(h)
    x2 = int(x1 + h/2 * np.tan(np.radians(angle)))
    y2 = int(h/2)

    # bizarre bug
    try:
        cv2.line(new, (x1, y1), (x2, y2), (0, 255, 0), 3)
    except:
        pass

    cv2.imshow("lane nav", new)

    return angle

def object_detection(frame):
    # detect traffic signs

    signs = traffic_sign_detection.detect_objects(frame)

    # draw traffic signs on the frame

    new = frame.copy()

    for sign in signs:
        name, x, y, w, h = sign
        cv2.rectangle(new, (x, y), (x+w, y+h), (255, 0, 255), 3)
        cv2.putText(new, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    cv2.imshow("object detection", new)

    return signs

if __name__ == "__main__":
    while True:
        frame = get_frame()
        if frame is None:
            break

        angle = lane_nav(frame)
        signs = object_detection(frame)

        print("angle:", angle)
        print("signs:", signs)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    cv2.destroyAllWindows()