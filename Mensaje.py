import pygame
from Configuraciones import * 
mensajes = []  # lista de (texto, tiempo_expiracion)
def agregar_mensaje(texto, dur_ms):
    mensajes.append((texto, pygame.time.get_ticks() + dur_ms))
def dibujar_mensajes(pantalla):
    ahora = pygame.time.get_ticks()
    # filtrar
    for t, exp in list(mensajes):
        if ahora < exp:
            surf = FUENTE.render(t, True, TEXTO_COLOR)
            pantalla.blit(surf, (ANCHO_VENTANA//2 - surf.get_width()//2, 40))
            break  # mostrar solo el primero (puedes cambiar para stack)
    # eliminar expirados
    while mensajes and mensajes[0][1] <= ahora:
        mensajes.pop(0)
