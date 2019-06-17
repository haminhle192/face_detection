__author__ = 'vietbq'

import struct
import time
import socket
import threading
import io
from PIL import Image
import numpy as np


class SocketWriter(threading.Thread):
    def __init__(self, connection_lock, writer, detector):
        super(SocketWriter, self).__init__()
        self.writer = writer
        self.event = threading.Event()
        self._lock = connection_lock
        self.detector = detector
        self.stream = io.BytesIO()
        self.terminated = False
        self.disconnect = False
        self.working = False
        self.start()

    def run(self):
        while not self.terminated:
            if self.event.wait(1):
                try:
                    with self._lock:
                        self.working = True
                        image = Image.open(self.stream).convert('RGB')
                        open_cv_image = np.array(image)
                        open_cv_image = open_cv_image[:, :, ::-1].copy()
                        faces = self.detector.find_faces(open_cv_image)
                        if len(faces) > 0:
                            size = faces[0].data_image.tell()
                            self.writer.write(struct.pack('<L', size))
                            faces[0].data_image.seek(0)
                            self.writer.flush()
                            self.writer.write(faces[0].data_image.read(size))
                            self.writer.flush()
                            print('Did send %d' % size)
                except Exception as e:
                    print(e)
                    print('Writer disconnected')
                    self.event.clear()
                    self.terminated = True
                finally:
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    self.working = False
        print('Writer bye bye')