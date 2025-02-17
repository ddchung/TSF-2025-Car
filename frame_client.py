# Client to recv from frame-server

import cv2
import socket
import pickle
import numpy as np
import threading
import time
import os

PORT = 5824

if os.environ.get("RC_CAR_PI_ADDR") is None:
    SERVER = "localhost"
    def _server_thread():
        import frame_server
    threading.Thread(target=_server_thread, daemon=True).start()
else:
    SERVER = os.environ.get("RC_CAR_PI_ADDR")

# Wrapper class to automatically lock/unlock
class SyncedVariable:
    def __init__(self, value):
        self._value = value
        self._lock = threading.Lock()

    def get(self):
        with self._lock:
            return self._value

    def set(self, value):
        with self._lock:
            self._value = value

_frame = SyncedVariable(None)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

print(f"Connected to {SERVER}:{PORT}")

def _recv():
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

def recv():
    global _frame
    return _frame.get()

def recv_thread():
    global _frame
    while True:
        _frame.set(_recv())

threading.Thread(target=recv_thread, daemon=True).start()

time.sleep(2) # allow time for the first frame to be received

if __name__ == "__main__":
    while True:
        frame = recv()
        if frame is None:
            break
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
