from Configuraciones import *

class Camara:
    def __init__(self): self.x = 0
    def aplicar(self, rect): return rect.move(-self.x, 0)
    def actualizar(self, objetivo_rect):
        centro_obj_x = objetivo_rect.centerx
        mitad = ANCHO_VENTANA // 2
        if centro_obj_x - self.x > mitad + MARGEN_CAMARA:
            self.x = min(MAPA_ANCHO - ANCHO_VENTANA, centro_obj_x - (mitad + MARGEN_CAMARA))
        elif centro_obj_x - self.x < mitad - MARGEN_CAMARA:
            self.x = max(0, centro_obj_x - (mitad - MARGEN_CAMARA))