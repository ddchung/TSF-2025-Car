
# imports
import cv2
import time
from ultralytics import YOLO
import rc_car_api
import numpy as np 
import threading
import tensorflow as tf

CAM_WIDTH = 480
CAM_HEIGHT = 240

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

def go():
    rc_car_api.set_steering_angle(steering_angle.get())
    speed_ = speed.get()
    if speed_ > 0:
        rc_car_api.start_move_forward(speed_)
        rc_car_api.set_light(1, 0) #< Tail light off
    elif speed_ < 0:
        rc_car_api.start_move_backward(-speed_)
        rc_car_api.set_light(1, 100) #< Tail light on
    else:
        rc_car_api.stop_move()
        rc_car_api.set_light(1, 50) #< Tail light half on

def red_light():
    speed.set(0)
    go()

last_stop_sign = 0
def stop_sign():
    global last_stop_sign
    global speed
    now = time.time()
    if now - last_stop_sign > 3:
        speed.set(0)
    else:
        speed.set(30)
    go()
    last_stop_sign = now

# Actions

object_actions = {
#   'object': {'threshold': percent, 'action': function}
    'red light':      {'threshold':.10,   'exclusive':True,   'disable':[],   'action': red_light},
    'person':   {'threshold':.10,   'exclusive':True,   'disable':[(0,0,.3,1), (.7,0,1,1)], 'action': red_light},
    'stop':     {'threshold':.15,   'exclusive':True,   'disable':[],   'action': stop_sign},
    'green light':    {'threshold':.10,   'exclusive':False,  'disable':[],   'action': lambda: None},
    'speed limit 10': {'threshold':.10,   'exclusive':False,  'disable':[],   'action': lambda: speed.set(8.3)},
    'speed limit 20': {'threshold':.10,   'exclusive':False,  'disable':[],   'action': lambda: speed.set(16.7)},
    'speed limit 30': {'threshold':.10,   'exclusive':False,  'disable':[],   'action': lambda: speed.set(25)},
    'speed limit 40': {'threshold':.10,   'exclusive':False,  'disable':[],   'action': lambda: speed.set(33.3)},
    'speed limit 50': {'threshold':.10,   'exclusive':False,  'disable':[],   'action': lambda: speed.set(41.7)},
    'speed limit 60': {'threshold':.10,   'exclusive':False,  'disable':[],   'action': lambda: speed.set(50)},
    'speed limit 70': {'threshold':.10,   'exclusive':False,  'disable':[],   'action': lambda: speed.set(58.3)},
    'speed limit 80': {'threshold':.10,   'exclusive':False,  'disable':[],   'action': lambda: speed.set(66.7)},
    'speed limit 90': {'threshold':.10,   'exclusive':False,  'disable':[],   'action': lambda: speed.set(75)},
    'speed limit 100':    {'threshold':.10,   'exclusive':False,  'disable':[],   'action': lambda: speed.set(83.3)},
    'speed limit 110':    {'threshold':.10,   'exclusive':False,  'disable':[],   'action': lambda: speed.set(91.7)},
    'speed limit 120':    {'threshold':.10,   'exclusive':False,  'disable':[],   'action': lambda: speed.set(100)},
}

def action(object):
    # object = (name, x, y, w, h)
    name, x, y, w, h = object
    name = name.lower()
    x1, y1, x2, y2 = x, y, x+w, y+h
    try:
        action = object_actions[name]
    except KeyError:
        print("WARNING: No action for", name)
        return
    threshold = action['threshold']
    if w * h / (CAM_WIDTH * CAM_HEIGHT) < threshold:
        return
    # Check if the object is in a disabled region
    for region in action['disable']:
        x1_, y1_, x2_, y2_ = region
        if x1 < x2_ * CAM_WIDTH and x2 > x1_ * CAM_WIDTH and y1 < y2_ * CAM_HEIGHT and y2 > y1_ * CAM_HEIGHT:
            return
    action['action']()
    if action['exclusive']:
        raise StopIteration

# Priority

object_priority = [
    'person',
    'red light',
    'stop',
    'green light',
    'speed limit 10',
    'speed limit 20',
    'speed limit 30',
    'speed limit 40',
    'speed limit 50',
    'speed limit 60',
    'speed limit 70',
    'speed limit 80',
    'speed limit 90',
    'speed limit 100',
    'speed limit 110',
    'speed limit 120',
]

def sort_objects(objects):
    def sort_predicate(x):
        try:
            return object_priority.index(x[0].lower())
        except ValueError:
            return len(object_priority)
    objects = sorted(objects, key=sort_predicate)
    return objects

# predictor threads

