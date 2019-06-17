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
        print('Reader is running')
        while not self.terminated:
            try:
                data_len = struct.unpack('<L', self.reader.read(struct.calcsize('<L')))[0]
                if not data_len:
                    continue
                self.stream.write(self.reader.read(data_len))
                self.stream.seek(0)
                byte_str = self.stream.read()
                text_obj = byte_str.decode()
                j_obj = json.loads(text_obj)
                self.handle_light(j_obj)
                self.stream.seek(0)
            except Exception as e:
                print(e)
            finally:
                self.stream.truncate()
        self.gpio_manager.cleanup()
        self.stream.close()
        print('Reader bye bye!')

    def terminal_reader(self):
        self.terminated = True
        self.reader.close()


    def handle_light(self, j_object):
        print(j_object)
        if j_object['code'] == 0:
            data = j_object['data']
            if len(data) > 0:
                face_id = int(j_object['data'][0]['id'])
                if face_id == 3:
                    print('Turn on the light')
                    self.gpio_manager.turn_on()