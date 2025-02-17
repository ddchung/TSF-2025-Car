import cv2
import numpy as np
import math

def draw_steering_curve(image, steering_angle):
    # angle from -90 to 90

    CALIBRATION = 20

    steering_angle = steering_angle / 90
    height, width = image.shape[:2]

    points = []
    angle = steering_angle
    points.append((width // 2, height))
    for i in range(1, 100):
        x1 = points[i - 1][0]
        y1 = points[i - 1][1]
        x2 = int(np.sin(angle * np.pi / 2) * (10) + x1)
        y2 = int(y1 - np.cos(angle * np.pi / 2) * (10))
        if x1 < 0 or x1 > width or y1 < 0 or y1 > height:
            break
        points.append((x2, y2))
        angle += steering_angle / CALIBRATION
    
    for i in range(1, len(points)):
        cv2.line(image, points[i - 1], points[i], (0, 255, 0), 2)
    
    return image

if __name__ == "__main__":
    # cap = cv2.VideoCapture(0)
    angle = 0
    while True:
        # ret, frame = cap.read()
        # if not ret:
        #     break
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        image = draw_steering_curve(frame, angle)
        cv2.imshow("Steering Curve", image)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        if key == ord('a'):
            angle -= 5
        if key == ord('d'):
            angle += 5