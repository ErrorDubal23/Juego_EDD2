# Importar librerías
import pygame 
import json
import sys
import os
import math
import time

# Importar clases propias
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
from Jefe_Muro_Divisible import Jefe, ParedDivisible
from Portal import Portal



# reiniciar la partida 
def reiniciar_juego():
    global jugador, all_sprites, enemigos, gemas_sprites, estado
    jugador = Jugador(50, ALTURA_VENTANA - 200)

    jugador.gemas.eliminarGemasPostorden()
    # Ejecutar los 20 eventos.
    ejecutar_eventos_demo(jugador.gemas, agregar_mensaje)
    # Reiniciar enemigos, gemas y cofres
    all_sprites = pygame.sprite.Group(); all_sprites.add(jugador)
    enemigos = pygame.sprite.Group()
    gemas_sprites = pygame.sprite.Group()
    for x,y,poder,nombre in iniciales:
        gemas_sprites.add(GemaSprite(poder, nombre, x, y))
    for x,y,poder,nombre in gemas_extra:
        gemas_sprites.add(GemaSprite(poder, nombre, x, y))
    reset_cofres()
    # recrear jefe y pared al reiniciar
    crear_boss_y_pared()
    estado = JUGANDO

# Crear grupo de plataformas
plataformas = []
grupo_plataformas = pygame.sprite.Group()

# Suelo base 
for i in range(0, MAPA_ANCHO, 300):
    p = Plataforma(i, ALTURA_VENTANA - 40, 300, 40, transparente=True)
    plataformas.append(p)
    grupo_plataformas.add(p)

# Posiciones de plataformas adicionales
pos_plat = [
    (400, 500, 160), (650, 460, 150), (910, 420, 180),
    (1150, 360, 200), (1410, 420, 180), (1700, 380, 160), (1900, 490, 100),
    (2050, 420, 390), (2500, 310, 120), (2700, 340, 100),
    (3200, 500, 300),
    (3600, 460, 130), (3750, 400, 140), (3950, 440, 100), (4150, 360, 140),
    (4600, 500, 300),
    (5000, 420, 120), (5200, 360, 160), (5400, 300, 140),
    (5650, 340, 120), (5900, 400, 180),
    (6100, 300, 300), (6500, 320, 150), (6770, 360, 140)
]
for x, y, w in pos_plat:
    p = Plataforma(x, y, w, 20, color=(44, 57, 47))  
    plataformas.append(p)
    grupo_plataformas.add(p)

inventario_abierto = False 

SAVE_FOLDER = "saves"

# Posiciones y tipos de cofres 
cofres_iniciales = [
    (950, 390, 'gema', 30),        
    (2550, 280, 'minimo', None),   
    (3950, 410, 'vida', 2),        
    (6500, 290, 'gema', 85),       
    (2200, 390, 'habilidad', None),
    (3350, 470, 'trampa', None)    
]
# Crear grupo de cofres
cofres = pygame.sprite.Group()


# Crear grupo de gemas y sus posiciones por defecto
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

# Verificar gemas requeridas por cofres
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


# Crear Portal 
portal = Portal(7600, ALTURA_VENTANA - 200, 120, 160)

# Características del jefe 
jefe_poder_requerido = 120   # poder que pide el jefe 
jefe_poder_entrega = 999     # gema que entrega el jefe al ser derrotado 

# función para crear el jefe y la pared asociada
def crear_boss_y_pared():
    global boss, wall
    # crear Jefe
    boss = Jefe(6980, ALTURA_VENTANA - 200, required_power=jefe_poder_requerido, reward_power=jefe_poder_entrega, w=120, h=160)
    # crear pared cercad el jefe
    width = max(300, portal.rect.left - boss.rect.right + 50)
    wall = ParedDivisible(x=boss.rect.right + 50, width=width)

# crear al inicio
crear_boss_y_pared()

# Crear grupo de enemigos 
enemigos = pygame.sprite.Group()
spawn_timer = 0

# Crear Fondo

# Carpeta actual del archivo donde está este código
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta a la carpeta de imágenes
IMG_DIR = os.path.join(BASE_DIR, "imagenes")

# Ruta final al archivo
background_path = os.path.join(IMG_DIR, "Background.png")

fondo = pygame.image.load(background_path).convert()
ancho_fondo, alto_fondo = fondo.get_size()

