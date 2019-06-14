__author__ = 'vietbq'

import struct
import time
import socket
import threading
import io
from PIL import Image
import detection as detection
import numpy as np


class SocketReader(threading.Thread):

    def __init__(self, connection, detection):
        super(SocketReader, self).__init__()
        self.connection = connection
        self.event = threading.Event()
        self._lock = threading.Lock()
        self.detection = detection
        self.stream = io.BytesIO()
        self.terminated = False

    def run(self):
        while not self.terminated:
            try:
                with self._lock:
                    image = Image.open(self.stream).convert('RGB')
                    open_cv_image = np.array(image)
                    open_cv_image = open_cv_image[:, :, ::-1].copy()
                    faces = self.detection.find_faces(open_cv_image)
                    if len(faces) > 0:
                        size = faces[0].data_image.tell()
                        self.connection.write(struct.pack('<L', size))
                        faces[0].data_image.seek(0)
                        self.connection.flush()
                        self.connection.write(faces[0].data_image.read(size))
                        self.connection.flush()
                        faces[0].data_image.truncate()
                        print('Did send %d' % size)

                    self.stream.seek(0)
                    self.stream.truncate()
            finally:
                self.stream.seek(0)
                self.stream.truncate()
                self.event.clear()