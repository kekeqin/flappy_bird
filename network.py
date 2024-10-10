import socket
from event import Event, PLAYER_LIST, QUIT, READY, PIPE_DATA
from client_pipe import MutilPlayerPipes
from bird import Player
from channel import Channel

class Network:
    def __init__(self, event, birds):
        self.event = event
        self.birds = birds
        self.channel = None

    def handle_pipe_data(self, event):
        self.client_pipes = MutilPlayerPipes(H, W, N_PAIRS, DISTANCE, up_pipe, down_pipe, event.data)
        self.client_pipes.init_pipes()
        
    def render_player_list(self, birds):
        bird_list = []
        gap = 10
        n = len(birds)
        y0 = self.window.get_height() - 150
        x0 = (self.window.get_width() - 34 * n - ( n - 1 ) * gap ) / 2
        x_offset = x0
        x_gap = 0
        x_bird = 0
        for i, bird in enumerate(birds):
            x = x_offset + x_bird + x_gap
            x_pid = x + 12
            bird_list.append({
                "image": self.pic_dict[1], 
                "position": (x, y0),
                "pid": bird["pid"],
                "pid_position": (x_pid + 4, y0 - 8)
            })
            # self.window.draw(self.pic_dict[1], (x, y0))
            x_gap = gap
            x_bird = 34
            x_offset = x
        
        self.player_list = bird_list

    def handle_play_list_event(self, event):
        # print("handle_play_list_event", event.id, event.data[0]["pid"], len(event.data))
        self.render_player_list(event.data)       

    def connect(self):
        self.channel = Channel(self.handle_event)
        self.channel.recv()
    