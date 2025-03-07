# traffic sign detection with YOLO

from ultralytics import YOLO
import numpy as np

# classes returned are on right column
#                              vvvvv
class_map = {
    'person'         :  'person'         ,
    'red light'      :  'red light'      ,
    'stop'           :  'stop'           ,
    'green light'    :  'green light'    ,
    'speed limit 10' :  'speed limit 10' ,
    'speed limit 20' :  'speed limit 20' ,
    'speed limit 30' :  'speed limit 30' ,
    'speed limit 40' :  'speed limit 40' ,
    'speed limit 50' :  'speed limit 50' ,
    'speed limit 60' :  'speed limit 60' ,
    'speed limit 70' :  'speed limit 70' ,
    'speed limit 80' :  'speed limit 80' ,
    'speed limit 90' :  'speed limit 90' ,
    'speed limit 100':  'speed limit 100',
    'speed limit 110':  'speed limit 110',
    'speed limit 120':  'speed limit 120',
}

object_model = YOLO("traffic_sign_detector.pt")
people_model = YOLO("yolov10n.pt")
def detect_objects(frame: np.ndarray) -> list[tuple[str, int, int, int, int]]:
    """
    detect traffic signs and people

    returns (name, x, y, w, h)

    x and y are top-left corner
    """
    objects = object_model.predict(frame, conf=0.6, verbose = False)
    people = people_model.predict(frame, conf=0.2, classes=[0], verbose = False) # chose a much lower value since lego people don't look that similar to people
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
            detected.append((class_map[name], x, y, w, h))
    for person in people:
        for box in person.boxes:
            x, y, w, h = box.xywh[0]
            x = int(x)
            y = int(y)
            w = int(w)
            h = int(h)
            x -= w // 2
            y -= h // 2
            detected.append((class_map['person'], x, y, w, h))
    return detected
