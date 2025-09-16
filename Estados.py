from Configuraciones import *
# ---------------- ESTADOS Y MENÚ ----------------
estado = MENU

def dibujar_menu_principal():
    PANTALLA.fill(FONDO)
    titulo = pygame.font.SysFont('Consolas', 40).render('BOSQUE ANCESTRAL', True, TEXTO_COLOR)
    sub = FUENTE.render('ENTER: Iniciar   Q: Salir', True, TEXTO_COLOR)
    PANTALLA.blit(titulo, (ANCHO_VENTANA//2 - titulo.get_width()//2, ALTURA_VENTANA//3))
    PANTALLA.blit(sub, (ANCHO_VENTANA//2 - sub.get_width()//2, ALTURA_VENTANA//2))
    pygame.display.flip()

def dibujar_pausa():
    s = pygame.Surface((ANCHO_VENTANA, ALTURA_VENTANA), pygame.SRCALPHA)
    s.fill((0,0,0,150)); PANTALLA.blit(s, (0,0))
    texto = FUENTE.render('PAUSA - R: Reanudar   M: Menú   Q: Salir', True, TEXTO_COLOR)
    PANTALLA.blit(texto, (ANCHO_VENTANA//2 - texto.get_width()//2, ALTURA_VENTANA//2))
    pygame.display.flip()

def dibujar_game_over():
    s = pygame.Surface((ANCHO_VENTANA, ALTURA_VENTANA)); s.fill((10,10,10))
    PANTALLA.blit(s,(0,0))
    t = pygame.font.SysFont('Consolas',34).render('GAME OVER', True, ROJO)
    t2 = FUENTE.render('ENTER: Jugar de nuevo   M: Menú', True, TEXTO_COLOR)
    PANTALLA.blit(t, (ANCHO_VENTANA//2 - t.get_width()//2, ALTURA_VENTANA//3))
    PANTALLA.blit(t2, (ANCHO_VENTANA//2 - t2.get_width()//2, ALTURA_VENTANA//2))