object_model = YOLO("traffic_sign_detector.pt")
people_model = YOLO("yolov10n.pt")
def predict_objects():
    frame_ = frame.get()
    objects = object_model.predict(frame_, conf=0.6, verbose = False)
    people = people_model.predict(frame_, conf=0.2, classes=[0], verbose = False) # chose a much lower value since lego people don't look that similar to people
    detected = []
    for object in objects:
        for box in object.boxes:
            x, y, w, h = box.xywh[0]
            x = int(x)
            y = int(y)
            w = int(w)
            h = int(h)
            x -= w // 2
            y -= h // 2
            name = object.names[int(box.cls)].lower()
            detected.append((name, x, y, w, h))
    for person in people:
        for box in person.boxes:
            x, y, w, h = box.xywh[0]
            x = int(x)
            y = int(y)
            w = int(w)
            h = int(h)
            x -= w // 2
            y -= h // 2
            detected.append(('person', x, y, w, h))
    detected_objects.set(detected)

steering_model = tf.keras.models.load_model("lane_navigation_final.keras")
def predict_steering():
    image = frame.get()
    height, _ = image.shape[:2]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = (50, 40, 40)
    upper_green = (85, 255, 255)
    mask = cv2.inRange(hsv, lower_green, upper_green)
    white = 255 * np.ones_like(image)
    white = cv2.bitwise_and(white, white, mask=mask)
    white = cv2.cvtColor(white, cv2.COLOR_BGR2GRAY)
    image = white[int(height/4):, :]
    image = cv2.GaussianBlur(image, (3, 3), 0)
    image = cv2.resize(image, (200, 66))
    image = image / 255
    image = np.asarray([image])
    steering = steering_model.predict(image, verbose = 0)
    steering_angle.set(int(steering[0][0] - 90))

def predict_objects_loop():
    while True:
        predict_objects()
        time.sleep(0.1)

def predict_steering_loop():
    while True:
        predict_steering()
        time.sleep(0.1)

# Common variables
speed = SyncedVariable(30)

frame = SyncedVariable(np.zeros((CAM_HEIGHT, CAM_WIDTH, 3), np.uint8))

steering_angle = SyncedVariable(90)
detected_objects = SyncedVariable([])

def print_summary():
    """
    example:
    +---------------------------------------------------------------+
    | Object          | X    | Y    | W    | H    | Priority        |
    +---------------------------------------------------------------+
    | red             | 100  | 200  | 50   | 50   | 1               |
    | green           | 200  | 200  | 50   | 50   | 2               |
    | stop            | 300  | 200  | 50   | 50   | 3               |
    +---------------------------------------------------------------+
    | Steering angle: 90                                            |
    | Speed: 30                                                     |
    +---------------------------------------------------------------+
    """
    print("\033[0m", end="")
    print("+---------------------------------------------------------------+")
    print("| Object          | X    | Y    | W    | H    | Priority        |")
    print("+---------------------------------------------------------------+")

    objects = detected_objects.get()
    objects = sort_objects(objects)
    angle = steering_angle.get()
    speed_ = speed.get()

    for object, idx in zip(objects, range(len(objects))):
        name, x, y, w, h = object
        name = name.lower()
        if idx == 0:
            print("\033[7m", end="")
        try:
            print(f"| {name:<15} | {x:<4} | {y:<4} | {w:<4} | {h:<4} | {object_priority.index(name):<15} |")
        except ValueError:
            print(f"| {name:<15} | {x:<4} | {y:<4} | {w:<4} | {h:<4} | {'err':<15} |")
        if idx == 0:
            print("\033[27m", end="")
    print("+---------------------------------------------------------------+")
    print(f"| Steering angle: {angle:<45} |")
    print(f"| Speed: {speed_:<54} |")
    print("+---------------------------------------------------------------+")
    print("\033[2J\033[H", end="")

def brightness(frame):
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    average_light_level = int(np.mean(gray_image))
    if average_light_level < 80:
        rc_car_api.set_light(3, 70)
        return True
    return False

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, CAM_WIDTH)
    cap.set(4, CAM_HEIGHT)

    ok, frame_ = cap.read()
    if not ok:
        print("Failed to read first frame")
        exit(1)

    frame.set(frame_)

    # Start the predictor threads
    threading.Thread(target=predict_objects_loop, daemon=True).start()
    threading.Thread(target=predict_steering_loop, daemon=True).start()

    while True:
        ok, frame_ = cap.read()
        if not ok:
            break

        too_dark = brightness(frame_)
        if too_dark:
            _, frame_ = cap.read() # reads again 
        frame.set(frame_)

        objects = detected_objects.get()
        print_summary()
        for object in sort_objects(objects):
            name, x, y, w, h = object
            cv2.rectangle(frame_, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame_, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            try:
                action(object)
            except StopIteration:
                break
        go()
        cv2.imshow("frame", frame_)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
