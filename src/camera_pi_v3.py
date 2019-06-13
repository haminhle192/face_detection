import io
import socket
import struct
import time
import threading
import picamera
import numpy as np
from PIL import Image
import detection as detection
import json

client_socket = socket.socket()
client_socket.connect(('192.168.1.183', 8989))
connection = client_socket.makefile('wb')

try:
    connection_lock = threading.Lock()
    reader_lock = threading.Lock()
    pool = []
    pool_lock = threading.Lock()


    class StreamerReader(threading.Thread):
        def __init__(self):
            self.event = threading.Event()
            self.terminated = False
            self.start()

        def run(self):
            while not self.terminated:
                try:
                    with reader_lock:
                        data_length = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
                        if data_length == 0:
                            continue
                        data = io.BytesIO()
                        data.write(connection.read(data_length))
                        decoded_data = data.decode('UTF-8')
                        data.seek(0)
                        j_data = json.loads(decoded_data)
                        print(j_data)
                finally:
                    self.event.clear()


    class ImageStreamer(threading.Thread):
        def __init__(self, detection):
            super(ImageStreamer, self).__init__()
            print("Starting Image Streamer")
            self.detection = detection
            self.stream = io.BytesIO()
            self.stream_face = io.BytesIO()
            self.event = threading.Event()
            self.terminated = False
            self.start()

        def run(self):
            # This method runs in a background thread
            while not self.terminated:
                if self.event.wait(1):
                    try:
                        with connection_lock:
                            image = Image.open(self.stream).convert('RGB')
                            open_cv_image = np.array(image)
                            open_cv_image = open_cv_image[:, :, ::-1].copy()
                            faces = self.detection.find_faces(open_cv_image)
                            print('Face detected %d' % len(faces))
                            if len(faces) > 0:
                                data = faces[0].data_image[1]
                                data = np.reshape(data, data.shape[0])
                                np.save(self.stream_face, data)
                                size = self.stream_face.tell()
                                print('Image len %d' % size)
                                connection.write(struct.pack('<L', size))
                                connection.write(self.stream_face.read(size))
                                self.stream_face.seek(0)
                            self.stream.seek(0)
                            self.stream.truncate()
                    finally:
                        self.stream.seek(0)
                        self.stream.truncate()
                        self.event.clear()
                        with pool_lock:
                            pool.append(self)

    count = 0
    start = time.time()
    finish = time.time()

    def streams():
        global count, finish
        while finish - start < 60:
            with pool_lock:
                if len(pool) == 0:
                    continue
                streamer = pool.pop()
            yield streamer.stream
            streamer.event.set()
            count += 1
            finish = time.time()

    detection = detection.Detection()
    with picamera.PiCamera() as camera:
        pool = [ImageStreamer(detection) for i in range(2)]
        camera.resolution = (640, 480)
        time.sleep(2)
        camera.capture_sequence(streams(), 'jpeg', use_video_port=True)
    # Shut down the streamers in an orderly fashion
    while pool:
        with pool_lock:
            streamer = pool.pop()
        streamer.terminated = True
        streamer.join()

    # Write the terminating 0-length: to the connection to let the server
    # know we're done
    with connection_lock:
        connection.write(struct.pack('<L', 0))

finally:
    connection.close()
    client_socket.close()

print('Sent %d images in %.2f seconds at %.2ffps' % (
    count, finish - start, count / (finish - start)))
