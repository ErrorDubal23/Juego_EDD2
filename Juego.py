import pygame 
from Configuraciones import *
from Jugador import Jugador
from GemaSprite import GemaSprite
from Camara import Camara
from Estados import *
import random
from Plataforma import Plataforma
from Cofre import Cofre
from ArbolBST import ArbolBST
from Eventos import ejecutar_eventos_demo
from Vidas import *
from Enemigo import Enemigo
import sys
import os
# C
# reiniciar la partida 
def reiniciar_juego():
    global jugador, all_sprites, enemigos, gemas_sprites, estado
    jugador = Jugador(50, ALTURA_VENTANA - 200)
    # Ejecutar demo de 20 eventos (se muestra en mensajes). Puedes comentar esta línea si no quieres que se ejecute automáticamente.
    ejecutar_eventos_demo(jugador.gemas, agregar_mensaje)
    all_sprites = pygame.sprite.Group(); all_sprites.add(jugador)
    enemigos = pygame.sprite.Group()
    gemas_sprites = pygame.sprite.Group()
    for x,y,poder,nombre in iniciales:
        gemas_sprites.add(GemaSprite(poder, nombre, x, y))
    for x,y,poder,nombre in gemas_extra:
        gemas_sprites.add(GemaSprite(poder, nombre, x, y))
    reset_cofres()
    estado = JUGANDO

# PLATAFORMAS
plataformas = []
grupo_plataformas = pygame.sprite.Group()

# Suelo base (cada 300 px)
for i in range(0, MAPA_ANCHO, 300):
    p = Plataforma(i, ALTURA_VENTANA - 40, 300, 40)
    plataformas.append(p)
    grupo_plataformas.add(p)


pos_plat = [
    (400, 500, 160), (650, 460, 150), (950, 420, 180),

    (1300, 360, 140), (1500, 420, 120), (1700, 380, 160), (1900, 450, 100),

    (2300, 320, 140), (2500, 280, 120), (2700, 340, 100),

    (3000, 500, 400),

    (3600, 460, 120), (3750, 400, 140), (3950, 440, 100), (4150, 360, 140),
    

    (4600, 480, 300),

    (5000, 420, 120), (5200, 360, 160), (5400, 300, 140),
    (5700, 340, 120), (5900, 400, 180),
    (6300, 280, 140), (6600, 320, 120), (6900, 360, 140)
]
for x, y, w in pos_plat:
    p = Plataforma(x, y, w, 20)
    plataformas.append(p)
    grupo_plataformas.add(p)

# COFRES 
cofres = pygame.sprite.Group()
cofres.add(Cofre(950, 380, tipo='gema', valor=30))       # sobre plataforma media
cofres.add(Cofre(2600, 240, tipo='minimo'))              # difícil, requiere saltos
cofres.add(Cofre(3950, 400, tipo='vida', valor=2))       # recompensa en camino
cofres.add(Cofre(6600, 280, tipo='gema', valor=85))      # zona final, complicado
# cofres adicionales: trampa y habilidad
cofres.add(Cofre(2200, 380, tipo='habilidad'))            # da una mejora de velocidad/salto
cofres.add(Cofre(3200, 420, tipo='trampa'))               # quita una gema aleatoria (no la máxima)

# GEMAS (colocadas de forma natural en el recorrido)
gemas_sprites = pygame.sprite.Group()
iniciales = [
    (80, ALTURA_VENTANA - 80, 50, 'Gema del Río'),
    (600, 420, 30, 'Gema del Viento'),
    (1400, 320, 70, 'Gema de la Tierra'),
    (3600, 440, 90, 'Gema del Sol')
]
for x, y, poder, nombre in iniciales:
    g = GemaSprite(poder, nombre, x, y)
    gemas_sprites.add(g)

gemas_extra = [
    (1150, 260, 40, 'Gema de la Luna'),
    (1850, 410, 55, 'Gema del Trueno'),
    (2450, 260, 65, 'Gema del Agua'),
    (3350, 460, 75, 'Gema de la Sombra'),
    (4200, 320, 80, 'Gema del Fuego'),
    (4950, 280, 60, 'Gema del Hielo'),
    (5600, 300, 100, 'Gema Estelar'),
    (6100, 360, 45, 'Gema del Viento II'),
    (7000, 260, 85, 'Gema del Rayo')
]
for x, y, poder, nombre in gemas_extra:
    g = GemaSprite(poder, nombre, x, y)
    gemas_sprites.add(g)

