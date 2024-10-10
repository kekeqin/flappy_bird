import pygame
import os

class Asserts:
    
    def __init__(self):
        self.images = self._load_images()
        self.audios = self._load_audios()
    
    def get_brid():
        pass
    
    def get_image(self, name):
        return self.images[name]
    
    def _load_images(self):
        images = {}
        
        for file in os.listdir("./pics"):
            name, extension = os.path.splitext(file)
            if extension in [".png", ".jpg"]:
                path = os.path.join("./pics", file)
                images[name] = pygame.image.load(path)
        
        return images

    def _load_audios(self):
        return {}
