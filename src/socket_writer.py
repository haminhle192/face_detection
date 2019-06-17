__author__ = 'vietbq'

import struct
import time
import socket
import threading
import io
from PIL import Image
import numpy as np


class SocketWriter(threading.Thread):
    def __init__(self, connection_lock, connection, detector):
        super(SocketWriter, self).__init__()
        self.connection = connection
        self.event = threading.Event()
        self._lock = connection_lock
        self.detector = detector
        # self.stream = io.BytesIO()
        self.stream = np.empty((640, 480, 3), dtype=np.uint8)
        self.terminated = False
        self.working = False
        self.start()

    def run(self):
        print('Start writer')
        while not self.terminated:
            if self.event.wait(1):
                try:
                    with self._lock:
                        self.working = True
                        print('Preparing for sending frame')
                        # image = Image.open(self.stream).convert('RGB')
                        # open_cv_image = np.array(image)
                        # open_cv_image = open_cv_image[:, :, ::-1].copy()
                        faces = self.detector.find_faces(self.stream)
                        print('Number of face %d' % len(faces))
                        if len(faces) > 0:
                            size = faces[0].data_image.tell()
                            # self.connection.write(struct.pack('<L', size))
                            self.connection.sendall(struct.pack('L', size))
                            faces[0].data_image.seek(0)
                            # self.connection.flush()
                            # self.connection.write(faces[0].data_image.read(size))
                            self.connection.sendall(faces[0].data_image.read(size))
                            # self.connection.flush()
                            print('Did send %d' % size)
                except IOError as e:
                    print(e)
                    # print('Writer disconnected')
                    # self.event.clear()
                    # self.terminated = True
                finally:
                    print('Finish frame')
                    self.stream = None
                    # self.stream.seek(0)
                    # self.stream.truncate()
                    self.event.clear()
                    self.working = False
        print('Writer bye bye')