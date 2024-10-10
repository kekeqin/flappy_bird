import random
from pipe import Pipe
import pygame

class BasePlayerPipes:
    def __init__(self, H, W, N_PAIRS, DISTANCE, up_pipe_image, down_pipe_image):
      self.H = H
      self.W = W
      self.N_PAIRS = N_PAIRS
      self.DISTANCE = DISTANCE
      self.up_pipe_image = up_pipe_image
      self.down_pipe_image = down_pipe_image
      self.pipes = pygame.sprite.Group()

    def init_pipes(self):
      raise NotImplementedError

    def update_pipes(self):
      raise NotImplementedError

    def draw_and_update(self, window):
      self.pipes.draw(window)
      self.pipes.update()


class SinglePlayerPipes(BasePlayerPipes):
  def __init__(self, H, W, N_PAIRS, DISTANCE, PIPE_GAP, up_pipe_image, down_pipe_image):
    super().__init__(H, W, N_PAIRS, DISTANCE, up_pipe_image, down_pipe_image)
    self.PIPE_GAP = PIPE_GAP
    

  def init_pipes(self):
    for i in range(self.N_PAIRS):
      x = self.W + i * self.DISTANCE
      up_y = random.randint(int(self.H*0.3), int(self.H*0.7))   # 随机生成管道的y坐标
      
      # 创建向上管道，第一个参数是x坐标，第二个是y坐标，第三个参数是方向参数True为上管道
      pipe_up = Pipe(x, up_y, self.up_pipe_image, True)
      
      # 创建向下管道，第一个参数是x坐标，第二个是y坐标，第三个参数是方向参数False为下管道
      down_y = up_y - self.PIPE_GAP
      pipe_down = Pipe(x, down_y, self.down_pipe_image, False)
      
      self.pipes.add(pipe_up)  # 将上管道加入到精灵组
      self.pipes.add(pipe_down)  # 将下管道加入到精灵组

  def update_pipes(self):
    first_pipe_up = self.pipes.sprites()[0]
    first_pipe_down = self.pipes.sprites()[1]

    # 如果第一个上管道已经完全移出屏幕，则生成新的管道对
    if first_pipe_up.rect.right < 0:
      up_y = random.randint(int(self.H * 0.3), int(self.H * 0.7))

      pipe_x = first_pipe_up.rect.x + self.N_PAIRS * self.DISTANCE
      new_pipe_up = Pipe(pipe_x, up_y, self.up_pipe_image, True)

      down_y = up_y - self.PIPE_GAP
      new_pipe_down = Pipe(pipe_x, down_y, self.down_pipe_image, False)
      
      self.pipes.add(new_pipe_up)
      self.pipes.add(new_pipe_down)
      
      first_pipe_up.kill()
      first_pipe_down.kill()


class MutilPlayerPipes(BasePlayerPipes):
  def __init__(self, H, W, N_PAIRS, DISTANCE, up_pipe_image, down_pipe_image, pipe_data):
    super().__init__(H, W, N_PAIRS, DISTANCE, up_pipe_image, down_pipe_image)
    self.pipe_data = pipe_data
    self.pipe_data_index = 0

  def init_pipes(self):
    for i in range(self.N_PAIRS):
      positions = self.pipe_data[self.pipe_data_index]
      # 创建向上管道，第一个参数是x坐标，第二个是y坐标，第三个参数是方向参数True为上管道
      x = self.W + i * self.DISTANCE
      pipe_up = Pipe(x, positions[0], self.up_pipe_image, True)
      # 创建向下管道，第一个参数是x坐标，第二个是y坐标，第三个参数是方向参数False为下管道
      pipe_down = Pipe(x, positions[1], self.down_pipe_image, False)
      self.pipes.add(pipe_up)  # 将上管道加入到精灵组
      self.pipes.add(pipe_down)  # 将下管道加入到精灵组
      self.pipe_data_index += 1

  def update_pipes(self):
    first_pipe_up = self.pipes.sprites()[0]
    first_pipe_down = self.pipes.sprites()[1]

    if first_pipe_up.rect.right < 0:
      positions = self.pipe_data[self.pipe_data_index] 

      x = first_pipe_up.rect.x + self.N_PAIRS * self.DISTANCE
      new_pipe_up = Pipe(x, positions[0], self.up_pipe_image, True)
      new_pipe_down = Pipe(x, positions[1], self.down_pipe_image, False)
      
      self.pipes.add(new_pipe_up) 
      self.pipes.add(new_pipe_down)  
      
      first_pipe_up.kill()
      first_pipe_down.kill()
      
      self.pipe_data_index += 1 
