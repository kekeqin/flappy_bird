import random
import sys
import pygame

class Player:
    def __init__(self, p_id, H, asserts):
        self.asserts = asserts
        self.H = H
        self.id = p_id
        self.x = random.randint(0, 100)
        self.y = random.randint(180, 250)
        
        self.y_vel = -6  # 跳跃初始速度
        self.gravity = 0.5  # 重力加速度
        self.velocity = 0  # 当前垂直速度
        self.dead = False
        
        self.pic = asserts.get_image("red_mid")
        self.frame_width =  self.pic.get_width() 
        self.frame_height = self.pic.get_height() 
        self.frame_num = 0
        self.frame_rect = (self.frame_num * self.frame_width, 0 * self.frame_height,
                           self.frame_width, self.frame_height)
        
        self.rect = pygame.Rect(self.x, self.y, self.frame_width, self.frame_height)

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
            if self.y < 0 or self.y > self.H - self.frame_height:             
                self.y = self.reset_position()  # 重置位置
                self.velocity = 0
                self.dead = True  # 设置为死亡状态
                
    def check_collision(self, current_pipes):
        if pygame.sprite.spritecollideany(self, current_pipes):
            self.dead = True

    def reset_position(self):
        self.x = random.randint(0, 100)
        self.y = (self.H - self.frame_height) / 2
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

    
    def draw(self, win):
        if not self.dead:
            win.blit(self.pic, (self.x, self.y), self.frame_rect)
 
            font = pygame.font.SysFont("Arial", 10)          
            id_text = font.render(self.id, True, (150, 150, 150))
            win.blit(id_text, (self.x + round(self.frame_width/2)
                            - round(id_text.get_width()/2),
                            self.y - id_text.get_height()))
        else:
            gameover = self.asserts.get_image("gameover")
            win.blit(gameover, (40, 180))
        
        