# Verificación: gemas requeridas por cofres
for c in list(cofres):
    if c.tipo == 'gema':
        existe = any(getattr(g, 'poder', None) == c.valor for g in gemas_sprites)
        if not existe:
            gx = max(50, min(MAPA_ANCHO - 50, c.rect.centerx + 40))
            gy = max(50, c.rect.top - 40)
            gemas_sprites.add(GemaSprite(c.valor, f'Gema necesaria {c.valor}', gx, gy))
    elif c.tipo == 'minimo':
        if len(gemas_sprites) == 0:
            gemas_sprites.add(GemaSprite(10, 'Gema mínima automática', 100, ALTURA_VENTANA - 100))


# PORTAL 
portal_rect = pygame.Rect(7600, ALTURA_VENTANA - 200, 120, 160)

# JEFE (bloquea el paso hasta entregar una gema)
boss_rect = pygame.Rect(7000, ALTURA_VENTANA - 200, 120, 160)
boss_required_power = 120   # poder que pide el jefe (puede ajustarse)
boss_defeated = False
boss_reward_power = 999     # gema que entrega el jefe al ser derrotado (máxima)

# ENEMIGOS 
enemigos = pygame.sprite.Group()
spawn_timer = 0

# FONDO
fondo = pygame.image.load("/Users/dubalaguilar/Downloads/Proyecto_EDD2_modificado (2)/imagenes/Background.png").convert()
ancho_fondo, alto_fondo = fondo.get_size()

#  JUGADOR Y CÁMARA 
jugador = Jugador(50, ALTURA_VENTANA - 200)


all_sprites = pygame.sprite.Group(); all_sprites.add(jugador)
camara = Camara()


#  MENSAJES 
mensajes = []  # lista de (texto, tiempo_expiracion)


def agregar_mensaje(texto, duracion=1000):
    mensajes.append((texto, pygame.time.get_ticks() + duracion))

def dibujar_mensajes(pantalla):
    # eliminar expirados
    ahora = pygame.time.get_ticks()
    global mensajes
    mensajes = [(t, exp) for (t, exp) in mensajes if exp > ahora]
    y = 60
    for t, exp in mensajes:
        surf = FUENTE.render(t, True, TEXTO_COLOR)
        pantalla.blit(surf, (12, y)); y += 18

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
    pygame.display.flip()

def dibujar_vidas(pantalla, jugador, cam):
    # dibuja las vidas (corazones) en HUD relativo a camara
    for i in range(jugador.vidas):
        x = 12 + i*22; y = 12
        pantalla.blit(ICONO_VIDA, (x - cam.x, y))


# ESTADOS
estado = MENU

# bucle principal
running = True
clock = pygame.time.Clock()
FPS = 60

def reset_cofres():
    # FALTA ESTO PARA CUANDO SE REINICIA EL JUEGO
    pass

