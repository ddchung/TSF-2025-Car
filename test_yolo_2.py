# ultralytics yolo test

from ultralytics import YOLO
import cv2
import platform
# import frame_client
# import white_balance
# import correct_fov

device = None
if "darwin" in platform.system().lower():
    device = "mps:0" # Use Apple's Metal Performance Shaders
elif "linux" in platform.system().lower():
    device = "auto"

model = YOLO("best (8).pt")
cap = cv2.VideoCapture(0)

while True:
    ret, img = cap.read()
    if not ret:
        break
    # frame = frame_client.recv()
    # if frame is None:
    #     break
    # frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    # frame = correct_fov.correct(frame)
    # img = white_balance.automatic_white_balance(frame)
    results = model.predict(img, device=device)

    for r in results:
        for box in r.boxes:
            x, y, w, h = box.xywh[0]
            x = int(x)
            y = int(y)
            w = int(w)
            h = int(h)
            x -= w // 2
            y -= h // 2
            name = r.names[int(box.cls)].lower()
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 255), 3)
            cv2.putText(img, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.imshow("img", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
