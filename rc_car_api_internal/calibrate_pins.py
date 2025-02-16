# Servo calibration script

import pins

print("Left servo calibration")

left_servo_value = 0
while True:
    angle = input("Enter angle: ")
    if angle == "ok":
        break
    try:
        angle = int(angle)
    except ValueError:
        print("Invalid angle")
        continue
    left_servo_value = angle
    pins.rawsetL(left_servo_value)

print("Right servo calibration")

right_servo_value = 0
while True:
    angle = input("Enter angle: ")
    if angle == "ok":
        break
    try:
        angle = int(angle)
    except ValueError:
        print("Invalid angle")
        continue
    right_servo_value = angle
    pins.rawsetR(right_servo_value)

print("=====================================")
print(f"Left servo value: {left_servo_value}")
print(f"Right servo value: {right_servo_value}")
print("=====================================")
