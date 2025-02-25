# python script to crop out top half of frames in directory

import cv2
import numpy as np
import glob

to_crop = glob.glob("/home/tin/TSF-2025-Car/lane_nav_data/IMG*.jpg")

for file in to_crop:
    frame = cv2.imread(file)
    # frame = frame[frame.shape[0] // 2:]
    frame = cv2.resize(frame, (200, 66))
    cv2.imwrite(file, frame)
    print(f"Processed {file}")
