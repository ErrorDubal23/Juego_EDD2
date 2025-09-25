import pygame
import math

class Portal:
    def __init__(self, x, y, w=120, h=160):
        self.base_w, self.base_h = w, h
        self.rect = pygame.Rect(x, y, w, h)
        self.tiempo_inicio = pygame.time.get_ticks()
        self.active = False  # se activa con la gema del jefe

    def update(self, jugador, boss, boss_reward_power):
        # El portal esta activo si el jugador tiene la gema del jefe o si el boss ya fue derrotado
        self.active = jugador.gemas.buscar(getattr(boss, 'reward_power', boss_reward_power)) is not None

    def draw(self, pantalla, camara):
        tiempo = (pygame.time.get_ticks() - self.tiempo_inicio) / 400
        factor = 1 + 0.08 * math.sin(tiempo)
        w = int(self.base_w * factor)
        h = int(self.base_h * factor)

        surface = pygame.Surface((w, h), pygame.SRCALPHA)

        if self.active:
            # Colores vivos
            r = int(100 + 80 * math.sin(tiempo))
            g = int(100 + 80 * math.sin(tiempo + 2))
            b = int(150 + 100 * math.cos(tiempo))
        else:
            # Portal apagado y oscuro
            r, g, b = (70, 70, 120)

        # Anillos 
        num_anillos = 5
        for i in range(num_anillos):
            radio_w = w - i * (w // num_anillos)
            radio_h = h - i * (h // num_anillos)
            alpha = 180 - i * 30
            color = (r, g, b, max(alpha, 30))
            pygame.draw.ellipse(surface, color, (i*5, i*5, radio_w, radio_h), 3)

        if self.active:
            pygame.draw.ellipse(surface, (255, 255, 255, 120), (w//4, h//4, w//2, h//2))

        rect_centrado = surface.get_rect(center=self.rect.center)
        pantalla.blit(surface, camara.aplicar(rect_centrado))


        font = pygame.font.SysFont("Consolas", 24, bold=True)

        texto_arriba = font.render("Portal", True, (180, 220, 255))
        pos_arriba = texto_arriba.get_rect(center=(self.rect.centerx, self.rect.top - 20))
        pantalla.blit(texto_arriba, camara.aplicar(pos_arriba))

        texto_abajo = font.render("Presione E", True, (250, 255, 150))
        pos_abajo = texto_abajo.get_rect(center=(self.rect.centerx, self.rect.bottom + 20))
        pantalla.blit(texto_abajo, camara.aplicar(pos_abajo))
