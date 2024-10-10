import pygame

class Pipe(pygame.sprite.Sprite):

    def __init__(self, x, y, pipe_image, upwards=True):
        pygame.sprite.Sprite.__init__(self)
        self.image = pipe_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        if upwards:
            self.rect.top = y  
        else:
            self.rect.bottom = y   
        self.x_vel = -1.5

            
    def update(self):
        self.rect.x += self.x_vel
