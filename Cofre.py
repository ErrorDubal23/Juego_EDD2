import pygame, math

class Cofre(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo='gema', valor=None):
        super().__init__()
        self.tipo = tipo
        self.valor = valor
        self.abierto = False
        self.t = 0  

        self.width, self.height = 40, 30
        self.base_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self._dibujar_cofre(self.base_image)

        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))

        self.glow_phase = 0

        glow_size = max(self.width, self.height) * 3
        self.glow = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        cx, cy = glow_size//2, glow_size//2
        for r in range(glow_size//2, 0, -10):
            alpha = max(20, 180 - r*3)
            pygame.draw.circle(self.glow, (255, 255, 150, alpha), (cx, cy), r)
        self.glow_rect = self.glow.get_rect(center=self.rect.center)

    def _dibujar_cofre(self, surface):
        w, h = self.width, self.height

        base_rect = pygame.Rect(0, h//3, w, h*2//3)
        pygame.draw.rect(surface, (139, 69, 19), base_rect)          
        pygame.draw.rect(surface, (100, 50, 15), base_rect, 2)      

        tapa_rect = pygame.Rect(0, 0, w, h//2 + 4)
        pygame.draw.rect(surface, (160, 82, 45), tapa_rect)          
        pygame.draw.arc(surface, (100, 50, 15), tapa_rect, math.pi, 2*math.pi, 3)  

        pygame.draw.line(surface, (220, 200, 80), (w//3, 0), (w//3, h), 3)
        pygame.draw.line(surface, (220, 200, 80), (2*w//3, 0), (2*w//3, h), 3)

        lock_rect = pygame.Rect(w//2 - 4, h//2, 8, 10)
        pygame.draw.rect(surface, (80, 80, 80), lock_rect)
        pygame.draw.circle(surface, (30, 30, 30), lock_rect.center, 2)


    def update(self):
        old_center = self.rect.center  

        if self.abierto:
            self.image = self.base_image.copy()
            self.rect = self.image.get_rect(center=old_center) 
            return
        
        self.t += 0.05
        scale = 1.0 + 0.08 * math.sin(self.t * 2)  
        size = int(self.glow.get_width() * scale)
        glow_scaled = pygame.transform.smoothscale(self.glow, (size, size))

        final = pygame.Surface((size, size), pygame.SRCALPHA)

        glow_rect = glow_scaled.get_rect(center=(size//2, size//2))
        final.blit(glow_scaled, glow_rect)

        cofre_rect = self.base_image.get_rect(center=(size//2, size//2))
        final.blit(self.base_image, cofre_rect)

        self.image = final
        self.rect = self.image.get_rect(center=old_center)









    

    
