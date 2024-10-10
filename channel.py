import json
from event import Event
import threading
import socket

def receive_message(sock):  # 定义一个receive_message函数 ，用于从 socket 接收消息
    length_bytes = sock.recv(4)  # 接收长度的4个字节
    
    if len(length_bytes) == 0:  # 如果接收到的长度字节数为0，表示连接已关闭，直接返回
        return

    if len(length_bytes) < 4:  # 如果接收到的长度字节数小于4，抛出ValueError
        raise ValueError(f"Length prefix not received correctly {len(length_bytes)}")
    
    message_length = int.from_bytes(length_bytes, 'big') # 将接收到的长度字节转换为整数
    
    # 根据长度读取消息
    message_data = b''
    while len(message_data) < message_length:  # 循环接收消息数据直到接收到完整的消息
        packet = sock.recv(message_length - len(message_data))
        if not packet:
            raise ValueError("Socket connection broken")
        message_data += packet
    
    # 解码 JSON 数据
    return message_data.decode('utf-8')


def send_message(sock, message):
    # 序列化消息为 JSON 字符串
    json_message = json.dumps(message)
    # 将 JSON 字符串编码为字节
    packed_message = json_message.encode('utf-8')
    # 获取消息的长度
    message_length = len(packed_message)
    # 发送消息长度和消息本身
    sock.sendall(message_length.to_bytes(4, 'big'))  # 使用4个字节表示长度
    sock.sendall(packed_message)


class ServerChannel():
    def __init__(self, conn, handler):
        self.conn = conn
        self.handler = handler
        self.is_close = False
    
    def recv(self):
        t = threading.Thread(target=self._recv)  # 创建一个新的线程来处理接收消息
        t.start()
        self.t = t
        
    def _recv(self):
        while not self.is_close:  # 循环接收消息
            json_message = receive_message(self.conn)  # 调用 receive_message 函数接收消息
            if json_message:  # 如果接收到消息，
                data = json.loads(json_message) # 将其解析为 JSON 并创建 Event 对象
                self.handler(self, Event(id=data['id'], data=data['data']))  # 调用 handler 函数处理

    def close(self):
        self.is_close = True


## Client channel
class Channel():  # 定义一个名为 Channel 的类，用于处理客户端的通信
    def __init__(self, handler):
        self.handler = handler  # 初始化时传入一个处理函数
        self.is_close = False

    def recv(self):
        t = threading.Thread(target=self._recv)  # 创建一个新的线程来处理接收消息
        t.start()

    def _recv(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建一个 socket 对象用于 TCP 连接
        s.connect(("127.0.0.1", 5000))  # 连接到服务器
        self.socket = s
        while not self.is_close:  # 循环接收消息
            json_message = receive_message(s)  # 调用 receive_message 函数接收消息
            if json_message:  # 如果接收到消息，
                data = json.loads(json_message) # 将其解析为 JSON 并创建 Event 对象
                self.handler(Event(id=data['id'], data=data['data']))  # 调用 handler 函数处理


    def send(self, data):  # 调用 send_message 函数发送消息
        send_message(self.socket, data)
        
    def close(self):
        self.is_close = True