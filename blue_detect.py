# Blue detector using OpenCV

import cv2
import numpy as np
import math

def follow_blue(frame):
    # Convert the frame to the HSV color space to isolate the blue color range
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the blue color range in HSV (adjust the lower and upper limits as necessary)
    lower_blue = np.array([100, 150, 50])  # Lower bound for blue color
    upper_blue = np.array([140, 255, 255])  # Upper bound for blue color

    # Create a mask for the blue regions
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Find contours in the binary image (blue mask)
    contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest blue region by contour area
    largest_contour = None
    max_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
            largest_contour = contour

    if largest_contour is None:
        return None  # No large blue splotch found

    # Compute the center of the largest blue splotch (centroid of the contour)
    M = cv2.moments(largest_contour)
    if M["m00"] == 0:  # Prevent division by zero if the contour has zero area
        return None
    center_x = int(M["m10"] / M["m00"])
    center_y = int(M["m01"] / M["m00"])

    # Get the bottom-center point of the frame
    height, width = frame.shape[:2]
    bottom_center = (height - 1, width // 2)

    # Calculate the difference in x and y between the bottom-center and the center of the blue splotch
    delta_x = center_x - bottom_center[1]
    delta_y = bottom_center[0] - center_y  # Notice: subtracting y because the y-axis increases downwards

    # Calculate the angle using arctan
    angle = math.degrees(math.atan2(delta_y, delta_x))  # atan2 gives angle relative to horizontal axis

    return 180 - angle