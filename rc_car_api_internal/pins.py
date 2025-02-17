import platform
import os

HOST = "tins-pi.local"

# Crude raspberry pi detection
if True:
    from gpiozero.pins.pigpio import PiGPIOFactory
    from gpiozero import Servo
    from gpiozero import PWMOutputDevice

    # P1 P2
    # 1  0  Forward
    # 0  1  Backward
    # 0  0  Stop

    # PWM factory
    PWM_PIN_FACTORY = PiGPIOFactory(host=HOST)

    # Front right

    WHEEL_FR_P1 = 26
    WHEEL_FR_P2 = 19

    # Front left

    WHEEL_FL_P1 = 21
    WHEEL_FL_P2 = 20

    # Back left

    WHEEL_BR_P1 = 17
    WHEEL_BR_P2 = 27

    # Back right

    WHEEL_BL_P1 = 3
    WHEEL_BL_P2 = 2

    # Steering Servos

    SERVO_FR_P = 6
    SERVO_FL_P = 5

    # helper
    def MAP_RANGE(value, in_min, in_max, out_min, out_max):
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def SERVO_FL_COMP(angle):
        angle = int(angle)
        if angle == 0:
            return -10 / 90
        if angle > 0:
            if angle > 30:
                angle = 30
            return MAP_RANGE(angle, 0, 30, -10, 45) / 90
        if angle < 0:
            if angle < -45:
                angle = -45
            return MAP_RANGE(angle, 0, -45, -10, -90) / 90
        assert False
    
    def SERVO_FR_COMP(angle):
        angle = int(angle)
        if angle == 0:
            return -2 / 90
        if angle > 0:
            if angle > 30:
                angle = 30
            return MAP_RANGE(angle, 0, 30, -2, 45) / 90
        if angle < 0:
            if angle < -45:
                angle = -45
            return MAP_RANGE(angle, 0, -45, -2, -90) / 90
        assert False
    
    # Lights

    HEADLIGHTS = 24
    TAILLIGHTS = 23
    SUN = 12

    PIN_LIST = [SERVO_FR_P, SERVO_FL_P, WHEEL_FL_P1, WHEEL_FL_P2, WHEEL_FR_P1, WHEEL_FR_P2, WHEEL_BL_P1, WHEEL_BL_P2, WHEEL_BR_P1, WHEEL_BR_P2, HEADLIGHTS, TAILLIGHTS, SUN]

    SERVO_FR_OBJ = Servo(SERVO_FR_P, pin_factory=PWM_PIN_FACTORY)
    SERVO_FL_OBJ = Servo(SERVO_FL_P, pin_factory=PWM_PIN_FACTORY)

    HEADLIGHT_OBJ = PWMOutputDevice(HEADLIGHTS, pin_factory=PWM_PIN_FACTORY)
    TAILLIGHT_OBJ = PWMOutputDevice(TAILLIGHTS, pin_factory=PWM_PIN_FACTORY)
    SUN_OBJ = PWMOutputDevice(SUN, pin_factory=PWM_PIN_FACTORY)

    WHEEL_FR_P1_OBJ = PWMOutputDevice(WHEEL_FR_P1, pin_factory=PWM_PIN_FACTORY)
    WHEEL_FR_P2_OBJ = PWMOutputDevice(WHEEL_FR_P2, pin_factory=PWM_PIN_FACTORY)
    WHEEL_FL_P1_OBJ = PWMOutputDevice(WHEEL_FL_P1, pin_factory=PWM_PIN_FACTORY)
    WHEEL_FL_P2_OBJ = PWMOutputDevice(WHEEL_FL_P2, pin_factory=PWM_PIN_FACTORY)
    WHEEL_BR_P1_OBJ = PWMOutputDevice(WHEEL_BR_P1, pin_factory=PWM_PIN_FACTORY)
    WHEEL_BR_P2_OBJ = PWMOutputDevice(WHEEL_BR_P2, pin_factory=PWM_PIN_FACTORY)
    WHEEL_BL_P1_OBJ = PWMOutputDevice(WHEEL_BL_P1, pin_factory=PWM_PIN_FACTORY)
    WHEEL_BL_P2_OBJ = PWMOutputDevice(WHEEL_BL_P2, pin_factory=PWM_PIN_FACTORY)

    def setSpeed(speed):
        """Speed from -100-0-100"""
        speed = max(-100, min(100, speed))
        speed /= 100
        if speed >= 0:
            WHEEL_FL_P1_OBJ.value = speed
            WHEEL_FR_P1_OBJ.value = speed
            WHEEL_BL_P1_OBJ.value = speed
            WHEEL_BR_P1_OBJ.value = speed
            WHEEL_FL_P2_OBJ.value = 0
            WHEEL_FR_P2_OBJ.value = 0
            WHEEL_BL_P2_OBJ.value = 0
            WHEEL_BR_P2_OBJ.value = 0
        else:
            speed = -speed
            WHEEL_FL_P1_OBJ.value = 0
            WHEEL_FR_P1_OBJ.value = 0
            WHEEL_BL_P1_OBJ.value = 0
            WHEEL_BR_P1_OBJ.value = 0
            WHEEL_FL_P2_OBJ.value = speed
            WHEEL_FR_P2_OBJ.value = speed
            WHEEL_BL_P2_OBJ.value = speed
            WHEEL_BR_P2_OBJ.value = speed
    
    def setHeadlights(brightness):
        """Brightness from 0-100"""
        brightness = max(0, min(100, brightness))
        HEADLIGHT_OBJ.value = brightness / 100
    
    def setTaillights(brightness):
        """Brightness from 0-100"""
        brightness = max(0, min(100, brightness))
        TAILLIGHT_OBJ.value = brightness / 100
    
    def setSun(brightness):
        """Brightness from 0-100"""
        brightness = max(0, min(100, brightness))
        SUN_OBJ.value = brightness / 100
    
    def setSteeringAngle(angle):
        """Angle from -90(left) to 90(right), 0 in middle"""
        SERVO_FR_OBJ.value = SERVO_FR_COMP(angle)
        SERVO_FL_OBJ.value = SERVO_FL_COMP(angle)
    
    def rawsetL(value):
        SERVO_FL_OBJ.value = value / 90
    
    def rawsetR(value):
        SERVO_FR_OBJ.value = value / 90
    
