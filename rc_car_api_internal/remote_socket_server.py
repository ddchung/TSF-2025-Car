# RC Car API remote control

import socket
import pins

PORT = 21834

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', PORT))
server.listen(5)

print(f"Server started on port {PORT}")

while True:
    conn, addr = server.accept()

    print(f"Connection from {addr}")

    try:
        while True:
            # {speed},{steering},{light1},{light2},{light3};
            data = conn.recv(20).decode()
            if not data:
                break
            if data[9] != ";":
                print("Invalid data", data)
                continue
            data = data[:9]
            split = data.split(",")
            speed = int(split[0])
            steering = int(split[1])
            light1 = int(split[2])
            light2 = int(split[3])
            light3 = int(split[4])

            pins.setSpeed(speed)
            pins.setSteeringAngle(steering)
            pins.setHeadlights(light1)
            pins.setTaillights(light2)
            pins.setSun(light3)
    finally:
        conn.close()
