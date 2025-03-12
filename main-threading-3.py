# better and revised main code

import cv2
import time
import traffic_sign_detection
import lane_nav_detector
import multiprocessing


# dispatch inferences to seperate processes

def steering_process(conn):
    while True:
        # recieve frame
        frame = conn.recv()
        if frame is None:
            time.sleep(0.1)
            continue
        # predict steering
        steering = lane_nav_detector.predict_steering(frame)
        # send steering
        conn.send([steering])
    conn.close()

def object_process(conn):
    while True:
        # recieve frame
        frame = conn.recv()
        if frame is None:
            time.sleep(0.1)
            continue
        # predict objects
        objects = traffic_sign_detection.detect_objects(frame)
        # send objects
        conn.send(objects)
    conn.close()

def steering_loop():
    global state
    global state_lock

    # start processes
    steering_conn, steering_child_conn = multiprocessing.Pipe()
    steering_proc = multiprocessing.Process(target=steering_process, args=(steering_child_conn,), daemon=True)
    steering_proc.start()

    while True:
        with state_lock:
            frame = state[0].frame
        steering_conn.send(frame)
        steering = steering_conn.recv()[0]
        with state_lock:
            state[0].steering = steering
        time.sleep(0.01)

def object_loop():
    global state
    global state_lock

    # start processes
    object_conn, object_child_conn = multiprocessing.Pipe()
    object_proc = multiprocessing.Process(target=object_process, args=(object_child_conn,), daemon=True)
    object_proc.start()

    while True:
        with state_lock:
            frame = state[0].frame
        object_conn.send(frame)
        objects = object_conn.recv()
        with state_lock:
            state[0].objects = objects
        time.sleep(0.01)


