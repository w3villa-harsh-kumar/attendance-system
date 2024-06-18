import cv2
import threading

class VideoStream:
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)
        self.ret, self.frame = self.cap.read()
        self.running = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()

    def update(self):
        while self.running:
            if self.cap.isOpened():
                self.ret, self.frame = self.cap.read()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()

def process_frame(frame):
    # Your face recognition code here
    pass

stream = VideoStream('rtsp://admin:admin_123@192.168.29.103:554/Streaming/channels/601')

while True:
    ret, frame = stream.read()
    if not ret:
        print("Failed to grab frame")
        break

    process_frame(frame)

    cv2.imshow('RTSP Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

stream.stop()
cv2.destroyAllWindows()
