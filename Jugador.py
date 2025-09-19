from Configuraciones import * 
from ArbolBST import ArbolBST
from Mensaje import * 
import pygame
import os 


class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Animaciones
        self.anim_walk = cargar_animacion("Personajes_juego_EDD2/Walk", (40,52))
        self.anim_death = cargar_animacion("Personajes_juego_EDD2/Death", (40,52))

        self.frame_index = 0
        self.image = self.anim_walk[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Velocidades
        self.vx = 0
        self.vy = 0
        self.speed = VELOCIDAD_JUGADOR
        self.jump_power = POTENCIA_SALTO

        # Estado
        self.en_suelo = False
        self.vidas = 5
        self.gemas = ArbolBST()
        self.invulnerable_timer = 0
        self.facing = 1
        self.estado = "walk"   # "walk", "death", etc
        self.anim_timer = 0
        self.puntos = 0



    def update(self, plataformas):
        # --- Movimiento (aw/d) ---
        keys = pygame.key.get_pressed()
        self.vx = 0
        if keys[pygame.K_a]:
            self.vx = -self.speed
            self.facing = -1
        elif keys[pygame.K_d]:
            self.vx = self.speed
            self.facing = 1

        # movimiento horizontal y colisiones
        self.rect.x += self.vx
        for p in plataformas:
            if self.rect.colliderect(p.rect):
                if self.vx > 0:
                    self.rect.right = p.rect.left
                elif self.vx < 0:
                    self.rect.left = p.rect.right

        # gravedad y colisiones verticales
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

        # --- Animación: actualizar índice ---
        self.anim_timer += 1
        if self.anim_timer >= 8:
            self.anim_timer = 0
            if self.estado == "walk":
                self.frame_index = (self.frame_index + 1) % len(self.anim_walk)
            elif self.estado == "death":
                # en death usualmente no loop; ajusta si quieres lo contrario
                self.frame_index = min(self.frame_index + 1, len(self.anim_death)-1)

        # --- Obtener frame base (sin flip) según estado ---
        if self.estado == "walk":
            base = self.anim_walk[self.frame_index]
        else:
            base = self.anim_death[self.frame_index] if self.frame_index < len(self.anim_death) else self.anim_death[-1]

        # --- Aplicar flip pero sin perder la referencia del frame original ---
        if self.facing == -1:
            frame = pygame.transform.flip(base, True, False)
        else:
            frame = base

        # --- Mantener posición del personaje (evita que "flote") ---
        old_midbottom = self.rect.midbottom  # guardamos la posición de los pies
        self.image = frame
        self.rect = self.image.get_rect()
        self.rect.midbottom = old_midbottom

        # --- Invulnerabilidad: parpadeo (overlay) ---
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
            # alternamos cada cierto tick
            if (self.invulnerable_timer // 6) % 2 == 0:
                overlay = self.image.copy()
                # usa BLEND_RGB_ADD para no alterar el canal alfa y evitar "cuadros"
                overlay.fill((*ROJO_CLARO, 0), special_flags=pygame.BLEND_RGB_ADD)
                self.image = overlay
        # fin update



    def saltar(self):
        if self.en_suelo:
            self.vy = -self.jump_power
            self.en_suelo = False

    def recibir_danio(self, cantidad):
        if self.invulnerable_timer > 0:
            return
        self.vidas -= cantidad
        self.invulnerable_timer = FPS
        
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






