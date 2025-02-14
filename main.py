import cv2
import time
from ultralytics import YOLO
import adapter
import lane_follower
import numpy as np 

sign_model = YOLO(r".\traffic_sign_detector.pt") # this lowers accuracy for better performance
person_model = YOLO(r".\yolov10n.pt")  # Use a smaller model like yolov8n for speed
conf = 0.6
speed = 16 # the slowest speed limit
prev_stop_area_ratio = 100 # making it so it stops no matter what for the first stop sign detection
stopped = False # checking if old/same signs that I checked made me stop
old_road = np.array([(155, 480), (576, 480), (489, 192), (249, 192)], dtype=np.int32) # a default road; should change based on dimensions of camera. (can be removed)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Unable to open the input file")
    exit()


cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
ret = True

def logs(detected, percent, coordinate, prev_stop_area_ratio, speed, stopped): # all the values should be changed later
    if percent > 4 and coordinate[0]: # the objects should be checked when they are close enough
        if coordinate[0] >= cap_width // 2: # only checking if the signs are on the right side of the road (// => floor division) (it can be combined w. first if statement by "and")
            match detected.split()[0].lower(): # getting the first word of the detected result
                case "stop":
                    if percent < prev_stop_area_ratio and not stopped: # stopping when the new detected stop sign is smaller than the previous frame's stop sign
                        adapter.stop_move()
                        adapter.set_light(0, 100) # if making lights transition, do threading.Thread(target=light_transition, args=(0, 0, 100)).start() 
                        print("STOPPING AT STOP SIGN")
                        time.sleep(3) # don't want to do the join()
                        adapter.start_move_forward(speed)
                        adapter.set_light(0, 0) # if making lights transition, do threading.Thread(target=light_transition, args=(0, 100, 0)).start()
                        stopped = True
                    else: 
                        print("GOING PAST STOP SIGN")
                        stopped = False # if the detected stop sign is bigger than the prev then it shows that it's the same stop sign (I think)
                    prev_stop_area_ratio = percent
                case "red": 
                    if percent > 10:
                        print("GOING PAST RED LIGHT") # Red light detected but too big; not making the car stop at the middle of the intersection
                        stopped = False # maybe unnecessary but still try
                    else:
                        adapter.set_light(100,1) # light transition may not work; though not necessary
                        adapter.stop_move()
                        stopped = True
                        print("STOPPING AT RED LIGHT")
                case "green":
                    adapter.set_light(0, 1) 
                    stopped = False
                    print("GOING PAST GREEN LIGHT")
                case "speed":
                    speed = int(int(detected.split()[-1])*100/120) 
                    print(f"CHANGING SPEED TO {detected.split()[-1]}")
    return prev_stop_area_ratio, speed, stopped

def box_percent(box_width, box_height, width, height):
    area = box_width * box_height
    percent = area/(height*width)*100 
    return percent

def road_area(lines):
    try:
        pt1 = lines[0][0][0], lines[0][0][1]  # First point of the first line
        pt2 = lines[1][0][0], lines[1][0][1]  # Second point of the second line
        pt3 = lines[1][0][2], lines[1][0][3]  # First point of the second line
        pt4 = lines[0][0][2], lines[0][0][3]  # Second point of the first line
        
        quadrilateral = np.array([pt1, pt2, pt3, pt4], dtype=np.int32)
        print(f"ROAD: {quadrilateral}")
    except Exception as E:
        print(f"IN 'ROAD AREA FUNCTION', GOT ERROR OF {E}")
        return []
    return quadrilateral

def check_obj_on_rd(coordinate, data):
    """checks whether a point is inside, outside, or on the edge of a shape. 
    it can also optionally calculate the shortest distance between the point and the shape"""
    return cv2.pointPolygonTest(data, coordinate, measureDist=False)

if __name__ == "__main__":
    while ret:
        front_distance = adapter.read_sensor(0)
        if front_distance and front_distance < 10 and front_distance > 0: # change the distances. will it also register signs that come near the car?
            if front_distance > 5:
                adapter.stop_move()
                print("STOPPING AT OBSTACLE")
            else:
                adapter.start_move_backward(speed)
                print("MOVING BACKWARDS FROM AN OBSTACLE THAT IS TOO CLOSE")
        else:
            ret, frame = cap.read(0)

            person_results = person_model.predict(frame, conf=0.2, classes=[0]) # decided to use a much lower one since the stakes are higher
            person_on_road = False
            lane_lines = lane_follower.detect_lane(frame)
            road = road_area(lane_lines)

            for result in person_results: 
                for box in result.boxes:
                    x_center, y_center, box_width, box_height = box.xywh[0]
                    coordinate = int(x_center), int(y_center)
                    percent = box_percent(box_width, box_height, cap_width, cap_height)
                    if len(road) > 0:
                        old_road = road # this is trying to remove any gaps where it hasn't detected a road
                    else:
                        road = old_road
                    res = check_obj_on_rd(coordinate, road)
                    if res != -1 and percent > 10: #change val later
                        print("STOPPING FOR PERSON ON ROAD")
                        adapter.stop_move() 
                        person_on_road = True
            if not person_on_road:
                main_results = sign_model.predict(frame, conf=conf)
                for result in main_results:
                    if not stopped:
                        for box in result.boxes:
                            if not stopped:
                                x_center, y_center, box_width, box_height = box.xywh[0]
                                coordinate = int(x_center), int(y_center)
                                detected = result.names[int(box.cls)]
                                percent  = box_percent(box_width, box_height, cap_width, cap_height)
                                print(f"DETECTED = {detected}, BOX PERCENT = {percent}")
                                
                                prev_stop_area_ratio, speed, stopped = logs(detected, percent, coordinate, prev_stop_area_ratio, speed, stopped)
                if not stopped:
                    adapter.start_move_forward(speed)
                    print("MOVING FORWARD!")
            
            print(f"======================================STOPPING? (T/F): {stopped}")
            cv2.imshow("Traffic sign detector", frame) # comment out the rest of the lines when using it
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break