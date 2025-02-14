from rc_car_api_internal import pins

def start_move_forward(speed):
    """speed from 0-100"""
    pins.setSpeed(speed)

def start_move_backward(speed):
    """speed from 0-100"""
    pins.setSpeed(-speed)

def stop_move():
    pins.setSpeed(0)

def set_steering_angle(angle):
    """angle from -90(left) to 90(right), 0 in middle"""
    pins.setSteeringAngle(angle)

def set_light(light, brightness):
    """
    brightness: 0-100
    lights:
    - 0 headlight
    - 1 taillight
    - 3 sun
    """
    if light == 0:
        pins.setHeadlights(brightness)
    elif light == 1:
        pins.setTaillights(brightness)
    elif light == 3:
        print("\nWARN: Sun not implemented yet\n")

def read_sensor(sensor):
    """
    sensors:
    - 0 front
    - 1 back
    - 2 left
    - 3 right
    """
    print("\nWARN: Sensors not implemented yet\n")
    return 15 # cm
