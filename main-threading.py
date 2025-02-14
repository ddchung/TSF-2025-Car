import cv2
import time
from ultralytics import YOLO
import rc_car_api
import lane_follower
import numpy as np 
import threading

def light_transition(light, start_light_val, end_light_val): # extra idea that can be implemented later
    """Gets a gradual transition between 2 different light values, for 3 seconds """
    rc_car_api.set_light(light, start_light_val)
    common_dif = (start_light_val-end_light_val)/12
    cur_light = start_light_val
    while cur_light - common_dif > 0:
        cur_light -= common_dif
        rc_car_api.set_light(light, cur_light)
        time.sleep(0.25)
    rc_car_api.set_light(light, end_light_val)
    pass 

def logs(detected, percent, coordinate): # all the values should be changed later
    global prev_stop_area_ratio
    global speed
    global lane_lines
    global stopped

    changed = False
    if percent > 4 and coordinate[0]: # the objects should be checked when they are close enough
        if coordinate[0] >= cap_width // 2: # only checking if the signs are on the right side of the road (// => floor division) (it can be combined w. first if statement by "and")
            match detected.split()[0].lower(): # getting the first word of the detected result
                case "stop":
                    if percent < prev_stop_area_ratio and not stopped: # stopping when the new detected stop sign is smaller than the previous frame's stop sign
                        rc_car_api.stop_move()
                        rc_car_api.set_light(0, 100) # if making lights transition, do threading.Thread(target=light_transition, args=(0, 0, 100)).start() 
                        time.sleep(3) # don't want to do the join()
                        print("STOPPING AT STOP SIGN")
                        rc_car_api.start_move_forward(speed)
                        rc_car_api.set_light(0, 0) # if making lights transition, do threading.Thread(target=light_transition, args=(0, 100, 0)).start()
                        stopped = True
                    else: 
                        print("GOING PAST STOP SIGN")
                        stopped = False # if the detected stop sign is bigger than the prev then it shows that it's the same stop sign (I think)
                    prev_stop_area_ratio = percent
                case "red": 
                    if percent > 8:
                        print("GOING PAST RED LIGHT") # Red light detected but too big; not making the car stop at the middle of the intersection
                        stopped = False # maybe unnecessary but still try
                    else:
                        rc_car_api.set_light(100,1) # light transition may not work; though not necessary
                        rc_car_api.stop_move()
                        stopped = True
                        print("STOPPING AT RED LIGHT")
                case "green":
                    rc_car_api.set_light(0, 1) 
                    stopped = False
                    print("GOING PAST GREEN LIGHT")
                case "speed":
                    speed = int(int(detected.split()[-1])*100/120) 
                    print(f"CHANGING SPEED TO {detected.split()[-1]}")
            changed = True
    return changed 

def box_percent(box_width, box_height, width, height):
    area = box_width * box_height
    percent = area/(height*width)*100 
    return percent

def draw_box(frame, data, color=(255,0,0), res=False, point=False):
    mask = np.zeros_like(frame, dtype=np.uint8)
    cv2.fillPoly(mask, [data], color=color)  # Blue color
    transparency_level = 0.5

    frame = cv2.addWeighted(frame, 1, mask, transparency_level, 0) # Blends the mask w. orig. img

    if point:
        if res == 1:
            cv2.circle(frame, point, 5, (0, 0, 255), -1)  # Red if inside
            print("The point is inside the quadrilateral")
        elif res == -1:
            cv2.circle(frame, point, 5, (255, 0, 0), -1)  # blue if outside
            print("The point is outside the quadrilateral")
        elif res == 0:
            cv2.circle(frame, point, 5, (0, 255, 0), -1)  # Green if on the edge
            print("The point is on the edge of the quadrilateral.")
        else:
            print("There has been no person detected.")
    return frame

def road_area(lines):
    try:
        pt1 = lines[0][0][0], lines[0][0][1]  # First point of the first line
        pt2 = lines[1][0][0], lines[1][0][1]  # Second point of the second line
        pt3 = lines[1][0][2], lines[1][0][3]  # First point of the second line
        pt4 = lines[0][0][2], lines[0][0][3]  # Second point of the first line
        
        quadrilateral = np.array([pt1, pt2, pt3, pt4], dtype=np.int32)
        print(f"ROAD: {quadrilateral}")
    except:
        return []
    return quadrilateral

