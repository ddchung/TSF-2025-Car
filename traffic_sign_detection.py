# traffic sign detection with YOLO

import platform

if "linux" not in platform.system().lower():
    from ultralytics import YOLO
    import numpy as np
    import ultralytics

    # classes returned are on right column
    #                              vvvvv
    class_map = {
        "person": "person",
        "red light": "red light",
        "stop": "stop",
        "green light": "green light",
        "maximum-speed-limit-10": "speed limit 10",
        "maximum-speed-limit-20": "speed limit 20",
        "maximum-speed-limit-30": "speed limit 30",
        "maximum-speed-limit-40": "speed limit 40",
        "maximum-speed-limit-50": "speed limit 50",
        "maximum-speed-limit-60": "speed limit 60",
        "maximum-speed-limit-70": "speed limit 70",
        "maximum-speed-limit-80": "speed limit 80",
        "maximum-speed-limit-90": "speed limit 90",
        "maximum-speed-limit-100": "speed limit 100",
        "maximum-speed-limit-110": "speed limit 110",
        "maximum-speed-limit-120": "speed limit 120",
    }

    object_model = YOLO("Traffic-Sign-Detection-AI/runs/detect/train/weights/best.pt")
    people_model = YOLO("yolov10n.pt")


    def detect_objects(frame: np.ndarray) -> list[tuple[str, int, int, int, int]]:
        """
        detect traffic signs and people

        returns (name, x, y, w, h)

        x and y are top-left corner
        """
        objects = object_model.predict(frame, conf=0.6, verbose=False)
        people = people_model.predict(
            frame, conf=0.2, classes=[0], verbose=False
        )  # chose a much lower value since lego people don't look that similar to people
        detected = []
        for object in objects:
            if object.boxes is None:
                print("WARN: No boxes found")
                continue
            for box in object.boxes:
                x, y, w, h = box.xywh[0]
                x = int(x)
                y = int(y)
                w = int(w)
                h = int(h)
                x -= w // 2
                y -= h // 2
                name = object.names[int(box.cls)].lower()
                name = "-".join(name.split("--")[1:-1])
                try:
                    detected.append((class_map[name], x, y, w, h))
                except KeyError:
                    pass
        for person in people:
            if person.boxes is None:
                print("WARN: No boxes found in people")
                continue
            for box in person.boxes:
                x, y, w, h = box.xywh[0]
                x = int(x)
                y = int(y)
                w = int(w)
                h = int(h)
                x -= w // 2
                y -= h // 2
                try:
                    detected.append((class_map["person"], x, y, w, h))
                except KeyError:
                    pass
        return detected
else: # linux
    from PIL import Image
    import edgetpu.detection.engine
    import numpy as np


    class_map = {
        "Green": "green light",
        "Person": "person",
        "Red": "red light",
        "Stop": "stop",
        "Limit 25": "speed limit 30",
        "Limit 40": "speed limit 70",
    }

    engine = edgetpu.detection.engine.DetectionEngine("road_signs_quantized_edgetpu.tflite")
    def detect_objects(frame: np.ndarray) -> list[tuple[str, int, int, int, int]]:
        """
        detect traffic signs and people

        returns (name, x, y, w, h)

        x and y are top-left corner
        """
        detected = []
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        results = engine.detect_with_image(image, threshold=0.6, keep_aspect_ratio=True, relative_coord=False, top_k=10)
        for result in results:
            name = result.label_id
            x, y, w, h = result.bounding_box.flatten().tolist()
            x = int(x * frame.shape[1])
            y = int(y * frame.shape[0])
            w = int(w * frame.shape[1])
            h = int(h * frame.shape[0])
            try:
                detected.append((class_map[name], x, y, w, h))
            except KeyError:
                pass
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
