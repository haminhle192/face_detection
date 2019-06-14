__author__ = 'vietbq'

import socket
import picamera
import time
import threading
import detection as detection
import json
import io
from socket_reader import SocketReader
from socket_writer import SocketWriter

class Client:

    def __init__(self):
        self.pool = []
        self.pool_lock = threading.Lock()
        self.connection_lock = threading.Lock()
        self.terminated = False
        self.ignore_stream = io.BytesIO()
        self.client_socket = None
        self.connection = None
        self.count = 0
        self.start = 0
        self.finish = 0
        self.reader = None
        
    def connect_server(self, address, port):
        self.client_socket = socket.socket()
        self.client_socket.connect((address, port))
        connection = self.client_socket.makefile('wb')
        print('Connected %s' % address)
        return connection

    def start_camera(self):
        self.start = time.time()
        self.finish = time.time()
        with picamera.PiCamera() as camera:
            try:
                self.connection = self.connect_server('192.168.1.212', 8989)
                detector = detection.Detection()
                self.reader = SocketReader(self.connection)
                self.pool = [(SocketWriter(self.connection_lock, self.connection, detector)) for i in range(1)]
                camera.resolution = (640, 480)
                camera.framerate = 10
                time.sleep(2)
                camera.capture_sequence(self.writers(), 'jpeg', use_video_port=True)
            except Exception as e:
                print(e)
                print('Connect to server error')
            finally:
                print('Stop streaming')
                self.terminal_streaming()

    def terminal_streaming(self):
        if self.reader is not None:
            self.reader.terminated = True
            self.reader.connection.close()
            self.reader = None
        for i in range(len(self.pool)):
             if self.pool[i] is not None:
                self.pool[i].terminated = True
        if self.connection is not None:
            self.connection.close()
        if self.client_socket is not None:
            self.client_socket.close()

    def writers(self):
        while self.finish - self.start < 30:
            writer = self.get_not_working_writer()
            if writer is None:
                self.ignore_stream.seek(0)
                self.ignore_stream.truncate()
                self.finish = time.time()
                yield self.ignore_stream
                continue
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
client.start_camera()