from rc_car_api_internal import pins
import os

if os.environ.get("RC_CAR_PI_ADDR") is not None:
    from rc_car_api_internal import remote_socket_client
    pins = remote_socket_client


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
        pins.setSun(brightness)
    else:
        print("\nWARN: Invalid light", light, "\n")

def read_sensor(sensor):
    """
    sensors:
    - 0 front
    - 1 back
    """
    return 15 # cm
