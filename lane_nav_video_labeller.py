# Python script to label angles onto video frames

import cv2
import numpy as np
import glob
import correct_fov
import white_balance
import os

# Videos
video_files = glob.glob('/home/tin/Downloads/Screen Recording 2025-02-25 at 8.0*.mov')
OUTPUT_DIR = 'lane_nav_data/'

print(f"Videos: {video_files}")

def process_frame(frame):
    frame = correct_fov.correct(frame)
    frame = white_balance.automatic_white_balance(frame)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_green = np.array([50, 30, 40])
    upper_green = np.array([100, 255, 215])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    # crop out top half
    mask = mask[mask.shape[0] // 2:]
    mask = cv2.resize(mask, (200, 66))
    return mask

def query(frame):
    mask = process_frame(frame)
    cv2.imshow("mask", mask)
    cv2.imshow("frame", frame)

    angle = -1234

    def mouse(event, x, y, flags, param):
        nonlocal angle
        if event == cv2.EVENT_LBUTTONDOWN:
            height, width = mask.shape[:2]
            bottom_center = (width // 2, height)
            
            dx = x - bottom_center[0]
            dy = bottom_center[1] - y  # Invert y-axis (since y increases downward in images)
            
            angle = np.degrees(np.arctan2(dx, dy))
            angle = int(angle) + 90
            print(angle)
    
    def empty(*args):
        pass
    
    cv2.setMouseCallback("mask", mouse)

    while True:
        key = cv2.waitKey(1)
        if key == ord('q'):
            exit(0)
        if key == ord('n'):
            return
        if key == ord("m"):
            return "skip10"
        if key == ord(","):
            return "skip50"
        if angle != -1234:
            break
    
    cv2.setMouseCallback("mask", empty)

    # save frame with angle
    num = os.listdir(OUTPUT_DIR)
    num = len(num)
    name = f"frame_{angle}_{num}.jpg"
    cv2.imwrite(os.path.join(OUTPUT_DIR, name), mask)
    
    print(f"Saved {name}")

for video_file in video_files:
    video = cv2.VideoCapture(video_file)
    while True:
        ok, frame = video.read()
        if not ok:
            break
        ret = query(frame)
        if ret == "skip10":
            for _ in range(10):
                video.read()
        if ret == "skip50":
            for _ in range(50):
                video.read()
    video.release()
    cv2.destroyAllWindows()
    print(f"Finished {video_file}")