if __name__ == "__main__":
    import rc_car_api
    import frame_client
    import numpy as np 
    import threading
    from dataclasses import dataclass
    import white_balance
    import correct_fov

    # state structure
    @dataclass
    class State:
        frame: np.ndarray
        distance_sensors: list[int]
        objects: list[tuple[str, int, int, int, int]]
        steering: int

        speed: int
        speed_limit: int
        lights: list[int]


    # global state
    state = [
        State(
            frame=np.zeros((480, 640, 3), dtype=np.uint8),
            distance_sensors=[0, 0, 0, 0],
            objects=[],
            steering=0,
            speed=1,
            speed_limit=40,
            lights=[0, 0, 0]
        )
    ]

    state_lock = threading.Lock()

    def update_car():
        # get the current state
        with state_lock:
            current_state = state[0]
        
        # update the car
        rc_car_api.set_steering_angle(current_state.steering)
        rc_car_api.start_move_forward(current_state.speed)
        rc_car_api.set_light(0, current_state.lights[0])
        rc_car_api.set_light(1, current_state.lights[1])
        rc_car_api.set_light(3, current_state.lights[2])


    def do_actions(actions):
        for action in actions:
            try:
                action()
            except StopIteration:
                break


    # actions

    def example_action():
        THRESHOLD = 0.1 # 10%

        global state
        global state_lock

        # get objects
        with state_lock:
            objects = state[0].objects
            cam_height, cam_width = state[0].frame.shape[:2]
        
        # search for some object bigger than some amount
        found = False
        for obj in objects:
            name, x, y, w, h = obj
            if w * h > THRESHOLD * cam_height * cam_width:
                print(f'Found object {name} at {x}, {y}')
                found = True
                break
        if not found:
            print('No object found')
            return
        
        # do something
        with state_lock:
            state[0].speed = 0
            state[0].steering = 0
            state[0].lights = [0, 0, 0]
        
        # can either return or raise StopIteration
        # return continues with other actions
        # raise StopIteration stops doing other actions
        raise StopIteration

    def check_speed_limit():
        # checks for any `speed limit %d`
        THRESHOLD = 0.001 # 0.1%

        global state
        global state_lock

        # get objects
        with state_lock:
            objects = state[0].objects
            cam_height, cam_width = state[0].frame.shape[:2]
        
        # search for speed limit bigger than some amount
        limit = None
        for obj in objects:
            name, x, y, w, h = obj
            if (name.startswith('speed limit') 
                    and w * h > THRESHOLD * cam_height * cam_width):
                try:
                    limit = int(name.split()[-1])
                except ValueError:
                    print(f"WARNING: Invalid speed limit {name}")
                    return
                break
        if limit is None:
            return
        
        # set speed limit
        with state_lock:
            state[0].speed_limit = limit

    def correct_speed():
        global state
        global state_lock

        with state_lock:
            cur_speed = state[0].speed
            speed_limit = state[0].speed_limit
            if speed_limit < 30:
                speed_limit = 30
            if cur_speed > 0:
                state[0].speed = speed_limit
            elif cur_speed < 0:
                state[0].speed = -speed_limit
            # don't do anything if speed is 0

    def check_distance_sensors():
        STOP_THRESHOLD = 5 # 5 cm
        BACK_THRESHOLD = 3 # 10 cm

        global state
        global state_lock

        with state_lock:
            front, back = state[0].distance_sensors[:2]
        
        if front < STOP_THRESHOLD:
            with state_lock:
                cur_speed = state[0].speed
                if cur_speed > 0:
                    print("Front obstacle detected, stopping")
                    state[0].speed = 0
                if front < BACK_THRESHOLD:
                    print("Front obstacle close, going back")
                    state[0].speed = -1
            raise StopIteration
        elif back < STOP_THRESHOLD:
            with state_lock:
                cur_speed = state[0].speed
                if cur_speed < 0:
                    print("Back obstacle detected, stopping")
                    state[0].speed = 0
                if back < BACK_THRESHOLD:
                    print("Back obstacle close, going forward")
                    state[0].speed = 1
            raise StopIteration

    def check_red_light():
        THRESHOLD = 0.001 # 0.1%

        global state
        global state_lock

        # get objects
        with state_lock:
            objects = state[0].objects
            cam_height, cam_width = state[0].frame.shape[:2]
        
        # search for red light bigger than some amount
        found = False
        for obj in objects:
            name, x, y, w, h = obj
            if (name == 'red light' 
                    and w * h > THRESHOLD * cam_height * cam_width):
                found = True
                break
        if not found:
            return
        
        # do something
        with state_lock:
            print("Red light detected, stopping")
            state[0].speed = 0
        raise StopIteration

    def check_person():
        THRESHOLD = 0.002 # 0.2%
        MAX_DISTANCE = 0.5 # max 20% radius, otherwise ignore

        global state
        global state_lock

        # get objects
        with state_lock:
            objects = state[0].objects
            cam_height, cam_width = state[0].frame.shape[:2]
        
        # search for person bigger than some amount
        found = False
        for obj in objects:
            name, x, y, w, h = obj
            # for person, additionally check if it's within the bottom-center of the frame
            dx = x + w/2 - cam_width/2
            dy = y + h - cam_height
            d = np.sqrt(dx**2 + dy**2)
            if (name == 'person' 
                    and w * h > THRESHOLD * cam_height * cam_width
                    and d < MAX_DISTANCE * cam_height):
                found = True
                break
        if not found:
            return
        
        # do something
        with state_lock:
            print("Person detected, stopping")
            state[0].speed = 0
        raise StopIteration    

    last_stop_sign_stop = -1
    last_stop_sign_go = 0
    def check_stop_sign():
        THRESHOLD = 0.002 # 0.2%
        STOP_TIME = 3 # 3 seconds
        GET_OUT_TIME = 5 # 5 seconds

        global state
        global state_lock
        global last_stop_sign_stop
        global last_stop_sign_go

        # get objects
        with state_lock:
            objects = state[0].objects
            cam_height, cam_width = state[0].frame.shape[:2]
        
        # search for stop sign bigger than some amount
        found = False
        for obj in objects:
            name, x, y, w, h = obj
            if (name == 'stop' 
                    and w * h > THRESHOLD * cam_height * cam_width):
                found = True
                break
        
        now = time.time()
        if not found:
            if now - last_stop_sign_stop < STOP_TIME:
                with state_lock:
                    state[0].speed = 0
                raise StopIteration
            return
        # stop for 3 seconds, then go
        if last_stop_sign_stop < last_stop_sign_go:
            if now - last_stop_sign_go > GET_OUT_TIME:
                # give car GET_OUT_TIME seconds to get out
                print("Detected stop sign, waiting")
                last_stop_sign_stop = now
                with state_lock:
                    state[0].speed = 0
                raise StopIteration
        else:
            # already stopped
            if now - last_stop_sign_stop > STOP_TIME:
                # stopped for STOP_TIME seconds
                print("Done stopping at stop sign")
                last_stop_sign_go = now
                with state_lock:
                    state[0].speed = 1 # let correct_speed() handle the speed
                return
            else:
                # still stopping
                with state_lock:
                    state[0].speed = 0
                raise StopIteration

    def check_green_light():
        THRESHOLD = 0.001 # 0.1%

        global state
        global state_lock

        # get objects
        with state_lock:
            objects = state[0].objects
            cam_height, cam_width = state[0].frame.shape[:2]
        
        # search for green light bigger than some amount
        found = False
        for obj in objects:
            name, x, y, w, h = obj
            if (name == 'green light' 
                    and w * h > THRESHOLD * cam_height * cam_width):
                found = True
                break
        if not found:
            return
        
        # do something
        with state_lock:
            print("Green light detected, going")
            state[0].speed = 1

    def go():
        global state
        global state_lock

        with state_lock:
            if (state[0].speed == 0):
                state[0].speed = 1

    # note: top ones have higher priority
    actions = [
        check_speed_limit,
        correct_speed,
        check_distance_sensors,
        check_red_light,
        check_person,
        check_stop_sign,
        check_green_light,
        go
    ]

    # Input loops

    # frame
    def frame_loop():
        global state
        global state_lock

        # cap = cv2.VideoCapture(0)
        while True:
            frame = frame_client.recv()
            # ok, frame = cap.read()
            if frame is None:
                print("WARN: No frame")
                continue
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            frame = white_balance.automatic_white_balance(frame)
            frame = correct_fov.correct(frame)
            # if not ok:
            #     print("WARN: no frame")
            #     continue
            with state_lock:
                state[0].frame = frame
            time.sleep(0.01)

    # distance sensors
    def distance_sensor_loop():
        global state
        global state_lock

        while True:
            sensors = [rc_car_api.read_sensor(i) for i in range(4)]
            with state_lock:
                state[0].distance_sensors = sensors
            time.sleep(0.01)

    def car_update_loop():
        while True:
            update_car()
            time.sleep(0.01)

    def main_loop():
        global state
        global state_lock

        # start threads
        threading.Thread(target=frame_loop, daemon=True).start()
        threading.Thread(target=distance_sensor_loop, daemon=True).start()
        threading.Thread(target=steering_loop, daemon=True).start()
        threading.Thread(target=object_loop, daemon=True).start()
        threading.Thread(target=car_update_loop, daemon=True).start()

        print("Started main loop")

        while True:
            with state_lock:
                current_state = state[0]
            do_actions(actions)
            annotated = current_state.frame.copy()
            objects = current_state.objects

            annotated_area = annotated.shape[0] * annotated.shape[1]

            for obj in objects:
                name, x, y, w, h = obj
                size = w * h / annotated_area * 100
                size = round(size, 2)
                name = f"{name} {size}%"
                cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(annotated, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('frame', annotated)

            if cv2.waitKey(100) == ord('q'):
                break
    
    main_loop()

