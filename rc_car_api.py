# Interface for the RC Car API

import adapter

def initCar():
    """Initialize the car"""
    pass # Adapter auto-inits when imported

def moveForward(speed, time=2):
    """Move the car forward by a certain distance(in cm) in a certain time(in seconds). Note that distance is ignored for now"""
    adapter.start_move_forward(speed)

def moveBackward(speed, time=2):
    """Move the car backward by a certain distance(in cm) in a certain time(in seconds). Note that distance is ignored for now"""
    adapter.moveBackward(speed)

def setSteeringAngle(speed):
    """Set the steering angle of the car(-90 to 90, 0 is straight)"""
    adapter.setSteeringAngle(speed)

def stop():
    """Cuts short any movement in progress"""
    adapter.stop_move()

def readDistance(sensor="front"):
    """Read from a distance sensor(front, front_left, front_right, back_left, back_right)"""
    
    return 0

def setLight(light="headlights", state="on"):
    """
    Manually turn on/off a light(headlights, brake_lights, turn_signal_left, turn_signal_right).
    Note that turn signals automaticaly blink when on.
    Brake lights and turn signals are automatically managed, this function is to manually override them.
    """
    pass
