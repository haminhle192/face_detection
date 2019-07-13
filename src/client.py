__author__ = 'vietbq'

import socket
import picamera
import time
import threading
import detection as detection
import json
import io
import numpy as np
from socket_writer import SocketWriter

class Client:

    def __init__(self):
        self.pool = []
        self.pool_lock = threading.Lock()
        self.connection_lock = threading.Lock()
        self.terminated = False
        self.ignore_stream = io.BytesIO()
        self.writer_stream = None
        self.reader = None
        self.count = 0
        self.start = 0
        self.finish = 0

    def start_streaming(self):
        self.start = time.time()
        self.finish = time.time()
        with picamera.PiCamera() as camera:
            try:
                print('Starting load model')
                detector = detection.Detection()
                detector.find_faces(np.empty((48, 48, 3), dtype=np.uint8))
                print('Did load model')
                self.pool = [(SocketWriter(self.connection_lock, self.writer_stream, detector)) for i in range(1)]
                camera.resolution = (640, 480)
                camera.framerate = 5
                time.sleep(2)
                camera.capture_sequence(self.writers(), 'jpeg', use_video_port=True)
            except Exception as e:
                print(e)
            finally:
                print('Stop camera')
                camera.close()
                print('Stop streaming')
                self.terminal_streaming()

    def terminal_streaming(self):
        if self.reader is not None:
            self.reader.terminal_reader()
        for i in range(len(self.pool)):
            if self.pool[i] is not None:
                self.pool[i].terminated = True

    def writers(self):
        while self.finish - self.start < 5:
            writer = self.get_not_working_writer()
            if writer is None:
                self.ignore_stream.seek(0)
                self.ignore_stream.truncate()
                self.finish = time.time()
                yield self.ignore_stream
            else:
                writer.stream.seek(0)
                yield writer.stream
                writer.event.set()
                self.count += 1
                self.finish = time.time()

    def get_not_working_writer(self):
        for i in range(1):
            if not self.pool[i].working:
                return self.pool[i]
        return None

client = Client()
client.start_streaming()