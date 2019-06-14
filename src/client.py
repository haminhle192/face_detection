__author__ = 'vietbq'

import socket
import picamera
import time
import threading
import detection as detection
import json
import io

from socket_writer import SocketWriter

class Client:

    def __init__(self):
        self.connection = None
        self.pool = []
        self.pool_lock = threading.Lock()
        self.terminated = False
        self.ignore_stream = io.BytesIO()
        
    def connect_server(self, address, port):
        try:
            client_socket = socket.socket()
            client_socket.connect((address, port))
            connection = client_socket.makefile('wb')
            print('Connected %s' % address)
            return connection
        finally:
            return None

    def start_camera(self):
        self.connection = self.connect_server('192.168.1.183', 8989)
        detector = detection.Detection()
        self.pool = [(SocketWriter(self.connection, detector)) for i in range(1)]
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            camera.framerate = 10
            time.sleep(2)
            camera.capture_sequence(self.writers(), 'jpeg', use_video_port=True)

    def writers(self):
        while self.terminated is False:
            with self.pool_lock:
                writer = self.get_not_working_writer()
                if writer is None:
                    print('Ignore frame')
                    self.ignore_stream.seek(0)
                    self.ignore_stream.truncate()
                    yield self.ignore_stream
                    continue
                yield writer.stream
                writer.event.set()

    def get_not_working_writer(self):
        for i in range(1):
            if not self.pool[i].working:
                return self.pool[i]
        return None

client = Client()
client.start_camera()