# python script to take videos and split them into frames


import cv2
import glob
import os
import white_balance
import correct_fov

OUT_DIR = "/Users/tin/Desktop/out_frames"

files = glob.glob("/Users/tin/Desktop/Screen Recording 2025-03-11 at 9.47.25 AM.mov")

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

for file in files:
    print(f"Processing {file}")
    cap = cv2.VideoCapture(file)
    while True:
        for _ in range(30):
            cap.read()
        ret, frame = cap.read()
        if not ret:
            break
        frame = white_balance.automatic_white_balance(frame)
        frame = correct_fov.correct(frame)
        frame_num = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        cv2.imwrite(f"{OUT_DIR}/{os.path.basename(file)}_{frame_num}.jpg", frame)
    cap.release()

print("Done")