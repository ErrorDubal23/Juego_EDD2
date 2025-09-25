
from NodoGema import NodoGema
import random

class ArbolBST:

    def __init__(self):
        self.root = None
        self.size = 0

    def insertar(self, poder, nombre, x=None, y=None):
        try:
            poder = int(poder)
        except Exception:
            return False
        node = NodoGema(poder, nombre, x, y)
        if self.root is None:
            self.root = node
            self.size = 1
            return True
        curr = self.root
        parent = None
        while curr:
            parent = curr
            if node.poder == curr.poder:
                return False  # ya existe
            elif node.poder < curr.poder:
                curr = curr.left
            else:
                curr = curr.right
        if node.poder < parent.poder:
            parent.left = node
        else:
            parent.right = node
        self.size += 1
        return True

    def buscar(self, poder):
        try:
            poder = int(poder)
        except Exception:
            return None
        curr = self.root
        while curr:
            if poder == curr.poder:
                return curr
            elif poder < curr.poder:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def _min_node(self, nodo):
        if nodo is None:
            return None
        while nodo.left:
            nodo = nodo.left
        return nodo

    def _max_node(self, nodo):
        if nodo is None:
            return None
        while nodo.right:
            nodo = nodo.right
        return nodo

    def minimo(self):
        n = self._min_node(self.root)
        return (n.poder, n.nombre) if n else None

    def maximo(self):
        n = self._max_node(self.root)
        return (n.poder, n.nombre) if n else None

    def inorden(self):
        res = []
        self._inorden(self.root, res)
        return res

    def _inorden(self, nodo, res):
        if not nodo: return
        self._inorden(nodo.left, res)
        res.append((nodo.poder, nodo.nombre))
        self._inorden(nodo.right, res)

    def preorden(self):
        res = []
        self._preorden(self.root, res)
        return res

    def _preorden(self, nodo, res):
        if not nodo: return
        res.append((nodo.poder, nodo.nombre))
        self._preorden(nodo.left, res)
        self._preorden(nodo.right, res)

    def postorden(self):
        res = []
        self._postorden(self.root, res)
        return res

    def _postorden(self, nodo, res):
        if not nodo: return
        self._postorden(nodo.left, res)
        self._postorden(nodo.right, res)
        res.append((nodo.poder, nodo.nombre))

    def eliminarGemasPostorden(self):
        def postorden_borrar(nodo):
            if nodo is None:
                return
            postorden_borrar(nodo.left)
            postorden_borrar(nodo.right)
            self.eliminar(nodo.poder) 
        
        postorden_borrar(self.root)

    def _to_list_nodes(self, nodo, arr):
        if not nodo: return
        self._to_list_nodes(nodo.left, arr)
        arr.append(nodo)
        self._to_list_nodes(nodo.right, arr)

    def gema_aleatoria(self, exclude=None):       
        if self.size == 0:
            return None
        arr = []
        self._to_list_nodes(self.root, arr)
        if exclude is not None:
            arr = [n for n in arr if n.poder != exclude]
            if not arr:
                return None
        return random.choice(arr).poder

    def eliminar(self, poder):
        try:
            poder = int(poder)
        except Exception:
            return False

        self.root, deleted = self._eliminar_rec(self.root, poder)
        if deleted:
            self.size -= 1
        return deleted

    def _eliminar_rec(self, nodo, poder):
        if nodo is None:
            return nodo, False
        deleted = False
        if poder < nodo.poder:
            nodo.left, deleted = self._eliminar_rec(nodo.left, poder)
        elif poder > nodo.poder:
            nodo.right, deleted = self._eliminar_rec(nodo.right, poder)
        else:
            deleted = True
            # caso 0 o 1 hijo
            if nodo.left is None:
                return nodo.right, True
            elif nodo.right is None:
                return nodo.left, True
            # caso 2 hijos: reemplazar por sucesor 
            succ = self._min_node(nodo.right)
            nodo.poder, nodo.nombre, nodo.x, nodo.y = succ.poder, succ.nombre, succ.x, succ.y
            nodo.right, _ = self._eliminar_rec(nodo.right, succ.poder)
        return nodo, deleted

    def sucesor(self, poder):
        """Devuelve (poder,nombre) del sucesor inmediato de 'poder' o None."""
        # generar lista inorden y buscar el siguiente
        arr = self.inorden()
        for i, (p, n) in enumerate(arr):
            if p == poder:
                if i+1 < len(arr):
                    return arr[i+1]
                else:
                    return None
            if p > poder:
                return (p, n)  # el primero mayor será sucesor
        return None

    def predecesor(self, poder):
        arr = self.inorden()
        prev = None
        for (p, n) in arr:
            if p >= poder:
                return prev
            prev = (p, n)
        return prev
    
    def listar_inventario(self):
        #Devuelve lista de strings con las gemas en orden de poder.
        gemas = self.inorden()
        return [f"Poder {p}: {n}" for p, n in gemas]