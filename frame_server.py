# Camera server that sends realtime frames through a socket connection

import cv2
import socket
import pickle

PORT = 5829

cap = cv2.VideoCapture(0)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', PORT))
server.listen(5)

print(f"Server started on port {PORT}")

while True:
    conn, addr = server.accept()

    print(f"Connection from {addr}")

    while True:
        ret, frame = cap.read()
        data = cv2.imencode('.jpg', frame)[1]
        data = pickle.dumps(data)
        try:
            conn.sendall(b"RCIM")
            conn.sendall(len(data).to_bytes(4, byteorder='big'))
            conn.sendall(data)
        except:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    conn.close()

