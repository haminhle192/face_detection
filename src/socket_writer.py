__author__ = 'vietbq'

import struct
import time
import socket
import threading
import io
from PIL import Image
import numpy as np

class SocketWriter(threading.Thread):
    def __init__(self, connection_lock, detector):
        super(SocketWriter, self).__init__()
        self.event = threading.Event()
        self.detector = detector
        self.stream = io.BytesIO()
        self.terminated = False
        self.working = False
        self.start()

    def run(self):
        print('Writer is running')
        while not self.terminated:
            if self.event.wait(1):
                try:
                    self.working = True
                    with Image.open(self.stream).convert('RGB') as image:
                        open_cv_image = np.array(image)
                        open_cv_image = open_cv_image[:, :, ::-1].copy()
                        faces = self.detector.find_faces(open_cv_image)
                        if len(faces) > 0:
                            print(len(faces))
                            print('Save image here')

                except Exception as e:
                    print(e)
                finally:
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    self.working = False
                    print('Finish frame')
        print('Writer bye bye')
        try:
            self.stream.seek(0)
            self.stream.close()
        except Exception as e:
            print(e)