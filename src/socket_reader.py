__author__ = 'vietbq'

import struct
import threading
import io
import json
from gpio_manager import GPIO_Manager

class SocketReader(threading.Thread):

    def __init__(self, reader_stream):
        super(SocketReader, self).__init__()
        self.reader = reader_stream
        self.stream = io.BytesIO()
        self.terminated = False
        self.gpio_manager = GPIO_Manager()
        self._lock = threading.Lock()


    def run(self):
        while not self.terminated:
            with self._lock:
                try:
                    data_len = struct.unpack('<L', self.reader.read(struct.calcsize('<L')))[0]
                    if not data_len:
                        continue
                    self.stream.write(self.reader.read(data_len))
                    self.stream.seek(0)
                    byte_str = self.stream.read()
                    text_obj = byte_str.decode('utf-8')
                    j_obj = json.loads(text_obj)
                    self.handle_light(j_obj)
                    self.stream.seek(0)
                    self.stream.truncate()
                except Exception as e:
                    print(e)
                    self.terminated = True
        self.gpio_manager.cleanup()
        print('Reader bye bye!')

    def terminal_reader(self):
        self.terminated = True
        self.reader.close()
        self.stream.close()

    def handle_light(self, j_object):
        if j_object['code'] == 0:
            data = j_object['data']
            print(type(data))
            if len(data) > 0:
                face_id = int(j_object['data'][0]['id'])
                if face_id == 3:
                    print('Turn on the light')