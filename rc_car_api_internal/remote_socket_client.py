
import socket
import os

PORT = 21834
HOST = os.environ.get("RC_CAR_PI_ADDR")

if HOST is None:
    print("RC_CAR_PI_ADDR not set")
    exit(1)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

print(f"Connected to {HOST}:{PORT}")

def send(speed, steering, light1, light2, light3):
    global client
    # temporary workaround
    if speed <= -100:
        speed = -99
    if speed > 100:
        speed = 100
    if steering <= -100:
        steering = -99
    if steering > 100:
        steering = 100
    if light1 < 0:
        light1 = 0
    if light1 > 100:
        light1 = 100
    if light2 < 0:
        light2 = 0
    if light2 > 100:
        light2 = 100
    if light3 < 0:
        light3 = 0
    if light3 > 100:
        light3 = 100
    data = f"{speed:03d},{steering:03d},{light1:03d},{light2:03d},{light3:03d};"
    client.sendall(data.encode())

speed = 0
steering = 0
light1 = 0
light2 = 0
light3 = 0


def setHeadlights(value):
    global light1
    light1 = value
    send(speed, steering, light1, light2, light3)

def setTaillights(value):
    global light2
    light2 = value
    send(speed, steering, light1, light2, light3)

def setSun(value):
    global light3
    light3 = value
    send(speed, steering, light1, light2, light3)

def setSpeed(value):
    global speed
    speed = value
    send(speed, steering, light1, light2, light3)

def setSteeringAngle(value):
    global steering
    steering = value
    send(speed, steering, light1, light2, light3)

