import pygame

class GameScreen:
    def __init__(self, game):
        self.game = game
        
    def render(self, **args):
        pass
    
    def blit(self, image, args):
        self.game.window.blit(image, args)
    
class HomeScreen(GameScreen):
    def __init__(self, game, asserts, FLOOR_Y):
        super().__init__(game)
        self.asserts = asserts
        self.FLOOR_Y = FLOOR_Y
        
    def render(self, **args):
        self.blit(self.asserts.get_image("day"), (0, 0))
        self.blit(self.asserts.get_image("flappy"), (50, 50))
        self.blit(self.asserts.get_image("single"), (65, 200))
        self.blit(self.asserts.get_image("multiplayer"), (65, 300))
        self.blit(self.asserts.get_image("floor"), (0, self.FLOOR_Y))
        
        pygame.display.update()