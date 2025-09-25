import pygame
from Configuraciones import *

import math
import pygame

class Jefe(pygame.sprite.Sprite):
    def __init__(self, x, y, required_power=120, reward_power=999, w=120, h=160):
        super().__init__()
        self.base_w, self.base_h = w, h
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)  # con transparencia
        self.rect = self.image.get_rect(topleft=(x, y))

        self.required_power = int(required_power)
        self.reward_power = int(reward_power)
        self.defeated = False
        self.tiempo_inicio = pygame.time.get_ticks()

    def actualizar_forma(self):
     
        tiempo = (pygame.time.get_ticks() - self.tiempo_inicio) / 500
        factor = 1 + 0.1 * math.sin(tiempo)  # palpita entre 0.9 y 1.1
        w = int(self.base_w * factor)
        h = int(self.base_h * factor)

        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        r = 200 + int(55 * math.sin(tiempo))     # oscila 200-255
        g = 50 + int(150 * abs(math.cos(tiempo))) # oscila 50-200
        b = 0  # sin azul para mantener la gama cálida
        color = (r, g, b)

        pygame.draw.ellipse(self.image, color, (0, 0, w, h))

        # ojos triangulares
        eye_w, eye_h = w // 5, h // 6
        ojo_izq = [(w//3 - eye_w, h//3), (w//3, h//3 - eye_h), (w//3 + eye_w//2, h//3)]
        ojo_der = [(2*w//3 + eye_w, h//3), (2*w//3, h//3 - eye_h), (2*w//3 - eye_w//2, h//3)]
        pygame.draw.polygon(self.image, (0, 0, 0), ojo_izq)
        pygame.draw.polygon(self.image, (0, 0, 0), ojo_der)

        # boca malvada 
        boca_rect = pygame.Rect(w//4, h//2, w//2, h//3)
        pygame.draw.arc(self.image, (0, 0, 0), boca_rect, math.pi*0.1, math.pi*0.9, 4)

        # aura brillante
        pygame.draw.ellipse(self.image, (255, 200, 0, 100), (5, 5, w-10, h-10), 3)

        # mantener posición centrada
        centro = self.rect.center
        self.rect = self.image.get_rect(center=centro)

    def interact(self, jugador):
        if self.defeated:
            return (False, 'El Jefe ya ha sido vencido...')

        requerido = self.required_power
        nodo = jugador.gemas.buscar(requerido)
        if nodo:
            jugador.gemas.eliminar(requerido)
            jugador.gemas.insertar(self.reward_power, 'Gema del Jefe', self.rect.centerx, self.rect.centery)
            self.defeated = True
            return (True, f'¡Has derrotado al Jefe! Entregaste {requerido} y recibiste la Gema del Jefe')
        else:
            suc = jugador.gemas.sucesor(requerido)
            pre = jugador.gemas.predecesor(requerido)
            elegido = suc if suc and (not pre or abs(suc[0]-requerido) < abs(pre[0]-requerido)) else pre
            if elegido:
                jugador.gemas.eliminar(elegido[0])
                jugador.gemas.insertar(self.reward_power, 'Gema del Jefe', self.rect.centerx, self.rect.centery)
                self.defeated = True
                return (True, f'El Jefe aceptó {elegido[0]} y te dio la Gema del Jefe')
            else:
                return (False, 'Jefe: No tienes gemas para entregarme')

    def draw(self, pantalla, camara):
        self.actualizar_forma()
        pantalla.blit(self.image, camara.aplicar(self.rect))
        font = pygame.font.SysFont('Consolas', 24, bold=True)

        # texto arriba del jefe
        texto_arriba = font.render("Boss", True, (255, 50, 50))
        pos_arriba = texto_arriba.get_rect(center=(self.rect.centerx, self.rect.top - 20))
        pantalla.blit(texto_arriba, camara.aplicar(pos_arriba))

        # texto abajo del jefe
        texto_abajo = font.render("Presione E", True, (248, 255, 100))
        pos_abajo = texto_abajo.get_rect(center=(self.rect.centerx, self.rect.bottom + 20))
        pantalla.blit(texto_abajo, camara.aplicar(pos_abajo))



class ParedDivisible:
   
    def __init__(self, x, width, altura=ALTURA_VENTANA, color=(22, 25, 37), speed=8):
        # la pared ocupara verticalmente toda la ventana por defecto
        self.x = int(x)
        self.width = int(width)
        self.altura = int(altura)
        self.color = color

        mitad = self.altura // 2

        self.top_rect = pygame.Rect(self.x, 0, self.width, mitad)
        self.bottom_rect = pygame.Rect(self.x, mitad, self.width, self.altura - mitad)

        self.top_target_y = -mitad
        self.bottom_target_y = self.altura

        self.speed = speed
        self.closed = True
        self.opening = False

    def start_opening(self):
        if not self.opening and self.closed:
            self.opening = True

    def update(self):
        
        if not self.opening:
            return

        moved = False
        # mover la mitad superior hacia arriba
        if self.top_rect.y > self.top_target_y:
            self.top_rect.y -= self.speed
            if self.top_rect.y < self.top_target_y:
                self.top_rect.y = self.top_target_y
            moved = True

        # mover la mitad inferior hacia abajo
        if self.bottom_rect.y < self.bottom_target_y:
            self.bottom_rect.y += self.speed
            if self.bottom_rect.y > self.bottom_target_y:
                self.bottom_rect.y = self.bottom_target_y
            moved = True

        # cuando ambas hayan alcanzado su objetivo, considerar la pared abierta
        if not moved:
            self.opening = False
            self.closed = False

    def draw(self, pantalla, camara):
        # dibuja ambas mitades en el orden que cubra la escena
        pygame.draw.rect(pantalla, self.color, camara.aplicar(self.top_rect))
        pygame.draw.rect(pantalla, self.color, camara.aplicar(self.bottom_rect))

    def colliderect(self, rect):
        if not self.closed:
            return False
        return rect.colliderect(self.top_rect) or rect.colliderect(self.bottom_rect)

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    def world_rect(self):
        # rect completa en coordenadas del mundo (útil para debug/dibujo)
        return pygame.Rect(self.x, 0, self.width, self.altura)
