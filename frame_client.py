# Client to recv from frame-server

import cv2
import socket
import pickle
import numpy as np

PORT = 5829
SERVER = "tins-pi.local"
# SERVER = "127.0.0.1"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

print(f"Connected to {SERVER}:{PORT}")

def recv():
    data = client.recv(4)
    if data == b"RCIM":
        data = client.recv(4)
        data_len = int.from_bytes(data, byteorder='big')
        data = b""
        while len(data) < data_len:
            data += client.recv(data_len - len(data))
        if not data:
            return None
        frame = pickle.loads(data)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        return frame
    return None

if __name__ == "__main__":
    while True:
        frame = recv()
        if frame is None:
            break
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
