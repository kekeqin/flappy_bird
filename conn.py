from threading import Thread
import pickle

class Connect:
    def __init__(self, server, conn) -> None:
        self.server = server
        self.conn = conn

    def handle_message(self):
        Thread(target=self._unpack).start()

    def _unpack(self):
        while True:
            try:
                data = self.conn.recv(2048)
                if not data:
                    print("未接收到数据，关闭连接")
                    self.server.remove()
                    break
                else:
                    data = pickle.loads(data)
                    # TODO 反序列化 
                    self.handle(data)
            except Exception as e:
                print(repr(e))
                break

    def handle(self, data):
        pass

    def send(self, data):
        pass

    def close(self):
        self.conn.close()

    def equals(self, connect):
        return str(id(self.conn)) ==  str(id(connect.conn))
