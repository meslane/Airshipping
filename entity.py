import pygame
from pathlib import Path
import typing
import numpy as np
import math

class vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    #vectors
    def __str__(self):
        return "(x={0},y={1})".format(self.x, self.y)
        
    def __add__(self, n):
        return vec2(self.x + n.x, self.y + n.y)
        
    def __sub__(self, n):
        return vec2(self.x - n.x, self.y - n.y)
        
    def __mul__(self, n):
        return vec2(self.x * n.x, self.y * n.y)
        
    def __truediv__(self, n):
        return vec2(self.x / n.x, self.y / n.y)
        
    def __floordiv__(self, n):
        return vec2(self.x // n.x, self.y // n.y)
        
    def __pow__(self, n):
        return vec2(self.x ** n.x, self.y ** n.y)
    
    #scalars
    def add(self, n):
        return vec2(self.x + n, self.y + n)
        
    def sub(self, n):
        return vec2(self.x - n, self.y - n)
        
    def mul(self, n):
        return vec2(self.x * n, self.y * n)
        
    def div(self, n):
        return vec2(self.x / n, self.y / n)
        
    def floordiv(self, n):
        return vec2(self.x // n, self.y // n)
        
    def pow(self, n):
        return vec2(self.x ** n, self.y ** n)
        
    #additional
    def mag(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
  
def dot(a, b):
    return (a.x * b.x) + (a.y * b.y)

class Entity(pygame.sprite.Sprite):
    def __init__(self, filepath: Path, **kwargs):
        pygame.sprite.Sprite.__init__(self)
    
        self.image = pygame.image.load(filepath).convert_alpha()
        
        #set to spritesheet size of 1 by default
        self.spritesize = kwargs.get('spritesize', None)
        if not self.spritesize:
            self.spritesize = self.image.get_size()
            
        self.matrixsize = kwargs.get('matrixsize', None)
        if not self.matrixsize:
            self.matrixsize = (1,1)
        
        self.physics = kwargs.get('physics', False)
        self.mass = kwargs.get('mass', 1e10)
        self.velocity = vec2(0,0)
        self.angle = 0
        
        self.surface = pygame.Surface(self.spritesize).convert_alpha() #must preserve an undisturbed copy for rotations
        self.rect = self.surface.get_rect()
        
        self.set_sprite_index(0) #init to zero
        
    def set_position(self, coords: tuple[int,int]):
        self.rect.topleft = coords
    
    def translate(self, offset):
        self.set_position((self.rect.topleft[0] + offset[0], self.rect.topleft[1] + offset[1]))
        
    def draw(self, drawsurface: pygame.surface):
        if (self.angle == 0):
            drawsurface.blit(self.surface, self.rect.topleft)
        else: #rotate and blit if angle != 0 (this is actually better than storing a rotated version persistantly)
            rotated_surface = pygame.transform.rotate(self.surface, self.angle)
            new_rect = rotated_surface.get_rect(center = self.surface.get_rect(topleft = self.rect.topleft).center)
            drawsurface.blit(rotated_surface, new_rect.topleft)
        
    def center_rotate(self, angle: float):
        self.angle = angle
        
    def set_sprite_index(self, index: int):
        self.surface.fill((0,0,0,0)) #set transparent
        x = (index % self.matrixsize[0]) * self.spritesize[0] #get horizontal location of sprite
        y = (index // self.matrixsize[0]) * self.spritesize[1] #get vertical
        self.surface.blit(self.image, (0,0), (x, y, self.spritesize[0], self.spritesize[1]))
    
    def update(self):
        if self.physics:
            self.velocity.y = self.velocity.y + (9.8 * (1.0/60.0)) #gravity
            self.translate((self.velocity.x, self.velocity.y))
            
#elastic collision
def collide(a: 'Entity', b: 'Entity'):
    c1 = vec2(a.rect.center[0], a.rect.center[1])
    c2 = vec2(b.rect.center[0], b.rect.center[1])
    v1 = a.velocity 
    v2 = b.velocity
    m1 = a.mass
    m2 = b.mass
    
    a.velocity = v1 - (c1 - c2).mul(((2 * m2)/(m1 + m2)) * (dot(v1 - v2, c1 - c2)/((c1-c2).mag()**2)))
    b.velocity = v2 - (c2 - c1).mul(((2 * m1)/(m1 + m2)) * (dot(v2 - v1, c2 - c1)/((c2-c1).mag()**2)))
    print(a.velocity)
    print(b.velocity)