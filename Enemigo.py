import pygame
import random
from Configuraciones import *

class Enemigo(pygame.sprite.Sprite):
    def __init__(self, x,y, min_x, max_x, dano=1):
        super().__init__()
        self.image = pygame.Surface((34,40))
        self.image.fill((200,40,40))
        self.rect = self.image.get_rect(topleft=(x,y))

        self.vx = random.choice([-1.2,1.2])
        self.vy = 0
        self.en_suelo = False

        self.patrulla_min_x = min_x
        self.patrulla_max_x = max_x

        self.dano = dano
        self.cooldown_ataque = 0
        self.vida = random.randint(1,3)

    def update(self, jugador, plataformas, enemigos):
        # -------- movimiento básico --------
        centro = self.rect.centerx
        if abs(centro - jugador.rect.centerx) < 250:
            if centro < jugador.rect.centerx:
                self.rect.x += 1.6
            else:
                self.rect.x -= 1.6
        else:
            self.rect.x += self.vx
            if self.rect.left < self.patrulla_min_x or self.rect.right > self.patrulla_max_x:
                self.vx *= -1

        # -------- gravedad --------
        self.vy += GRAVEDAD
        self.rect.y += self.vy
        self.en_suelo = False
        for p in plataformas:
            if self.rect.colliderect(p.rect):
                if self.vy > 0:  # caer sobre la plataforma
                    self.rect.bottom = p.rect.top
                    self.vy = 0
                    self.en_suelo = True
                elif self.vy < 0:  # chocar con el techo
                    self.rect.top = p.rect.bottom
                    self.vy = 0

        # -------- separación de otros enemigos --------
        for otro in enemigos:
            if otro is not self and self.rect.colliderect(otro.rect):
                if self.rect.centerx < otro.rect.centerx:
                    self.rect.x -= 1
                    otro.rect.x += 1
                else:
                    self.rect.x += 1
                    otro.rect.x -= 1

        if self.cooldown_ataque > 0:
            self.cooldown_ataque -= 1

    def intentar_atacar(self, jugador):
        if self.cooldown_ataque > 0: 
            return False
        if self.rect.colliderect(jugador.rect):
            jugador.recibir_danio(self.dano)
            self.cooldown_ataque = FPS
            return True
        return False

    def draw_barra_vida(self, pantalla, camara_x):
        ancho = self.rect.width
        alto = 5
        max_vida = 3
        relleno = max(0, int((self.vida / max_vida) * ancho))
        x = self.rect.x - camara_x
        y = self.rect.y - 8
        pygame.draw.rect(pantalla, ROJO, (x, y, relleno, alto))
        pygame.draw.rect(pantalla, BLANCO, (x, y, ancho, alto), 1)

    def muere(self):
        # posibilidad de soltar algo luego
        self.kill()
