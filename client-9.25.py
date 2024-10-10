import sys
import pygame
import pickle
import socket
import random
from event import Event, PLAYER_LIST, QUIT, READY, PIPE_DATA
from channel import Channel


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

FLOOR_Y = H - floor.get_height()   # 计算地板Y轴位置

class GameWindow:
    def __init__(self):
        self.channel = None
        self.window = self.init_window()
        self.pic_dict = {
            1: pygame.image.load("./pics/blue_mid.png"),
            2: pygame.image.load("./pics/red_mid.png"),
            3: pygame.image.load("./pics/yellow_mid.png"),
        }
        frame_width = self.pic_dict[1].get_width() 
        frame_height = self.pic_dict[1].get_height() 
        self.player = Player(p_id=None,
                             x=random.randint(0, 100),
                             y=random.randint(180, 250),
                             pic_num=random.randint(1, 3),
                             frame_width=frame_width,
                             frame_height=frame_height)
        self.pipes = pygame.sprite.Group()
        ## TODO 这里存在单人和多人冲突
        # self.create_pipes()

        # 多人玩家模式
        self.player_list = []
        self.game_mode = None
        self.pipe_data = []
        self.pipe_data_index = 0

    def init_window(self):
        pygame.init()
        pygame.display.set_caption('flappybird')
        return pygame.display.set_mode((W, H))
    
    def create_pipes(self):
        for i in range(N_PAIRS):
            pipe_y = random.randint(int(H*0.3), int(H*0.7))   # 随机生成管道的y坐标
            # 创建向上管道，第一个参数是x坐标，第二个是y坐标，第三个参数是方向参数True为上管道
            pipe_up = Pipe(W + i * DISTANCE, pipe_y, True)    
            # 创建向下管道，第一个参数是x坐标，第二个是y坐标，第三个参数是方向参数False为下管道
            pipe_down = Pipe(W + i * DISTANCE, pipe_y - PIPE_GAP, False)   
            self.pipes.add(pipe_up)  # 将上管道加入到精灵组
            self.pipes.add(pipe_down)  # 将下管道加入到精灵组
            
    def update_pipes(self):
        first_pipe_up = self.pipes.sprites()[0]
        first_pipe_down = self.pipes.sprites()[1]
        if first_pipe_up.rect.right < 0:
            # 如果第一个上管道已经完全移出屏幕，则生成新的管道对
            pipe_y = random.randint(int(H * 0.3), int(H * 0.7))
            new_pipe_up = Pipe(first_pipe_up.rect.x + N_PAIRS * DISTANCE, pipe_y, True)
            new_pipe_down = Pipe(first_pipe_up.rect.x + N_PAIRS * DISTANCE, pipe_y - PIPE_GAP, False)
            self.pipes.add(new_pipe_up)   # 将新上管道添加到精灵组                
            self.pipes.add(new_pipe_down)  # 将新下管道添加到精灵组
            first_pipe_up.kill()    # 从精灵组中移除旧上管道
            first_pipe_down.kill()  # 从精灵组中移除旧下管道

        self.pipes.update()   # 更新管道精灵组的状态            
            

    def update_window(self):     
        self.window.blit(screen, (0, 0))
        self.draw_room_text()
        self.player.move()
        self.player.check_collision(self.pipes)  # 检查玩家是否与管道碰撞
        self.player.draw(self.window, self.pic_dict[self.player.pic_num])
        self.pipes.draw(self.window)
        self.pipes.update()
        
        if self.game_started:
            self.floor_x -= 2
            if self.floor_x <= - (floor.get_width() - W):
                self.floor_x = 0
                
            self.window.blit(floor, (self.floor_x, FLOOR_Y))

        pygame.display.update()

    def handle_event(self, event):
        #1. 判断这个 event 是不是 play_list event
        if event.isEvent(PLAYER_LIST):
            self.handle_play_list_event(event=event)
        elif event.isEvent(READY):
            self.handle_ready_event(event=event)
        elif event.isEvent(PIPE_DATA):
            self.handle_pipe_data(event=event)


    def handle_pipe_data(self, event):
        self.pipe_data = event.data
        self.multiplayer_create_pipes()
        
    def multiplayer_create_pipes(self):
        for i in range(N_PAIRS):
            positions = self.pipe_data[self.pipe_data_index] 
            # 创建向上管道，第一个参数是x坐标，第二个是y坐标，第三个参数是方向参数True为上管道
            pipe_up = Pipe(W + i * DISTANCE, positions[0], True)
            # 创建向下管道，第一个参数是x坐标，第二个是y坐标，第三个参数是方向参数False为下管道
            pipe_down = Pipe(W + i * DISTANCE, positions[1], False)   
            self.pipes.add(pipe_up)  # 将上管道加入到精灵组
            self.pipes.add(pipe_down)  # 将下管道加入到精灵组
            self.pipe_data_index += 1
   
   
    def multiplayer_update_pipes(self):
        first_pipe_up = self.pipes.sprites()[0]
        first_pipe_down = self.pipes.sprites()[1]
        if first_pipe_up.rect.right < 0:
            # 如果第一个上管道已经完全移出屏幕，则生成新的管道对
            positions = self.pipe_data[self.pipe_data_index] 
            new_pipe_up = Pipe(first_pipe_up.rect.x + N_PAIRS * DISTANCE, positions[0], True)
            new_pipe_down = Pipe(first_pipe_up.rect.x + N_PAIRS * DISTANCE, positions[1], False)
            self.pipes.add(new_pipe_up)   # 将新上管道添加到精灵组                
            self.pipes.add(new_pipe_down)  # 将新下管道添加到精灵组
            first_pipe_up.kill()    # 从精灵组中移除旧上管道
            first_pipe_down.kill()  # 从精灵组中移除旧下管道
            self.pipe_data_index += 1

        self.pipes.update()   # 更新管道精灵组的状态                      

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
        self.connect()
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
                        
            self.update_pipes()
    
            if not self.game_started:
                # 如果游戏未开始，可以在这里显示一些等待开始的界面或文本
                self.window.blit(screen, (0, 0))  
                self.window.blit(flappy, (50, 50))
                self.window.blit(single_player_image, (65, 200))
                self.window.blit(multiplayer_image, (65, 300))
                self.window.blit(floor, (0, FLOOR_Y))

                pygame.display.update()
                continue  # 跳过游戏循环的其余部分
            # 游戏开始后的操作
            self.update_window()  # 更新窗口显示
            
            
    def handle_mouse_click(self, event):
        if 65 < event.pos[0] < 200 and 200 < event.pos[1] < 300:
            self.game_mode = 'single'
            print("已选择单人游戏模式")
        elif 65 < event.pos[0] < 200 and 300 < event.pos[1] < 400:
            self.game_mode = 'multiplayer'
            print("已选择多人游戏模式")
        if self.game_mode == 'single':
            self.single_player_mode()
        elif self.game_mode == 'multiplayer':
            self.multiplayer_mode()
    
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
            self.update_pipes()
            
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
            self.multiplayer_update_pipes()
            
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

    def draw_room_text(self):
        font = pygame.font.Font("SimHei.ttf", 15)
        room_text = font.render(f"{self.player.room}号房间", True, (150, 150, 150))
        self.window.blit(room_text, (W/2-room_text.get_width()/2, 10))

    def show_host(self, data):
        for player in data.values():
            if player.is_host:
                return
            
        self.player.is_host = True


