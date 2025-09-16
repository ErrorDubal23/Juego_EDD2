
# Eventos.py
# Contiene una lista y función para ejecutar una secuencia de eventos sobre un ArbolBST.
# Está pensada para demostrar las operaciones requeridas (al menos 20 eventos).

import random
def ejecutar_eventos_demo(arbol, agregar_mensaje=None):
    """
    Ejecuta una serie de ~20 eventos sobre el árbol `arbol`.
    Si `agregar_mensaje` está provisto, se llamará para mostrar resultados en pantalla.
    """
    def log(msg):
        if agregar_mensaje:
            agregar_mensaje(msg, 1200)
        else:
            print(msg)

    # 1-6: Insertar varias gemas
    inserts = [
        (15, 'Gema A'), (35, 'Gema B'), (25, 'Gema C'), (5, 'Gema D'),
        (45, 'Gema E'), (30, 'Gema F')
    ]
    for p,n in inserts:
        arbol.insertar(p, n, 0, 0)
        log(f'[Evento] INSERTAR {p} {n}')

    # 7: Buscar (existente y no existente)
    b = arbol.buscar(25)
    log(f'[Evento] BUSCAR 25 -> {"encontrada" if b else "no encontrada"}')

    b2 = arbol.buscar(99)
    log(f'[Evento] BUSCAR 99 -> {"encontrada" if b2 else "no encontrada"}')

    # 8: Eliminar un nodo hoja / interno
    arbol.eliminar(5)
    log('[Evento] ELIMINAR 5')

    # 9: Insertar más
    arbol.insertar(55, 'Gema G', 0, 0); log('[Evento] INSERTAR 55 Gema G')
    arbol.insertar(60, 'Gema H', 0, 0); log('[Evento] INSERTAR 60 Gema H')

    # 11: Mínimo / Máximo
    mn = arbol.minimo(); mx = arbol.maximo()
    log(f'[Evento] MINIMO -> {mn}')
    log(f'[Evento] MAXIMO -> {mx}')

    # 12: Sucesor / Predecesor
    log(f'[Evento] SUCESOR(30) -> {arbol.sucesor(30)}')
    log(f'[Evento] PREDECESOR(30) -> {arbol.predecesor(30)}')

    # 13: Gema aleatoria
    g = arbol.gema_aleatoria()
    log(f'[Evento] GEMA_ALEATORIA -> {g}')

    # 14: Eliminar una gema aleatoria (si existe)
    if g is not None:
        arbol.eliminar(g)
        log(f'[Evento] ELIMINAR gema aleatoria {g}')

    # 15: Insertar y mostrar recorridos
    arbol.insertar(8, 'Gema I', 0, 0); log('[Evento] INSERTAR 8 Gema I')
    log(f'[Evento] INORDEN -> {arbol.inorden()}')
    log(f'[Evento] PREORDEN -> {arbol.preorden()}')
    log(f'[Evento] POSTORDEN -> {arbol.postorden()}')

    # 16: Buscar sucesor/predecesor de un valor no presente (40)
    log(f'[Evento] SUCESOR(40) -> {arbol.sucesor(40)}')
    log(f'[Evento] PREDECESOR(40) -> {arbol.predecesor(40)}')

    # 17-20: Operaciones mixtas para llegar a ~20 eventos
    for i in range(4):
        val = random.randint(1, 120)
        arbol.insertar(val, f'GemaRnd{val}', 0, 0)
        log(f'[Evento] INSERTAR aleatoria {val}')
    log('[Evento] DEMO DE EVENTOS COMPLETADO')
