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

    def __init__(self, connection):
        super(SocketReader, self).__init__()
        self.connection = connection
        self.event = threading.Event()
        self._lock = threading.Lock()
        self.detection = detection
        self.stream = io.BytesIO()
        self.terminated = False
        self.start()

    def run(self):
        while not self.terminated:
            try:
                with self._lock:
                    data_len = struct.unpack('<L', self.connection.read(struct.calcsize('<L')))[0]
                    if not data_len:
                        continue
                    self.stream.write(self.connection.read(data_len))
                    text_obj = self.stream.decode('UTF-8')
                    print(text_obj)
                    self.stream.seek(0)
                    self.stream.truncate()
            finally:
                self.stream.seek(0)
                self.stream.truncate()
                self.event.clear()
        print('Reader bye bye')