class Player:
    def __init__(self, p_id, x, y, pic_num, frame_width, frame_height):
        self.id = p_id
        self.x = x
        self.y = y
        self.y_vel = -6  # 跳跃初始速度
        self.gravity = 0.5  # 重力加速度
        self.velocity = 0  # 当前垂直速度
        self.dead = False  # 初始时方块是死的

        self.pic_num = pic_num

        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame_num = 0
        self.frame_rect = (self.frame_num * self.frame_width, 0 * self.frame_height,
                           self.frame_width, self.frame_height)

        self.is_host = False
        self.room = random.randint(1, 2)
        
        self.rect = pygame.Rect(x, y, frame_width, frame_height)

    def move(self):
        if not self.dead:
            keys = pygame.key.get_pressed()
            # 跳跃逻辑：如果按下空格且没有死亡
            if keys[pygame.K_SPACE] and self.velocity >= 0:
                self.velocity = self.y_vel
            self.velocity += self.gravity
            self.y += self.velocity
            
            self.rect.x = self.x
            self.rect.y = self.y

            # 检测是否到达顶部或底部边界
            if self.y < 0 or self.y > H - self.frame_height:             
                self.y = self.reset_position()  # 重置位置
                self.velocity = 0
                self.dead = True  # 设置为死亡状态
                
    def check_collision(self, pipes):
        if pygame.sprite.spritecollideany(self, pipes):
            self.dead = True

    def reset_position(self):
        # 重置方块的垂直位置到窗口的中间位置
        self.x = random.randint(0, 100)
        self.y = (H - self.frame_height) / 2
        self.velocity = 0
        self.rect.x = self.x
        self.rect.y = self.y
        return self.y

    def set_frame_rect(self, pic_row):
        self.frame_num += 1
        if self.current_dir != self.last_dir or self.frame_num > 3:
            self.frame_num = 0

        self.frame_rect = (self.frame_num * self.frame_width, pic_row 
                           * self.frame_height,
                           self.frame_width, self.frame_height)

    
    def draw(self, win, pic):
        if not self.dead:
            win.blit(pic, (self.x, self.y), self.frame_rect)
 
            font = pygame.font.SysFont("Arial", 10)          # 1
            id_text = font.render(self.id, True, (150, 150, 150))
            win.blit(id_text, (self.x + round(self.frame_width/2)
                            - round(id_text.get_width()/2),
                            self.y - id_text.get_height()))
        else:
            # 如果死亡，显示死亡信息
            font = pygame.font.SysFont("Arial", 24)
            death_text = font.render("Game Over", True, (255, 0, 0))
            win.blit(death_text, (80, 180))
        
        if self.is_host:                    
            host_text = font.render("房主", True, (150, 150, 150))
            win.blit(host_text, (self.x + round(self.frame_width/2) 
                                 - round(host_text.get_width()/2),
                                   self.y + self.frame_height 
                                   + host_text.get_height()))
            

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, upwards=True):
        pygame.sprite.Sprite.__init__(self)
        if upwards:  
            self.image = up_pipe
            self.rect = self.image.get_rect()
            self.rect.x = x   
            self.rect.top = y  
        else:
            self.image = down_pipe
            self.rect = self.image.get_rect()  
            self.rect.x = x    
            self.rect.bottom = y   
        self.x_vel = -1.5  
            
    def update(self):
        self.rect.x += self.x_vel



if __name__ == '__main__':
    game = GameWindow()
    game.start()
