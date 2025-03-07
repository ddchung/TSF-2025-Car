# Camera frame correction

import cv2
import numpy as np
import math
import defisheye
import scipy


def crop_frame(frame, top, bottom, left, right):
    # margins in percent
    h, w = frame.shape[:2]
    top = int(h * top)
    bottom = int(h * bottom)
    left = int(w * left)
    right = int(w * right)
    return frame[top:h-bottom, left:w-right]

def defish(frame):
    dtype = 'linear'
    format = 'fullframe'
    fov = 175
    new_fov = 137
    return defisheye.Defisheye(frame, dtype=dtype, format=format, fov=fov, pfov=new_fov).convert()

def correct(frame):
    frame = crop_frame(frame, 0, 0.29, 0.15, 0)
    cv2.imshow("cropped", frame)
    frame = defish(frame)
    return frame

if __name__ == "__main__":
    import white_balance
    video = cv2.VideoCapture('/home/tin/Downloads/Screen Recording 2025-02-25 at 8.04.05 AM.mov')
    while True:
        ok, frame = video.read()
        if not ok:
            break
        frame = correct(frame)
        frame = white_balance.automatic_white_balance(frame)
        cv2.imshow("frame", frame)
        key = cv2.waitKey(0)
        if key == ord('q'):
            break
        if key == ord('n'):
            for _ in range (10):
                video.read()
        if key == ord('m'):
            for _ in range (50):
                video.read()
        if key == ord(','):
            for _ in range (100):
                video.read()