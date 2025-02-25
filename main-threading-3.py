# better and revised main code

import cv2
import time
from ultralytics import YOLO
import rc_car_api
import frame_client
import numpy as np 
import threading
import tensorflow as tf
from dataclasses import dataclass
from collections import defaultdict

CAM_WIDTH = 480
CAM_HEIGHT = 360

# Wrapper class to automatically lock/unlock
class SyncedVariable:
    def __init__(self, value):
        self._value = value
        self._lock = threading.Lock()

    def get(self):
        with self._lock:
            return self._value

    def set(self, value):
        with self._lock:
            self._value = value


class PredictedObjects:
    def __init__(self):
        self._objects = defaultdict(set)
        
    def add_object(self, obj_class, x, y, w, h):
        self._objects[obj_class].add((x, y, w, h))
    
    def get_objects(self, obj_class):
        return self._objects[obj_class]
    
    def get_all_objects(self):
        return self._objects
    
    def clear_objects(self, obj_class):
        del self._objects[obj_class]
    
    def clear_all_objects(self):
        self._objects.clear()

@dataclass
class CarState:
    speed : int
    steering_angle : int
    headlights : int
    taillights : int
    sun : int

@dataclass
class EnvironState:
    predicted_objects : PredictedObjects
    predicted_steering : int
    frame : np.ndarray

# Global variables
environ_state = SyncedVariable(EnvironState(PredictedObjects(), 0, np.zeros((CAM_HEIGHT, CAM_WIDTH, 3), dtype=np.uint8)))
speed_limit = SyncedVariable(0.3)

# actions
# signature: (CarState) -> CarState, bool
# returns: updated car state, whether to continue with other actions

def check_person(car_state):
    people = environ_state.get().predicted_objects.get_objects('person')

    # in percent
    ACTIVE_AREA = ((0., 1.), (1., 1.), (0.3, 0.5), (0.7, 0.5))
    ACTIVE_AREA = ((int(x * CAM_WIDTH), int(y * CAM_HEIGHT)) for x, y in ACTIVE_AREA)
    ACTIVE_AREA = tuple(ACTIVE_AREA)

    for person in people:
        # check if person is in active area
        x, y, w, h = person
        c_x, c_y = x + w // 2, y + h // 2
        if ACTIVE_AREA[0][0] < c_x < ACTIVE_AREA[1][0] and ACTIVE_AREA[0][1] < c_y < ACTIVE_AREA[1][1]:
            car_state.speed = 0
            car_state.taillights = 1
            return car_state, False
    return car_state, True

def check_stop_sign(car_state):
    stop_signs = environ_state.get().predicted_objects.get_objects('stop')

    if stop_signs:
        # TODO: make start moving after 3 seconds
        car_state.speed = 0
        car_state.taillights = 1
        return car_state, False
    return car_state, True

def check_red_light(car_state):
    red_lights = environ_state.get().predicted_objects.get_objects('red light')

    if red_lights:
        car_state.speed = 0
        car_state.taillights = 1
        return car_state, False
    return car_state, True

def check_green_light(car_state):
    green_lights = environ_state.get().predicted_objects.get_objects('green light')

    if green_lights:
        car_state.speed = speed_limit.get()
        car_state.taillights = 0.5
    return car_state, True

def check_speed_limit(car_state):
    MIN_SPEED_LIM = 10
    MAX_SPEED_LIM = 120
    STEP_SPEED_LIM = 10

    for i in range(MIN_SPEED_LIM, MAX_SPEED_LIM + 1, STEP_SPEED_LIM):
        speed_limit = environ_state.get().predicted_objects.get_objects(f'speed limit {i}')

        if speed_limit:
            car_state.speed = i / 3
            break
    return car_state, True

def correct_brightness(car_state):
    ADJ_TO = 80 # 0-255

    frame = environ_state.get().frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    brightness = np.mean(frame[:,:,2])

    correction = ADJ_TO - brightness
    correction /= 4 # stabilize
    car_state.headlights *= correction
    car_state.sun *= correction
    return car_state, True

def correct_steering(car_state):
    angle = environ_state.get().predicted_steering
    car_state.steering_angle = angle
    return car_state, True

# priority: first to last
actions = [
    # should always correct, so put at top
    correct_brightness,
    correct_steering,

    check_person,
    check_stop_sign,
    check_red_light,
    check_green_light,
    check_speed_limit,
]

def run_actions(car_state) -> CarState:
    for action in actions:
        car_state, cont = action(car_state)
        if not cont:
            break
    return car_state

# Input loops

def poll_camera():
    while True:
        frame = frame_client.get_frame()
        if frame is None:
            continue
        environ_state.set(environ_state.get()._replace(frame=frame))
        

def main():
    car_state = CarState(0, 0, 0, 0, 0)