#  Crear Jugador
jugador = Jugador(50, ALTURA_VENTANA - 200)
all_sprites = pygame.sprite.Group(); all_sprites.add(jugador)
# Crear Cámara
camara = Camara()

#  Crear lista de mensajes flotantes 
mensajes = []  

def agregar_mensaje(texto, duracion=1000):
    mensajes.append((texto, pygame.time.get_ticks() + duracion))

def dibujar_mensajes(pantalla):
    # eliminar expirados
    ahora = pygame.time.get_ticks()
    global mensajes
    mensajes = [(t, exp) for (t, exp) in mensajes if exp > ahora]
    
    y = 80
    for t, exp in mensajes:
        surf = FUENTE.render(t, True, TEXTO_COLOR)
        # Calcular X para centrar
        x = (ANCHO_VENTANA // 2) - (surf.get_width() // 2)
        pantalla.blit(surf, (x, y))
        y += 18  

def dibujar_menu_principal():
    PANTALLA.fill(FONDO)

    # animación palpitante
    tiempo = pygame.time.get_ticks() / 300  # velocidad
    factor = 1 + 0.1 * math.sin(tiempo)    

    #  fuente dinamica 
    base_tamano = 60  
    tamano_animado = int(base_tamano * factor)

    fuente_titulo = pygame.font.SysFont('Consolas', tamano_animado, bold=True)  
    titulo = fuente_titulo.render('BOSQUE ANCESTRAL', True, TEXTO_COLOR)

    #  subtitulos fijos 
    fuente_sub = pygame.font.SysFont('Consolas', 24, bold=True)  
    sub = fuente_sub.render('ENTER: Iniciar   Q: Salir', True, TEXTO_COLOR)

    # Posiciones 
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
    # fondo oscuro
    s = pygame.Surface((ANCHO_VENTANA, ALTURA_VENTANA))
    s.fill((10,10,10))
    PANTALLA.blit(s, (0,0))

    # animacion palpitante usando seno del tiempo
    t_actual = time.time()
    scale = 1.0 + 0.1 * math.sin(t_actual * 3)  # 3 = velocidad del pulso

    # Fuente  grande y negrita
    base_size = 80  
    font_big = pygame.font.SysFont('Consolas', int(base_size * scale), bold=True)
    t = font_big.render('GAME OVER', True, ROJO)

    # subtitulo (instrucciones)
    t2 = pygame.font.SysFont('Consolas', 34, bold=True).render(
        'ENTER: Jugar de nuevo   M: Menú', True, TEXTO_COLOR
    )

    # dibujar textos
    PANTALLA.blit(t, (ANCHO_VENTANA//2 - t.get_width()//2, ALTURA_VENTANA//3))
    PANTALLA.blit(t2, (ANCHO_VENTANA//2 - t2.get_width()//2, ALTURA_VENTANA//2))

    pygame.display.flip()


def dibujar_victoria():
    # fondo oscuro
    s = pygame.Surface((ANCHO_VENTANA, ALTURA_VENTANA))
    s.fill((0, 0, 0))  # un tono verdoso oscuro distinto al game over
    PANTALLA.blit(s, (0,0))

    # anaimacion palpitante
    t_actual = time.time()
    scale = 1.0 + 0.1 * math.sin(t_actual * 3)

    # texto principal
    base_size = 80
    font_big = pygame.font.SysFont('Consolas', int(base_size * scale), bold=True)
    t = font_big.render('VICTORIA', True, (50, 220, 50))  # verde brillante

    # subtitulos (instrucciones)
    t2 = pygame.font.SysFont('Consolas', 34, bold=True).render(
        'ENTER: Jugar de nuevo   M: Menú', True, TEXTO_COLOR
    )

    # dibujar textos
    PANTALLA.blit(t, (ANCHO_VENTANA//2 - t.get_width()//2, ALTURA_VENTANA//3))
    PANTALLA.blit(t2, (ANCHO_VENTANA//2 - t2.get_width()//2, ALTURA_VENTANA//2))

    pygame.display.flip()

def dibujar_inventario(superficie, inventario, fuente):
    
    columnas = 4   # cantidad de slots por fila
    slot_size = 100
    padding = 10

    # calcular tamaño del inventario
    filas = (len(inventario) + columnas - 1) // columnas
    ancho = columnas * (slot_size + padding) + padding
    alto = filas * (slot_size + padding) + 60  

    rect = pygame.Rect(ANCHO_VENTANA//2 - ancho//2,
                       ALTURA_VENTANA//2 - alto//2,
                       ancho, alto)
   
    s = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    s.fill((20, 20, 20, 220))  
    superficie.blit(s, rect.topleft)
   
    pygame.draw.rect(superficie, (200, 200, 200), rect, 3, border_radius=12)

    titulo = fuente.render("Inventario", True, (255, 215, 0))
    superficie.blit(titulo, (rect.x + 10, rect.y + 10))

    def draw_text_centered(text, font, color, rect, y_offset=0):
        max_width = rect.width - 8  
        txt_surface = font.render(text, True, color)
   
        while txt_surface.get_width() > max_width and len(text) > 1:
            text = text[:-2] + "…"   
            txt_surface = font.render(text, True, color)

        superficie.blit(txt_surface, (rect.centerx - txt_surface.get_width()//2, rect.y + y_offset))
    
    start_y = rect.y + 50
    for i, linea in enumerate(inventario):
        fila = i // columnas
        col = i % columnas
        x = rect.x + padding + col * (slot_size + padding)
        y = start_y + fila * (slot_size + padding)

        # rectangulo del slot
        slot_rect = pygame.Rect(x, y, slot_size, slot_size)
        pygame.draw.rect(superficie, (50, 50, 50), slot_rect)  
        pygame.draw.rect(superficie, (200, 200, 200), slot_rect, 2)  
      
        try:
            poder, nombre = linea.split(":", 1)
        except ValueError:
            poder, nombre = linea, ""
     
        draw_text_centered(poder.strip(), fuente, (255, 255, 255), slot_rect, 5)   
        draw_text_centered(nombre.strip(), fuente, (150, 200, 255), slot_rect, slot_size//2 - 8)

def guardar_inventario(jugador, slot=1):
    
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

    datos = jugador.gemas.preorden()  
    ruta = os.path.join(SAVE_FOLDER, f"save{slot}.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2)

    agregar_mensaje(f"Inventario guardado en slot {slot}", 1500)


def cargar_inventario(jugador, slot=1):
    
    ruta = os.path.join(SAVE_FOLDER, f"save{slot}.json")
    if not os.path.exists(ruta):
        agregar_mensaje(f"No hay guardado en slot {slot}", 1500)
        return

    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)

    jugador.gemas = ArbolBST()  # reiniciar árbol
    for poder, nombre in datos:
        jugador.gemas.insertar(poder, nombre)

    agregar_mensaje(f"Inventario cargado desde slot {slot}", 1500)

# esto para iniciar en el menú
estado = MENU

# bucle principal
running = True
clock = pygame.time.Clock()
FPS = 60

def reset_cofres():
    global cofres
    cofres.empty()  
    for x, y, tipo, valor in cofres_iniciales:
        cofres.add(Cofre(x, y, tipo=tipo, valor=valor))

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
                mods = pygame.key.get_mods()
                # Para que cuando de shift 1 no se detecte como ! y lo mismo con los demas
                teclas_a_slots = {
                    pygame.K_1: 1,
                    pygame.K_2: 2,
                    pygame.K_3: 3,
                    pygame.K_4: 4,
                    pygame.K_5: 5
                }

                if evento.key in teclas_a_slots:
                    slot = teclas_a_slots[evento.key]

                    if mods & pygame.KMOD_CTRL:
                        cargar_inventario(jugador, slot)
                        print(f"Inventario cargado desde slot {slot}")
                    elif mods & pygame.KMOD_SHIFT:
                        guardar_inventario(jugador, slot)
                        print(f"Inventario guardado en slot {slot}")
                if evento.key == pygame.K_r:
                    jugador.gemas.eliminarGemasPostorden()
                if evento.key == pygame.K_TAB:
                    inventario_abierto = not inventario_abierto
                if evento.key in (pygame.K_w, pygame.K_SPACE):
                    jugador.saltar()
                if evento.key == pygame.K_j:
                    jugador.ataque_cuerpo(enemigos)
                if evento.key == pygame.K_e:                  
                    jugador_world = jugador.rect 
                    interacted = False
                    for c in cofres:
                        if jugador_world.colliderect(c.rect.inflate(24,24)) and not c.abierto:
                            if jugador.gemas.minimo() is None:
                                agregar_mensaje("Necesitas al menos una gema para abrir el cofre", 1800)
                            else:
                                if c.tipo == 'minimo':
                                    mn = jugador.gemas.minimo()
                                    c.abierto = True; jugador.puntos += 10
                                    agregar_mensaje(f'Cofre abierto con gema mínima {mn[1]}', 1800)

                                elif c.tipo == 'gema':
                                    if jugador.gemas.buscar(c.valor):
                                        c.abierto = True; jugador.puntos += 20
                                        agregar_mensaje(f'Cofre abierto con gema {c.valor}', 1600)
                                    else:
                                        agregar_mensaje(f'Falta gema {c.valor} para abrir el cofre', 2200)

                                elif c.tipo == 'vida':
                                    jugador.curar(c.valor); c.abierto = True; jugador.puntos += 15

                                elif c.tipo == 'habilidad':
                                    habilidad = 'velocidad' if random.random() < 0.5 else 'salto'
                                    if habilidad == 'velocidad':
                                        jugador.speed += 1
                                        agregar_mensaje('Cofre: Velocidad aumentada', 1600)
                                    else:
                                        jugador.jump_power += 2
                                        agregar_mensaje('Cofre: Potencia de salto aumentada', 1600)
                                    c.abierto = True; jugador.puntos += 12

                                elif c.tipo == 'trampa':
                                    mx = jugador.gemas.maximo()
                                    exclude = mx[0] if mx else None
                                    gp = jugador.gemas.gema_aleatoria(exclude=exclude)
                                    if gp:
                                        jugador.gemas.eliminar(gp)
                                        agregar_mensaje(f'Trampa: perdiste la gema {gp}', 1600)
                                        jugador.puntos = max(0, jugador.puntos - 5)
                                    else:
                                        agregar_mensaje('Trampa: No hay gema para quitar', 1600)
                                    c.abierto = True
                                else:                                   
                                    c.abierto = True
                                    agregar_mensaje("El cofre está vacío", 1600)

                            interacted = True

                    #  interacción con el jefe 
                    if jugador.rect.colliderect(boss.rect) and not getattr(boss, 'defeated', False) and not interacted:                     
                        mensaje = ''
                        aceptado = False
                        try:
                            aceptado, mensaje = boss.interact(jugador)
                        except Exception:
                            
                            requerido = jefe_poder_requerido
                            nodo = jugador.gemas.buscar(requerido)
                            if nodo:
                                jugador.gemas.eliminar(requerido)
                                jugador.gemas.insertar(jefe_poder_entrega, 'Gema del Jefe', boss.rect.centerx, boss.rect.centery)
                                aceptado = True
                                mensaje = f'Jefe derrotado: entregaste gema {requerido} y recibiste Gema del Jefe'
                            else:
                                suc = jugador.gemas.sucesor(requerido)
                                pre = jugador.gemas.predecesor(requerido)
                                elegido = None
                                if suc and pre:
                                    elegido = suc if abs(suc[0]-requerido) <= abs(pre[0]-requerido) else pre
                                else:
                                    elegido = suc or pre
                                if elegido:
                                    jugador.gemas.eliminar(elegido[0])
                                    jugador.gemas.insertar(jefe_poder_entrega, 'Gema del Jefe', boss.rect.centerx, boss.rect.centery)
                                    aceptado = True
                                    mensaje = f'Jefe aceptó gema {elegido[0]} y entregó Gema del Jefe'
                                else:
                                    aceptado = False
                                    mensaje = 'Jefe: No tienes gemas para entregarme'

                        if aceptado:
                            try:
                                boss.defeated = True
                            except Exception:
                                pass
                            agregar_mensaje(mensaje, 2200)
                            try:
                                wall.start_opening()
                            except Exception:
                                pass

                            boss.defeated = True
                            boss.rect.x = -9999  # lo sacamos de pantalla
                            boss.rect.y = -9999                        
                        else:
                            agregar_mensaje(mensaje, 1800)
                        interacted = True
                    # portal ahora requiere la gema que entrega el jefe 
                    if jugador.rect.colliderect(portal.rect) and not interacted:
                        required = getattr(boss, 'reward_power', jefe_poder_entrega)
                        if jugador.gemas.buscar(required):
                            jugador.gemas.eliminar(required)
                            agregar_mensaje(f'Usaste la Gema del Jefe en el portal. ¡Victoria!', 2500)
                            jugador.puntos += 100
                            estado = VICTORIA
                        else:
                            agregar_mensaje('El portal requiere la Gema del Jefe para activarse', 1500)
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

        #  VICTORIA
        elif estado == VICTORIA:
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
    if estado == VICTORIA:
        dibujar_victoria()
        continue
  
    jugador.update(plataformas)
    gemas_sprites.update()
    cofres.update()

    # actualizar camara primero 
    camara.actualizar(jugador.rect)

    # bloqueo solido para que le jugador no atraviese la pared
    try:
        if wall.closed:
            # si el jugador intenta cruzar la pared, empújalo hacia atrás
            if jugador.rect.right > wall.left:
                jugador.rect.right = wall.left
                try:
                    jugador.vx = 0
                except Exception:
                    pass
    except NameError:
        pass

    # caida fuera del mapa
    if jugador.rect.top > ALTURA_VENTANA + 300:
        agregar_mensaje('Has caído: pierdes una vida', 1500)
        jugador.vidas -= 1
        jugador.rect.topleft = (50, ALTURA_VENTANA - 200); jugador.vy = 0
        if jugador.vidas <= 0:
            estado = GAME_OVER

    DISTANCIA_MIN_ENEMIGOS = 200       # separación minima entre ellos
    SPAWN_DISTANCIA_EXTRA = 300        # distancia fuera de la camara donde pueden spawnear
    DESPAWN_DISTANCIA = 800            # si están a mas de esto del jugador, se eliminan

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
            if jugador.rect.centerx < e.rect.centerx:
                jugador.rect.x -= 30
            else:
                jugador.rect.x += 30

    # recoger gemas 
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

    #  Dibujar todo 
    
    for p in grupo_plataformas: PANTALLA.blit(p.image, camara.aplicar(p.rect))
    for c in cofres:
        PANTALLA.blit(c.image, camara.aplicar(c.rect))
        if c.abierto:
            txt = FUENTE.render('Abierto', True, BLANCO)
            PANTALLA.blit(txt, camara.aplicar(c.rect).move(-19,-18))
    for g in gemas_sprites: PANTALLA.blit(g.image, camara.aplicar(g.rect))

    # dibujar jefe (usa su propio draw)
    if boss and not getattr(boss, 'defeated', False):
        try:
            boss.draw(PANTALLA, camara)
        except Exception:
            pygame.draw.rect(PANTALLA, (80,40,120), camara.aplicar(boss.rect))

    # dibujar portal: cambia apariencia si el jugador tiene la gema del jefe (o si boss ya la entregó)
    portal.update(jugador, boss, jefe_poder_entrega)
    portal.draw(PANTALLA, camara)
    pausa_text = FUENTE.render("[ESC] - Pausa", True, BLANCO)
    PANTALLA.blit(pausa_text, (20, ALTURA_VENTANA - 27))

    for e in enemigos:
        PANTALLA.blit(e.image, camara.aplicar(e.rect))
        try:
            e.draw_barra_vida(PANTALLA, camara.x)
        except Exception:
            pass
    PANTALLA.blit(jugador.image, camara.aplicar(jugador.rect))

    # dibujar_vidas 
    dibujar_mensajes(PANTALLA)

    def dibujar_hud(pantalla, jugador, enemigos):
        #  corazones (vidas) 
        corazon = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(corazon, (255, 0, 0), (9, 10), 8)   # círculo izquierdo
        pygame.draw.circle(corazon, (255, 0, 0), (21, 10), 8)  # círculo derecho
        pygame.draw.polygon(corazon, (255, 0, 0), [(5, 15), (25, 15), (15, 28)])  # triángulo inferior

        for i in range(jugador.vidas):
            pantalla.blit(corazon, (20 + i*35, 20))  # separa los corazones

        #  texto a la derecha 
        texto = FUENTE.render(f'Puntos: {jugador.puntos}   Enemigos: {len(enemigos)}', True, BLANCO)
        pantalla.blit(texto, (ANCHO_VENTANA - texto.get_width() - 20, 25))
        if inventario_abierto:
            inv = jugador.gemas.listar_inventario()
            dibujar_inventario(PANTALLA, inv, FUENTE)
    dibujar_hud(PANTALLA, jugador, enemigos)

    try:
        wall.update()
        wall.draw(PANTALLA, camara)
    except NameError:
        pass

    pygame.display.flip()

pygame.quit()
sys.exit()