def check_obj_on_rd(coordinate, data):
    """checks whether a point is inside, outside, or on the edge of a shape. 
    it can also optionally calculate the shortest distance between the point and the shape"""
    return cv2.pointPolygonTest(data, coordinate, measureDist=False)

def predict_person(frame):
    global person_results
    global person_model
    person_results = person_model.predict(frame, conf=0.2, classes=[0]) # chose a much lower value since lego people don't look that similar to people
    print(f"INSIDE THE PREDICT PERSON FUNCTION, RESULTS = {person_results}")

def predict_sign(frame):
    global conf
    global main_results
    global sign_model
    main_results = sign_model.predict(frame, conf=conf)

sign_model = YOLO(r".\traffic_sign_detector.pt") # I tested this on my computer; just change the path
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

person_results = None
main_results = None
cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

ret = True
while ret:
    front_distance = rc_car_api.read_sensor(0)

    if front_distance and front_distance < 10 and front_distance > 0: # change the distances. will it also register signs that come near the car?
        if front_distance > 5:
            rc_car_api.stop_move()
            print("STOPPING AT OBSTACLE")
        else:
            rc_car_api.start_move_backward(speed)
            print("MOVING BACKWARDS FROM AN OBSTACLE THAT IS TOO CLOSE")
    else:
        ret, frame = cap.read(0)
        t0 = time.time()

        person_thread = threading.Thread(target=predict_person, args=(frame,))
        main_thread = threading.Thread(target=predict_sign, args=(frame,))
        person_thread.start()
        main_thread.start()
        person_thread.join()
        main_thread.join()
        new_frame=frame # created a new frame to show not interfere with other 
        main_results_plotted_image = main_results[0].plot()
        person_plotted_image = person_results[0].plot()  # This returns an image with bounding boxes
        new_frame = cv2.addWeighted(main_results_plotted_image, 0.5, person_plotted_image, 0.5, 0)
        lane_lines = lane_follower.detect_lane(frame)
        new_frame = lane_follower.display_lines(new_frame, lane_lines)

        road = road_area(lane_lines)
        if len(road) > 0:
            new_frame = draw_box(new_frame, road)
            old_road = road # this is trying to remove any gaps where it hasn't detected a road
        else:
            road = old_road
            new_frame = draw_box(new_frame, old_road) # since it has not detected a person, it will not draw the coordinate
        
        person_on_road = False
        for result in person_results: 
            for box in result.boxes:
                x_center, y_center, box_width, box_height = box.xywh[0]
                coordinate = int(x_center), int(y_center)
                box_percent(box_width, box_height, cap_width, cap_height)
                res = check_obj_on_rd(coordinate, road)
                hw = box_width//2
                hh = box_height//2

                if res != -1:
                    print("STOPPING FOR PERSON ON ROAD")
                    rc_car_api.stop_move() 
                    person_on_road = True
                new_frame = draw_box(new_frame, np.array([(x_center-hw, y_center+hh), (x_center+hw, y_center+hh), (x_center+hw, y_center-hh), (x_center-hw, y_center-hh)], dtype=np.int32), color=(0,255,0), res=res, point=coordinate)
        if not person_on_road:
            for result in main_results:
                for box in result.boxes:
                    x_center, y_center, box_width, box_height = box.xywh[0]

                    coordinate = int(x_center), int(y_center)
                    detected = result.names[int(box.cls)]
                    percent  = box_percent(box_width, box_height, cap_width, cap_height)
                    print(f"DETECTED = {detected}, BOX PERCENT = {percent}")
                    
                    changed = logs(detected, percent, coordinate)
                    if changed:
                        print("DRAWING BOX!!!")
                        hw = box_width//2
                        hh = box_height//2
                        new_frame = draw_box(new_frame, np.array([(x_center-hw, y_center+hh), (x_center+hw, y_center+hh), (x_center+hw, y_center-hh), (x_center-hw, y_center-hh)], dtype=np.int32))
            if not stopped:
                rc_car_api.start_move_forward(speed)
                print("MOVING FORWARD!")
        
        new_frame = cv2.line(new_frame, (cap_width//2, 0), (cap_width//2, cap_height), (0, 0, 255), 1)
        cv2.imshow("Traffic sign detector", new_frame)
        t1 = time.time()
        print(t1-t0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    print(f"======================================STOPPING? (T/F): {stopped}")
