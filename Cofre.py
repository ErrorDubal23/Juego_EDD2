import pygame
class Cofre(pygame.sprite.Sprite):
    def __init__(self, x,y, tipo='gema', valor=None):
        super().__init__()
        self.image = pygame.Surface((32,26)); self.image.fill((160,120,40))
        self.rect = self.image.get_rect(topleft=(x,y))
        self.abierto=False; self.tipo=tipo; self.valor=valor
