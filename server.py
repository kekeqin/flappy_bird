import socket
from player import Player
from channel import send_message, ServerChannel
from event import Event, PLAYER_LIST, QUIT, CLIENT_QUIT, READY, PIPE_DATA
import random


class Server:
    def __init__(self):
        self.port = 5000
        self.host = "127.0.0.1"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.players = []
        self.conns = []
        self.channels = []
        self.players_ready = []

    def start(self):
        self.get_socket_ready()
        self.handle_connection()

    def get_socket_ready(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print("服务器已准备接收客户端连接")


    def handle_connection(self):
        while True:
            conn, addr = self.sock.accept()
            self.conns.append(conn)
            print(f"接收到来自{addr}的连接 , Players: {len(self.players)}")

            player = Player(pid = len(self.players) + 1)
            self.players.append(player)
            self.players_ready.append(False)

            player_list = self._get_play_list()
            
            ## 发送给所有客户端
            self.broadcast(data=Event(id=PLAYER_LIST, data=player_list).to_dict())
            self.broadcast(data=Event(id=PIPE_DATA, data=self.gen_pipe_data()).to_dict())
            
            channel = ServerChannel(conn, self.client_event_handler)
            channel.recv()
            self.channels.append(channel)

    def client_event_handler(self, channel, event):
        if event.isEvent(QUIT):
            self.handle_quit_event(channel)
    
    def gen_pipe_data(self):
        pipes = []
        H = 512
        gap = 150
        for i in range(1000):
            y1 = random.randint(int(H * 0.3), int(H * 0.7))
            pipes.append(
                [
                    y1, # 0
                    y1 - gap # 1          
                ]
            )
        return pipes

    
    def handle_quit_event(self, channel):
        self.remove(channel.conn)
        # 广播
        self.broadcast(Event(id=CLIENT_QUIT, data=None).to_dict())
        player_list = self._get_play_list()
        self.broadcast(data=Event(id=PLAYER_LIST, data=player_list).to_dict())

    def broadcast(self, data):
        for connection in self.conns:
            send_message(connection, data)

    def remove(self, conn):
        for i, c in enumerate(self.conns):
            if str(id(c)) == str(id(conn)):
                self.conns.pop(i)
                self.players.pop(i)
                self.channels[i].close()
                self.channels.pop(i)
                break
        conn.close()

    def _get_play_list(self):
        player_list = []
        for p in self.players:
            player_list.append(p.to_dict())
        
        return player_list


if __name__ == '__main__':
    server = Server()
    server.start()


