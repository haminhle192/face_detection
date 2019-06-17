__author__ = 'vietbq'

import struct
import threading
import io

class SocketReader(threading.Thread):
    def __init__(self, connection):
        super(SocketReader, self).__init__()
        self.connection = connection
        self.stream = io.BytesIO()
        self.terminated = False
        self.start()

    def run(self):
        while not self.terminated:
            try:
                print('Waiting for read stream')
                can_frame_size = struct.calcsize('L')
                data_len, addr = self.connection.recvfrom(can_frame_size)
                if addr is None:
                    self.terminated = True
                print('Received: data_len=%s, addr=%s' % (data_len, addr))
                # data_len = struct.unpack('<L', self.connection.read(struct.calcsize('<L')))[0]
                if not data_len:
                    continue
                self.stream.write(self.connection.read(data_len))
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
        print('Reader stopped')
        self.terminated = True