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
        self._lock = threading.Lock()

    def run(self):
        while not self.terminated:
            with self._lock:
                try:
                    print('Waiting for read stream')
                    data_len = struct.unpack('<L', self.reader.read(struct.calcsize('<L')))[0]
                    if not data_len:
                        continue
                    self.stream.write(self.reader.read(data_len))
                    self.stream.seek(0)
                    byte_str = self.stream.read()
                    text_obj = byte_str.decode('utf-8')
                    print('Data len %s' % data_len)
                    print('Data received %s' % text_obj)
                    self.stream.seek(0)
                    self.stream.truncate()
                except Exception as e:
                    print(e)
                    self.terminated = True
        print('Reader bye bye!')

    def terminal_reader(self):
        self.terminated = True
        self.reader.close()
        self.stream.close()