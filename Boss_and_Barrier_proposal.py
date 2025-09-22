import pygame
from Configuraciones import *


class Jefe(pygame.sprite.Sprite):
    """Clase Jefe (separada de Enemigo).

    - required_power: el poder que el jefe solicita al jugador.
    - reward_power: la gema que entrega al ser satisfecho.

    Método interact(jugador): intenta recibir la gema del jugador. Si el jugador
    tiene la gema (o la gema elegida por sucesor/predecesor), la consume, entrega
    la gema de recompensa al árbol de gemas del jugador y marca al jefe como derrotado.
    Devuelve una tupla (aceptada: bool, mensaje: str).
    """
    def __init__(self, x, y, required_power=120, reward_power=999, w=120, h=160):
        super().__init__()
        self.image = pygame.Surface((w, h))
        # color por defecto — puedes reemplazar esta surface por un sprite más adelante
        self.image.fill((80, 40, 120))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.required_power = int(required_power)
        self.reward_power = int(reward_power)
        self.defeated = False

    def interact(self, jugador):
        """Intentar entregar la gema al jefe.

        Si el jugador tiene la gema exacta requerida, la consume y devuelve la gema
        de recompensa al jugador. Si no tiene la exacta, intenta elegir sucesor o predecesor
        (misma lógica que el Juego original). Si no tiene ninguna gema, devuelve False.
        """
        if self.defeated:
            return (False, 'Jefe ya está satisfecho')

        requerido = self.required_power
        nodo = jugador.gemas.buscar(requerido)
        if nodo:
            # gema exacta
            jugador.gemas.eliminar(requerido)
            jugador.gemas.insertar(self.reward_power, 'Gema del Jefe', self.rect.centerx, self.rect.centery)
            self.defeated = True
            return (True, f'Jefe derrotado: entregaste gema {requerido} y recibiste Gema del Jefe')
        else:
            suc = jugador.gemas.sucesor(requerido)
            pre = jugador.gemas.predecesor(requerido)
            elegido = None
            # elegir la gema más cercana en valor
            if suc and pre:
                elegido = suc if abs(suc[0] - requerido) < abs(pre[0] - requerido) else pre
            else:
                elegido = suc or pre

            if elegido:
                jugador.gemas.eliminar(elegido[0])
                jugador.gemas.insertar(self.reward_power, 'Gema del Jefe', self.rect.centerx, self.rect.centery)
                self.defeated = True
                return (True, f'Jefe aceptó gema {elegido[0]} y entregó Gema del Jefe')
            else:
                return (False, 'Jefe: No tienes gemas para entregarme')

    def draw(self, pantalla, camara):
        pantalla.blit(self.image, camara.aplicar(self.rect))


class ParedDivisible:
    """Una pared que bloquea visualmente y físicamente el paso hasta que se abra.

    Comportamiento:
      - Cuando está cerrada (closed=True) bloquea el paso: colliderect devuelve True.
      - Cuando se inicia la apertura (start_opening), las dos mitades (superior e inferior)
        se separan verticalmente: la superior sube y la inferior baja (como una puerta automática
        pero en horizontal - es decir, la linea de separaciÃ³n es horizontal).
      - La pared se dibuja en coordenadas del mundo (usa camara.aplicar para dibujar).

    Parámetros:
      x: coordenada horizontal (mundo) donde empieza la pared.
      width: ancho de la pared en pixeles (normalmente hasta el portal o hasta el final del pasillo).
      altura: se toma de ALTURA_VENTANA para que cubra toda la pantalla verticalmente.
    """
    def __init__(self, x, width, altura=ALTURA_VENTANA, color=(30, 30, 30), speed=8):
        # la pared ocupará verticalmente toda la ventana por defecto
        self.x = int(x)
        self.width = int(width)
        self.altura = int(altura)
        self.color = color

        mitad = self.altura // 2
        # rects en coordenadas del mundo
        self.top_rect = pygame.Rect(self.x, 0, self.width, mitad)
        self.bottom_rect = pygame.Rect(self.x, mitad, self.width, self.altura - mitad)

        # objetivos para la animación: la parte superior sube 'mitad' y la inferior baja 'mitad'
        self.top_target_y = -mitad
        self.bottom_target_y = self.altura

        self.speed = speed
        self.closed = True
        self.opening = False

    def start_opening(self):
        if not self.opening and self.closed:
            self.opening = True

    def update(self):
        """Animar apertura si corresponde."""
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
        """Devuelve True si el rect del jugador colisiona con alguna mitad y la pared está cerrada."""
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
