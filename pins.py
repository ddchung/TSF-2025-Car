#! /usr/bin/python

# Pins
"""
import RPi.GPIO as GPIO
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo

# Front left

WHEEL_FL_P1 = 26
WHEEL_FL_P2 = 19

# Front right

WHEEL_FR_P1 = 21
WHEEL_FR_P2 = 20

# Back left

WHEEL_BR_P1 = 17
WHEEL_BR_P2 = 27

# Back right

WHEEL_BL_P1 = 3
WHEEL_BL_P2 = 2

# Steering Servos

SERVO_PIN_FACTORY = PiGPIOFactory()

SERVO_FR_P = 6
SERVO_FL_P = 5

# Lights

HEADLIGHTS = 24
TAILLIGHTS = 23

GPIO.setmode(GPIO.BCM)

GPIO.setup([SERVO_FR_P, SERVO_FL_P, WHEEL_FL_P1, WHEEL_FL_P2, WHEEL_FR_P1, WHEEL_FR_P2, WHEEL_BL_P1, WHEEL_BL_P2, WHEEL_BR_P1, WHEEL_BR_P2, HEADLIGHTS, TAILLIGHTS], GPIO.OUT, initial=GPIO.LOW)

SERVO_FR_OBJ = Servo(SERVO_FR_P, pin_factory=SERVO_PIN_FACTORY)
SERVO_FL_OBJ = Servo(SERVO_FL_P, pin_factory=SERVO_PIN_FACTORY)"""

def cleanupPins():
    pass
    #GPIO.cleanup([SERVO_FR_P, SERVO_FL_P, WHEEL_FL_P1, WHEEL_FL_P2, WHEEL_FR_P1, WHEEL_FR_P2, WHEEL_BL_P1, WHEEL_BL_P2, WHEEL_BR_P1, WHEEL_BR_P2])

def startMoveForward():
    pass
    #GPIO.output([WHEEL_FL_P1, WHEEL_FR_P1, WHEEL_BL_P1, WHEEL_BR_P1], True)
    #GPIO.output([WHEEL_FL_P2, WHEEL_FR_P2, WHEEL_BL_P2, WHEEL_BR_P2], False)

def startMoveBackward():
    pass
    #GPIO.output([WHEEL_FL_P1, WHEEL_FR_P1, WHEEL_BL_P1, WHEEL_BR_P1], False)
    #GPIO.output([WHEEL_FL_P2, WHEEL_FR_P2, WHEEL_BL_P2, WHEEL_BR_P2], True)

def setHeadlights(on = False):
    pass
    #GPIO.output(HEADLIGHTS, on)

def setTaillights(on = False):
    pass
    #GPIO.output(TAILLIGHTS, on)

def setSteeringAngle(angle = 0):
    pass
    if angle < -50:
        angle = -50
    if angle > 50:
        angle = 50
    #SERVO_FR_OBJ.value = angle / 90
    #SERVO_FL_OBJ.value = angle / 90

def stopMove():
    pass
    #GPIO.output([WHEEL_FL_P1, WHEEL_FR_P1, WHEEL_BL_P1, WHEEL_BR_P1], False)
    #GPIO.output([WHEEL_FL_P2, WHEEL_FR_P2, WHEEL_BL_P2, WHEEL_BR_P2], False)

"""

if __name__ == '__main__':
    from time import sleep
    steering_angle = 0
    while (True):
        cmd = input()
        match cmd:
            case "w":
                startMoveForward()
                sleep(1)
                stopMove()
            case "s":
                startMoveBackward()
                sleep(1)
                stopMove()
            case "d":
                steering_angle += 15
                setSteeringAngle(steering_angle)
            case "a":
                steering_angle -= 15
                setSteeringAngle(steering_angle)
            case "q":
                cleanupPins()
                exit()
            case "h":
                setHeadlights(True)
            case "t":
                setTaillights(True)
            case "n":
                setHeadlights(False)
                setTaillights(False)
            case _:
                stopMove()
                setSteeringAngle(0)




"""
