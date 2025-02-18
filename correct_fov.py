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
    fov = 190
    new_fov = 120
    return defisheye.Defisheye(frame, dtype=dtype, format=format, fov=fov, pfov=new_fov).convert()

def correct(frame):
    frame = crop_frame(frame, 0, 0.29, 0.15, 0)
    frame = defish(frame)
    frame = scipy.ndimage.rotate(frame, 6, reshape=True)
    frame = crop_frame(frame, 0.1, 0.1, 0.2, 0.1)
    return frame

if __name__ == "__main__":
    import white_balance
    import frame_client
    img = cv2.imread("/Users/tin/fisheye_lanes.png")
    img = defish(img)
    img = white_balance.automatic_white_balance(img)
    cv2.imshow("frame", img)
    cv2.waitKey(0)
    