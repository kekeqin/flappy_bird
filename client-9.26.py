import sys
import pygame
import pickle
import socket
import random, os
from event import Event, PLAYER_LIST, QUIT, READY, PIPE_DATA
from channel import Channel
from client_pipe import SinglePlayerPipes, MutilPlayerPipes
from bird import Player
from network import Network
from asserts import Asserts
from game_screen import HomeScreen

W = 288
H = 512
FPS = 60
DISTANCE = 200   # 设置每对管道间的距离
N_PAIRS = 4   # 设置初始生成的管道对数
PIPE_GAP = 150   # 设置管道之间的垂直距离

screen = pygame.image.load("./pics/day.png")
start = pygame.image.load("./pics/start.png")
flappy = pygame.image.load("./pics/flappy.png")
floor = pygame.image.load("./pics/floor.png")
up_pipe = pygame.image.load("./pics/green_pipe.png")
down_pipe = pygame.transform.flip(up_pipe, False, True)
single_player_image = pygame.image.load("./pics/single.jpg")
multiplayer_image = pygame.image.load("./pics/multiplayer.jpg")
gameover = pygame.image.load("./pics/gameover.png")
key = pygame.image.load("./pics/key.png")

FLOOR_Y = H - floor.get_height()   # 计算地板Y轴位置

asserts = Asserts()

class GameWindow:
    def __init__(self):
        self.channel = None
        self.window = self.init_window() 
        self.player = Player(p_id=None,H = H, asserts = asserts)

        self.client_pipes = None
        
        # 多人玩家模式
        self.player_list = []
        
    def init_window(self):
        pygame.init()
        pygame.display.set_caption('flappybird')
        return pygame.display.set_mode((W, H))
    
    def update_window(self):     
        self.window.blit(screen, (0, 0))
        self.player.move()
        self.player.check_collision(self.client_pipes.pipes)  # 检查玩家是否与管道碰撞
        self.player.draw(self.window)

        if self.game_started:
            self.client_pipes.draw_and_update(self.window)
            self.floor_x -= 2
            if self.floor_x <= - (floor.get_width() - W):
                self.floor_x = 0             
            self.window.blit(floor, (self.floor_x, FLOOR_Y)) 

        pygame.display.update()
    
    def handle_event(self, event):
        #1. 判断这个 event 是不是 play_list event
        if event.isEvent(PLAYER_LIST):
            self.handle_play_list_event(event=event)
        elif event.isEvent(PIPE_DATA):
            self.handle_pipe_data(event=event)

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

    def start(self):
        clock = pygame.time.Clock()
        self.running = True
        self.game_started = False  # 添加一个标志来控制游戏开始
        self.floor_x = 0
        
        while self.running:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    return
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event)
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.game_started:
                        self.game_started = True  # 按下空格键开始游戏 
                                                   
            if not self.game_started:
                HomeScreen(self, asserts, FLOOR_Y).render()
                continue  # 跳过游戏循环的其余部分
            # 游戏开始后的操作
            self.update_window()  # 更新窗口显示  

    def handle_mouse_click(self, event):
        if 65 < event.pos[0] < 200 and 200 < event.pos[1] < 300:
            self.client_pipes = SinglePlayerPipes(H, W, N_PAIRS, DISTANCE, PIPE_GAP, up_pipe, down_pipe)
            self.client_pipes.init_pipes()
            self.single_player_mode()
            print("已选择单人游戏模式")
        elif 65 < event.pos[0] < 200 and 300 < event.pos[1] < 400:
            self.connect()
            self.multiplayer_mode()
            print("已选择多人游戏模式")
    
    def single_player_mode(self):
        self.init_window()
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    return                   
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.game_started = True 
            
            self.client_pipes.update_pipes()
             
            if not self.game_started:
                self.window.blit(screen, (0, 0))  
                self.window.blit(start, (50, 50))                
                self.window.blit(floor, (0, FLOOR_Y))
                pygame.display.update()
                continue  
            pygame.display.update()
            self.update_window()
       
    def multiplayer_mode(self):
        self.init_window()
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    return                   
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.game_started = True  

            self.client_pipes.update_pipes()
             
            if not self.game_started:
                self.window.blit(screen, (0, 0))  
                self.window.blit(flappy, (50, 50))                
                self.window.blit(floor, (0, FLOOR_Y))
                    
                if len(self.player_list) != 0:
                    for bird in self.player_list:
                        # print(bird["image"],bird["position"])
                        self.window.blit(bird["image"],bird["position"])
                        font = pygame.font.SysFont("Arial", 14)
                        pid_text = font.render(bird["pid"], True, (0, 0, 0))
                        self.window.blit(pid_text, bird["pid_position"])
                pygame.display.update()
                continue  # 跳过游戏循环的其余部分
            pygame.display.update()
            self.update_window()

    def quit(self):
        self.channel.send(data=Event(id=QUIT, data=None).to_dict())
        self.channel.close()
        pygame.quit()
        sys.exit()
        

if __name__ == '__main__':
    game = GameWindow()
    game.start()
