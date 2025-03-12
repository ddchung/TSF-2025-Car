# traffic sign detection with YOLO

import numpy as np
from ultralytics import YOLO
import platform

device = None

if "darwin" in platform.system().lower():
    device = "mps:0" # Use Apple's Metal Performance Shaders
elif "linux" in platform.system().lower():
    device = "auto" # Use CUDA


class_map = {
    'person':   'person',
    'red':  'red light',
    'stop': 'stop',
    'green':    'green light',
    '20' :  'speed limit 20' ,
    '30' :  'speed limit 30' ,
    '40' :  'speed limit 40' ,
    '50' :  'speed limit 50' ,
    '60' :  'speed limit 60' ,
    '70' :  'speed limit 70' ,
}

object_model = YOLO("best (9).pt")
# people_model = YOLO("yolov10n.pt")
def detect_objects(frame: np.ndarray) -> list[tuple[str, int, int, int, int]]:
    """
    detect traffic signs and people

    returns (name, x, y, w, h)

    x and y are top-left corner
    """
    objects = object_model.predict(frame, conf=0.5, verbose = False, device=device)
    # people = people_model.predict(frame, conf=0.2, classes=[0], verbose = False, device=device) # chose a much lower value since lego people don't look that similar to people
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
    # for person in people:
    #     for box in person.boxes:
    #         x, y, w, h = box.xywh[0]
    #         x = int(x)
    #         y = int(y)
    #         w = int(w)
    #         h = int(h)
    #         x -= w // 2
    #         y -= h // 2
    #         detected.append((class_map['person'], x, y, w, h))
    return detected

if __name__ == "__main__":
    import cv2

    cap = cv2.VideoCapture(0)
    print("classes:", object_model.names)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        detected = detect_objects(frame)
        for name, x, y, w, h in detected:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )
        cv2.imshow("frame", frame)
        key = cv2.waitKey(1)
        if key == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
