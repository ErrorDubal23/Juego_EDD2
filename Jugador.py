from Configuraciones import * 
from ArbolBST import ArbolBST
from Mensaje import * 
import pygame

class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.base_image = pygame.Surface((36, 48))
        self.base_image.fill(VERDE)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))

        # Velocidades
        self.vx = 0
        self.vy = 0
        # atributos ajustables para habilidades (velocidad / salto)
        self.speed = VELOCIDAD_JUGADOR
        self.jump_power = POTENCIA_SALTO

        # Estado
        self.en_suelo = False   
        self.vidas = 5
        self.gemas = ArbolBST()
        self.puntos = 0
        self.invulnerable_timer = 0
        self.facing = 1  


    def update(self, plataformas):
        keys = pygame.key.get_pressed()
        self.vx = 0
        if keys[pygame.K_a]:
            self.vx = -self.speed
            self.facing = -1
        if keys[pygame.K_d]:
            self.vx = self.speed
            self.facing = 1

        # movimiento horizontal
        self.rect.x += self.vx
        for p in plataformas:
            if self.rect.colliderect(p.rect):
                if self.vx > 0:
                    self.rect.right = p.rect.left
                elif self.vx < 0:
                    self.rect.left = p.rect.right

        # gravedad
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

        # invulnerabilidad parpadeo
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
            if (self.invulnerable_timer // 6) % 2 == 0:
                self.image.fill(ROJO_CLARO)
            else:
                self.image = self.base_image.copy()
        else:
            self.image = self.base_image.copy()

    def saltar(self):
        if self.en_suelo:
            self.vy = -self.jump_power
            self.en_suelo = False

    def recibir_danio(self, cantidad):
        if self.invulnerable_timer > 0:
            return
        self.vidas -= cantidad
        self.invulnerable_timer = FPS
        self.image.fill(ROJO)
        agregar_mensaje(f'Has recibido {cantidad} de daño', 1500)

    def curar(self, cantidad):
        self.vidas += cantidad
        agregar_mensaje(f'Has recuperado {cantidad} vidas', 1500)

    def ataque_cuerpo(self, enemigos):
        golpe_rect = pygame.Rect(
            self.rect.centerx + (self.facing*24),
            self.rect.centery-12, 48, 24
        )
        golpeo = False
        for e in list(enemigos):
            if golpe_rect.colliderect(e.rect):
                e.vida -= 1
                golpeo = True
                if e.vida <= 0:
                    e.muere()
                    agregar_mensaje('Enemigo derrotado', 1000)
                else:
                    agregar_mensaje('Enemigo golpeado', 900)
        if not golpeo:
            agregar_mensaje('Golpe fallido', 600)