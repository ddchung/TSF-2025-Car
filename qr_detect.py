import cv2
import numpy as np
import math

qcd = cv2.QRCodeDetector()

SHOW_QR_CODES = True

def detect_qr_codes(frame):
    retval, data, points, _ = qcd.detectAndDecodeMulti(frame)
    output = []
    if retval:
        output = zip(data, points)
        if SHOW_QR_CODES:
            for d, p in output:
                if d:
                    print("Decoded QR Code:", d)
                    color = (0, 255, 0)
                else:
                    color = (0, 0, 255)
                frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)
    if SHOW_QR_CODES:
        cv2.imshow("QR_Codes", frame)
    return output

def follow_qr(frame, qr_codes):
    h, w, _ = frame.shape

    for d, p in qr_codes:
        x, y = calculate_center(p)
        angle = calculate_angle(x, y, w, h) + 90
        return angle
    return None

def calculate_center(corners):
    """
    Given four corner positions, calculates the approximate center position.

    :param corners: List of four points representing the corners [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    :return: (cx, cy) as the approximate center of the quadrilateral
    """
    # Convert the list of corners into a numpy array for easier manipulation
    corners = np.array(corners)
    
    # Compute the average of the x and y coordinates separately
    cx = np.mean(corners[:, 0])  # Mean of x-coordinates
    cy = np.mean(corners[:, 1])  # Mean of y-coordinates

    return int(cx), int(cy)

def calculate_angle(x, y, width, height):
    """
    Calculate the angle of a point (x, y) relative to the bottom-center of the screen.
    
    Parameters:
    x (int): x-coordinate of the point.
    y (int): y-coordinate of the point.
    width (int): Width of the screen.
    height (int): Height of the screen.
    
    Returns:
    float: The angle in degrees.
    """
    # Bottom-center of the screen is at (width / 2, height)
    center_x = width / 2
    center_y = height
    
    # Calculate differences
    dx = x - center_x
    dy = y - center_y
    
    # Use atan2 to calculate the angle in radians
    angle_rad = math.atan2(dy, dx)
    
    # Convert the angle to degrees
    angle_deg = math.degrees(angle_rad)
    
    return angle_deg
