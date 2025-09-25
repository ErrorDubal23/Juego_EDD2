import pygame, random, math
from Configuraciones import *

class Enemigo(pygame.sprite.Sprite):
    def __init__(self, x, y, min_x=None, max_x=None, dano=1):
        super().__init__()
        self.radio = 20
        self.base_image = pygame.Surface((self.radio*2, self.radio*2), pygame.SRCALPHA)

        pygame.draw.circle(self.base_image, (200, 40, 40), (self.radio, self.radio), self.radio)
        pygame.draw.circle(self.base_image, (80, 0, 0), (self.radio, self.radio), self.radio, 3)

        eye_radius = 4
        pygame.draw.circle(self.base_image, (0,0,0), (self.radio-6, self.radio-4), eye_radius)
        pygame.draw.circle(self.base_image, (0,0,0), (self.radio+6, self.radio-4), eye_radius)
        pygame.draw.line(self.base_image, (0,0,0), (self.radio-10, self.radio-10), (self.radio-2, self.radio-6), 2)
        pygame.draw.line(self.base_image, (0,0,0), (self.radio+2, self.radio-6), (self.radio+10, self.radio-10), 2)
        pygame.draw.arc(self.base_image, (0,0,0), (self.radio-8, self.radio+2, 16, 10), math.pi, 2*math.pi, 2)

        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))

        self.vx = random.choice([-2, 2])  # más rápido
        self.vy = 0
        self.en_suelo = False
        self.angulo = 0

        self.spawn_x = x
        self.patrulla_min_x = min_x if min_x is not None else x - 180
        self.patrulla_max_x = max_x if max_x is not None else x + 180

        self.dano = dano
        self.cooldown_ataque = 0
        self.vida = random.randint(2, 4)

    def update(self, jugador, plataformas, enemigos):
        centro = self.rect.centerx

        if abs(centro - jugador.rect.centerx) < 220:

            if centro < jugador.rect.centerx:
                self.rect.x += 2.2
                self.angulo -= 6
            else:
                self.rect.x -= 2.2
                self.angulo += 6

            if self.en_suelo and random.random() < 0.02:
                self.vy = -10
        else:

            self.rect.x += self.vx
            if self.vx > 0:
                self.angulo -= 4
            else:
                self.angulo += 4

            if self.rect.left < self.patrulla_min_x or self.rect.right > self.patrulla_max_x:
                self.vx *= -1

            if random.random() < 0.005:
                self.vx *= -1

            if self.en_suelo and random.random() < 0.01:
                self.vy = -8

        self.vy += GRAVEDAD
        self.rect.y += self.vy
        self.en_suelo = False
        for p in plataformas:
            if self.rect.colliderect(p.rect):
                if self.vy > 0:
                    self.rect.bottom = p.rect.top
                    self.vy = 0
                    self.en_suelo = True
                elif self.vy < 0:
                    self.rect.top = p.rect.bottom
                    self.vy = 0

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

        self.image = pygame.transform.rotate(self.base_image, self.angulo)
        self.rect = self.image.get_rect(center=self.rect.center)

    def intentar_atacar(self, jugador):
        if self.cooldown_ataque > 0:
            return False
        if self.rect.colliderect(jugador.rect):
            jugador.recibir_danio(self.dano)
            self.cooldown_ataque = FPS // 2
            return True
        return False

    def draw_barra_vida(self, pantalla, camara_x):
        ancho = self.rect.width
        alto = 5
        max_vida = 4
        relleno = max(0, int((self.vida / max_vida) * ancho))
        x = self.rect.x - camara_x
        y = self.rect.y - 8
        pygame.draw.rect(pantalla, ROJO, (x, y, relleno, alto))
        pygame.draw.rect(pantalla, BLANCO, (x, y, ancho, alto), 1)

    def muere(self):
        self.kill()
