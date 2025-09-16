import pygame
class GemaSprite(pygame.sprite.Sprite):
    def __init__(self, poder, nombre, x, y):
        super().__init__()
        self.poder = int(poder); self.nombre = nombre
        self.image = pygame.Surface((18,18))
        self.image.fill((50 + (self.poder*3)%200, 50, 200 - (self.poder*2)%150))
        self.rect = self.image.get_rect(center=(x,y))