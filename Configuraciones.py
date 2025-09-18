import pygame
import os 
# ---------------- CONFIGURACIÓN ----------------
ANCHO_VENTANA, ALTURA_VENTANA = 1100, 640
FPS = 60
GRAVEDAD = 0.6
VELOCIDAD_JUGADOR = 3
POTENCIA_SALTO = 12

MAPA_ANCHO = 8000
MARGEN_CAMARA = 220
MAX_ENEMIGOS_EN_PANTALLA = 5
ENEMY_SPAWN_COOLDOWN = FPS * 2

pygame.init()
FUENTE = pygame.font.SysFont('Consolas', 18)
PANTALLA = pygame.display.set_mode((ANCHO_VENTANA, ALTURA_VENTANA))
pygame.display.set_caption('Bosque Ancestral - Versión Completa')
RELOJ = pygame.time.Clock()

# Colores
BLANCO = (255,255,255)
NEGRO = (0,0,0)
ROJO = (220,30,30)
ROJO_CLARO = (255,60,60)
MARRON = (16,18,32)
VERDE = (40,180,100)
FONDO = (20,35,18)
PORTAL_COLOR = (90,10,170)
TEXTO_COLOR = (240,240,240)

# Estados de juego
MENU = 'menu'
JUGANDO = 'jugando'
PAUSA = 'pausa'
GAME_OVER = 'game_over'

import pygame

# Ícono de vida (corazón)

ICONO_VIDA = pygame.Surface((18,18), pygame.SRCALPHA)
pygame.draw.circle(ICONO_VIDA, (220,20,60), (9,6), 6)
pygame.draw.circle(ICONO_VIDA, (220,20,60), (5,6), 6)
pygame.draw.polygon(ICONO_VIDA, (220,20,60), [(2,10),(9,16),(16,10)])

def cargar_animacion(ruta_carpeta, escala=None):
    frames = []
    for nombre in sorted(os.listdir(ruta_carpeta)):
        if nombre.endswith(".png"):
            img = pygame.image.load(os.path.join(ruta_carpeta, nombre)).convert_alpha()
            # recorta bordes transparentes
            recorte = img.get_bounding_rect()
            img = img.subsurface(recorte)
            if escala:
                img = pygame.transform.scale(img, escala)
            frames.append(img)
    return frames
