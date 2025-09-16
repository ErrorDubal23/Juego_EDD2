import pygame

class NodoGema:
    def __init__(self, poder, nombre, x, y):
        self.poder = int(poder)
        self.nombre = nombre
        self.x = x
        self.y = y
        self.left = None
        self.right = None
    def __repr__(self):
        return f'({self.poder}:{self.nombre})'