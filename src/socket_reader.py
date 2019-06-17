__author__ = 'vietbq'

import struct
import threading
import io

class SocketReader(threading.Thread):
    def __init__(self, reader):
        super(SocketReader, self).__init__()
        self.reader = reader
        self.stream = io.BytesIO()
        self.terminated = False
        self.start()

    def run(self):
        while not self.terminated:
            try:
                print('Waiting for read stream')
                data_len = struct.unpack('<L', self.reader.read(struct.calcsize('<L')))[0]
                if not data_len:
                    continue
                self.stream.write(self.reader.read(data_len))
                text_obj = self.stream.decode('UTF-8')
                print(text_obj)
                self.stream.seek(0)
                self.stream.truncate()
            except Exception as e:
                print(e)
                print('Reader disconnected')
                self.terminated = True
            finally:
                self.stream.seek(0)
                self.stream.truncate()
        print('Reader bye bye')

    def terminal_reader(self):
        self.terminated = True