import pygame
from Configuraciones import *

class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=MARRON, transparente=False):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)  # soporta transparencia
        if not transparente:
            self.image.fill(color)
        # Si transparente=True, la Surface queda vacía (invisible)
        self.rect = self.image.get_rect(topleft=(x, y))