elif False: # Not on raspberry pi, make tkinter UI showing stuff
    import tkinter as tk
    import math

    root = tk.Tk()
    root.title("RC Car")

    canvas = tk.Canvas(root, width=400, height=400)
    canvas.create_rectangle(0, 0, 400, 400, fill="white")
    canvas.pack()

    headlights = tk.Label(root, text="Headlights: 0")
    headlights.pack()

    taillights = tk.Label(root, text="Taillights: 0")
    taillights.pack()

    sun = tk.Label(root, text="Sun: 0")
    sun.pack()

    root.update()

    steering_angle = 0
    speed = 0

    def drawLine(angle, length):
        # Draws a line from bottom-center to angle
        length *= 4
        x = length * math.sin(math.radians(angle))
        y = length * math.cos(math.radians(angle))
        x = 200 + x
        y = 400 - y
        canvas.create_rectangle(0, 0, 400, 400, fill="white")
        canvas.create_line(200, 400, x, y, fill="red", width=4)
        root.update_idletasks()

    def setSpeed(s):
        global speed
        speed = s
        drawLine(steering_angle, speed)
    
    def setHeadlights(brightness):
        headlights.config(text=f"Headlights: {brightness}")
        root.update_idletasks()

    def setTaillights(brightness):
        taillights.config(text=f"Taillights: {brightness}")
        root.update_idletasks()

    def setSteeringAngle(angle):
        global steering_angle
        steering_angle = angle
        drawLine(steering_angle, speed)
    def setSun(brightness):
        sun.config(text=f"Sun: {brightness}")
        root.update_idletasks()
else:
    def setSpeed(speed):
        pass
    def setHeadlights(brightness):
        pass
    def setTaillights(brightness):
        pass
    def setSteeringAngle(angle):
        pass
    def setSun(brightness):
        pass
    
