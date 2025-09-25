import pygame
from Configuraciones import *


class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=(101, 67, 33), transparente=False, radio=12):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)  # soporta transparencia

        if not transparente:
            # --- Rectángulo marrón oscuro con esquinas redondeadas ---
            base_rect = pygame.Rect(0, 0, w, h)
            pygame.draw.rect(self.image, color, base_rect, border_radius=radio)

            # --- Degradado de sombra interna ---
            for i in range(h):
                tono = (
                    max(0, color[0] - i // 4),
                    max(0, color[1] - i // 5),
                    max(0, color[2] - i // 6)
                )
                pygame.draw.rect(self.image, tono, (0, i, w, 1), border_radius=radio)

            # --- Vetas de madera ---
            for i in range(5, w, 20):
                pygame.draw.line(self.image, (60, 40, 30), (i, 5), (i, h - 5), 2)

            # --- Musgo verde oscuro en la parte superior ---
            pygame.draw.rect(self.image, (15, 60, 15), (0, 0, w, 12), border_radius=radio)

            # Pequeñas manchas de musgo irregular
            for i in range(0, w, 25):
                pygame.draw.circle(self.image, (10, 50, 10), (i + 10, 10), 4)

        self.rect = self.image.get_rect(topleft=(x, y))
