__author__ = 'vietbq'

import struct
import threading
import io

class SocketReader(threading.Thread):
    def __init__(self, reader_stream):
        super(SocketReader, self).__init__()
        self.reader = reader_stream
        self.stream = io.BytesIO()
        self.terminated = False

    def run(self):
        while not self.terminated:
            try:
                print('Waiting for read stream')
                data_len = struct.unpack('<L', self.reader.read(struct.calcsize('<L')))[0]
                if not data_len:
                    continue
                self.stream.write(self.reader.read(data_len))
                byte_str = self.stream.read()
                text_obj = byte_str.decode('UTF-8')
                print('Data received %s' % text_obj)
            except Exception as e:
                print(e)
                self.terminated = True
            finally:
                self.stream.seek(0)
                self.stream.truncate()
        print('Reader bye bye!')

    def terminal_reader(self):
        self.terminated = True
        self.reader.close()
        self.stream.close()