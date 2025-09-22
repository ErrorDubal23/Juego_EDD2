import pygame, math

class GemaSprite(pygame.sprite.Sprite):
    def __init__(self, poder, nombre, x, y):
        super().__init__()
        self.poder = int(poder)
        self.nombre = nombre

        # tamaño base de la gema
        size = 16
        self.base_image = pygame.Surface((size*3, size*3), pygame.SRCALPHA)
        
        # color principal según poder
        color = (50 + (self.poder*3) % 200,
                 50 + (self.poder*5) % 150,
                 200 - (self.poder*2) % 150)

        # coordenadas del rombo (gema central)
        cx, cy = self.base_image.get_width()//2, self.base_image.get_height()//2
        points = [
            (cx, cy - size),   # arriba
            (cx + size, cy),   # derecha
            (cx, cy + size),   # abajo
            (cx - size, cy)    # izquierda
        ]
        
        # dibujar la gema central
        pygame.draw.polygon(self.base_image, color, points)
        pygame.draw.polygon(self.base_image, (230,230,230), points, 2)  # borde

        # resplandor alrededor
        glow = pygame.Surface((size*5, size*5), pygame.SRCALPHA)
        for r in range(40, 0, -8):  # círculos concéntricos con alpha decreciente
            alpha = max(20, 200 - r*4)
            pygame.draw.circle(glow, (*color, alpha), (glow.get_width()//2, glow.get_height()//2), r)
        glow_rect = glow.get_rect(center=(cx, cy))
        self.base_image.blit(glow, glow_rect, special_flags=pygame.BLEND_RGBA_ADD)

        # esta imagen será la usada por Pygame
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))

        # variables para animar el brillo
        self.t = 0

    