while running:
    
    dt = clock.tick(FPS)
    for x in range(0, MAPA_ANCHO, ancho_fondo):
                for y in range(0, ALTURA_VENTANA, alto_fondo):  
                    PANTALLA.blit(fondo, (x - camara.x, y))
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False

        #  MENU 
        if estado == MENU:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    reiniciar_juego()
                if evento.key == pygame.K_q:
                    running = False

        #  JUGANDO 
        elif estado == JUGANDO:
            

            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_w, pygame.K_SPACE):
                    jugador.saltar()
                if evento.key == pygame.K_j:
                    jugador.ataque_cuerpo(enemigos)
                if evento.key == pygame.K_e:                  
                    jugador_world = jugador.rect 
                    interacted = False
                    for c in cofres:
                        if jugador_world.colliderect(c.rect.inflate(24,24)) and not c.abierto:
                            # Cofres de tipo mínimo / gema / vida (existentes)
                            if c.tipo == 'minimo':
                                mn = jugador.gemas.minimo()
                                if mn:
                                    c.abierto = True; jugador.puntos += 10
                                    agregar_mensaje(f'Cofre abierto con gema mínima {mn[1]}', 1800)
                                else:
                                    agregar_mensaje('No tienes gemas para abrir este cofre', 1800)
                            elif c.tipo == 'gema':
                                if jugador.gemas.buscar(c.valor):
                                    c.abierto = True; jugador.puntos += 20
                                    agregar_mensaje(f'Cofre abierto con gema {c.valor}', 1600)
                                else:
                                    agregar_mensaje(f'Falta gema {c.valor} para abrir el cofre', 2200)
                            elif c.tipo == 'vida':
                                jugador.curar(c.valor); c.abierto = True; jugador.puntos += 15
                            # ofres que dan habilidades (velocidad/salto)
                            elif c.tipo == 'habilidad':
                                # otorgar mejora al jugador 
                                habilidad = 'velocidad' if random.random() < 0.5 else 'salto'
                                if habilidad == 'velocidad':
                                    jugador.speed += 1
                                    agregar_mensaje('Cofre: Velocidad aumentada', 1600)
                                else:
                                    jugador.jump_power += 2
                                    agregar_mensaje('Cofre: Potencia de salto aumentada', 1600)
                                c.abierto = True; jugador.puntos += 12
                            #  cofres trampa quitan una gema aleatoria (excepto la máxima que necesita el portal)
                            elif c.tipo == 'trampa':
                                mx = jugador.gemas.maximo()
                                exclude = mx[0] if mx else None
                                gp = jugador.gemas.gema_aleatoria(exclude=exclude)
                                if gp is None:
                                    agregar_mensaje('Trampa: No hay gema para quitar (solo máxima presente)', 1600)
                                else:
                                    jugador.gemas.eliminar(gp)
                                    agregar_mensaje(f'Trampa: perdiste la gema {gp}', 1600)
                                    jugador.puntos = max(0, jugador.puntos - 5)
                                c.abierto = True
                            interacted = True

                    #  interacción con el jefe 
                    if jugador.rect.colliderect(boss_rect) and not boss_defeated and not interacted:
                        # solicitar gema al jugador
                        requerido = boss_required_power
                        nodo = jugador.gemas.buscar(requerido)
                        if nodo:
                            # se entrega la gema exacta al jefe
                            jugador.gemas.eliminar(requerido)
                            # el jefe entrega una gema poderosa como recompensa
                            jugador.gemas.insertar(boss_reward_power, 'Gema del Jefe', boss_rect.centerx, boss_rect.centery)
                            boss_defeated = True
                            agregar_mensaje(f'Jefe derrotado: entregaste gema {requerido} y recibiste Gema del Jefe', 2200)
                        else:
                            # dar la gema más cercana (sucesor o predecesor)
                            suc = jugador.gemas.sucesor(requerido)
                            pre = jugador.gemas.predecesor(requerido)
                            elegido = None
                            if suc and pre:
                                # elegir la más cercana por diferencia de poder
                                elegido = suc if abs(suc[0]-requerido) <= abs(pre[0]-requerido) else pre
                            else:
                                elegido = suc or pre
                            if elegido:
                                jugador.gemas.eliminar(elegido[0])
                                jugador.gemas.insertar(boss_reward_power, 'Gema del Jefe', boss_rect.centerx, boss_rect.centery)
                                boss_defeated = True
                                agregar_mensaje(f'Jefe aceptó gema {elegido[0]} y entregó Gema del Jefe', 2200)
                            else:
                                agregar_mensaje('Jefe: No tienes gemas para entregarme', 1800)
                        interacted = True
                    # Portal 
                    if jugador.rect.colliderect(portal_rect) and not interacted:
                        mx = jugador.gemas.maximo()
                        if mx:
                            # consumir gema máxima y declarar victoria
                            jugador.gemas.eliminar(mx[0])
                            agregar_mensaje(f'Usaste gema máxima {mx[1]} en el portal. ¡Victoria!', 2500)
                            jugador.puntos += 100
                            estado = GAME_OVER
                        else:
                            agregar_mensaje('Necesitas una gema para usar el portal', 1500)
                if evento.key == pygame.K_ESCAPE:
                    estado = PAUSA

        #  PAUSA 
        elif estado == PAUSA:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    estado = JUGANDO
                if evento.key == pygame.K_m:
                    estado = MENU

        #  GAME OVER 
        elif estado == GAME_OVER:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    reiniciar_juego()
                if evento.key == pygame.K_m:
                    estado = MENU

    
    if estado == MENU:
        dibujar_menu_principal()
        continue
    if estado == PAUSA:
        PANTALLA.fill(FONDO)
        dibujar_pausa()
        continue
    if estado == GAME_OVER:
        dibujar_game_over()
        continue

    
    jugador.update(plataformas)

    # actualizar cámara primero 
    camara.actualizar(jugador.rect)

    # caída fuera del mapa
    if jugador.rect.top > ALTURA_VENTANA + 300:
        agregar_mensaje('Has caído: pierdes una vida', 1500)
        jugador.vidas -= 1
        jugador.rect.topleft = (50, ALTURA_VENTANA - 200); jugador.vy = 0
        if jugador.vidas <= 0:
            estado = GAME_OVER

    DISTANCIA_MIN_ENEMIGOS = 200       # separación mínima entre ellos
    SPAWN_DISTANCIA_EXTRA = 300        # distancia fuera de la cámara donde pueden spawnear
    DESPAWN_DISTANCIA = 800            # si están a más de esto del jugador, se eliminan

    spawn_timer += dt
    if spawn_timer > ENEMY_SPAWN_COOLDOWN and len(enemigos) < MAX_ENEMIGOS_EN_PANTALLA:
        spawn_timer = 0

       
        zonas_spawn = []
        zonas_spawn.append((camara.x - SPAWN_DISTANCIA_EXTRA, camara.x - 50))  # izquierda de cámara
        zonas_spawn.append((camara.x + ANCHO_VENTANA + 50, camara.x + ANCHO_VENTANA + SPAWN_DISTANCIA_EXTRA))  # derecha de cámara

        lado = random.choice(zonas_spawn)
        ex = random.randint(lado[0], lado[1])
        ex = max(0, min(MAPA_ANCHO - 40, ex))  
        ey = ALTURA_VENTANA - 80 

       
        muy_cerca = any(abs(ex - e.rect.x) < DISTANCIA_MIN_ENEMIGOS for e in enemigos)
        if not muy_cerca:
            patr_min = max(0, ex - 120)
            patr_max = min(MAPA_ANCHO, ex + 120)
            e = Enemigo(ex, ey, patr_min, patr_max, dano=random.choice([1,1,2]))
            enemigos.add(e)

    camara_centro = camara.x + ANCHO_VENTANA // 2

    for e in list(enemigos):
        if abs(e.rect.centerx - camara_centro) > DESPAWN_DISTANCIA:
            enemigos.remove(e)



    
    for e in list(enemigos):
        e.update(jugador, plataformas, enemigos)
        if e.rect.top > ALTURA_VENTANA + 300 or e.rect.left < -800 or e.rect.left > MAPA_ANCHO + 800:
            enemigos.remove(e)
            continue

       
        if jugador.rect.colliderect(e.rect) and (jugador.vy > 0 or jugador.rect.centery < e.rect.centery) and (jugador.rect.bottom - e.rect.top) < 22:
            e.muere()
            jugador.vy = -8
            agregar_mensaje('Enemigo aplastado', 1000)
            continue

        # si enemigo ataca devuelve True
        if e.intentar_atacar(jugador):
            # knockback lateral
            if jugador.rect.centerx < e.rect.centerx:
                jugador.rect.x -= 30
            else:
                jugador.rect.x += 30

    # recoger gemas (colisiones mundo)
    for g in list(gemas_sprites):
        if jugador.rect.colliderect(g.rect):
            añadido = jugador.gemas.insertar(g.poder, g.nombre, g.rect.centerx, g.rect.centery)
            if añadido:
                agregar_mensaje(f'Has recogido gema {g.poder} {g.nombre}', 1400)
            else:
                agregar_mensaje(f'Gema {g.poder} ya la tenías', 1200)
            gemas_sprites.remove(g)

    # verificar vida por daños
    if jugador.vidas <= 0:
        agregar_mensaje('Has muerto', 2000)
        try:
            jugador.muere()
        except Exception:
            pass
        estado = GAME_OVER
        continue

    # limitar jugador dentro del mapa
    if jugador.rect.left < 0: jugador.rect.left = 0
    if jugador.rect.right > MAPA_ANCHO: jugador.rect.right = MAPA_ANCHO

    #  DIBUJADO 
 
    for p in grupo_plataformas: PANTALLA.blit(p.image, camara.aplicar(p.rect))
    for c in cofres:
        PANTALLA.blit(c.image, camara.aplicar(c.rect))
        if c.abierto:
            txt = FUENTE.render('Abierto', True, BLANCO)
            PANTALLA.blit(txt, camara.aplicar(c.rect).move(0,-18))
    for g in gemas_sprites: PANTALLA.blit(g.image, camara.aplicar(g.rect))
    # dibujar portal y jefe (bloqueador)
    pygame.draw.rect(PANTALLA, (80,40,120), camara.aplicar(boss_rect)) if not boss_defeated else None
    pygame.draw.rect(PANTALLA, (120,200,240), camara.aplicar(portal_rect))
    for e in enemigos:
        PANTALLA.blit(e.image, camara.aplicar(e.rect))
        try:
            e.draw_barra_vida(PANTALLA, camara.x)
        except Exception:
            pass
    PANTALLA.blit(jugador.image, camara.aplicar(jugador.rect))

    # dibujar_vidas removed: mostrar vidas sólo por texto HUD
    dibujar_mensajes(PANTALLA)

    hud = FUENTE.render(f'Vidas: {jugador.vidas}   Puntos: {jugador.puntos}   Enemigos: {len(enemigos)}', True, BLANCO)
    PANTALLA.blit(hud, (30,30))

    pygame.display.flip()

pygame.quit()
sys.exit()