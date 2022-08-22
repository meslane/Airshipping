import pygame
import pymunk

from pathlib import Path
import typing
import numpy as np
import math

class Entity(pygame.sprite.Sprite):
    def __init__(self, space, filepath: Path, **kwargs):
        pygame.sprite.Sprite.__init__(self)
    
        self.image = pygame.image.load(filepath).convert_alpha()
        
        #set to spritesheet size of 1 by default
        self.spritesize = kwargs.get('spritesize', None)
        if not self.spritesize:
            self.spritesize = self.image.get_size()
            
        self.matrixsize = kwargs.get('matrixsize', None)
        if not self.matrixsize:
            self.matrixsize = (1,1)
        
        self.surface = pygame.Surface(self.spritesize).convert_alpha() #must preserve an undisturbed copy for rotations
        self.rect = self.surface.get_rect()
        
        self.body = pymunk.Body(kwargs.get('mass', 0), 
                                kwargs.get('moment', 0), 
                                body_type = kwargs.get('body_type'))
        
        self.box = pymunk.Poly.create_box(self.body, (self.rect.width, self.rect.height))
        print(self.box.get_vertices())
        self.box.collision_type = 1 
        space.add(self.body, self.box)
        self.box.density = 0.9
        self.box.elasticity = 0.1
        self.box.friction = 0.4
        
        self.set_sprite_index(0) #init to zero
        
    def set_position(self, coords: tuple[int,int]):
        self.body.position = coords
    
    def translate(self, offset):
        self.set_position((self.body.position[0] + offset[0], self.body.position[1] + offset[1]))
        
    def draw(self, drawsurface: pygame.surface):
        self.rect.topleft = self.body.position
        if (self.body.angle == 0):
            drawsurface.blit(self.surface, self.rect.topleft)
        else: #rotate and blit if angle != 0 (this is actually better than storing a rotated version persistantly)
            rotated_surface = pygame.transform.rotate(self.surface, self.body.angle)
            new_rect = rotated_surface.get_rect(center = self.surface.get_rect(topleft = self.rect.topleft).center)
            drawsurface.blit(rotated_surface, new_rect.topleft)
            pygame.draw.rect(drawsurface, (0, 255, 0), new_rect, 2)
 
        pygame.draw.rect(drawsurface, (255, 0, 0), self.rect, 2)
        
    def center_rotate(self, space, angle: float):
        self.body.angle = angle
        space.reindex_shapes_for_body(self.body) 
        
    def set_sprite_index(self, index: int):
        self.surface.fill((0,0,0,0)) #set transparent
        x = (index % self.matrixsize[0]) * self.spritesize[0] #get horizontal location of sprite
        y = (index // self.matrixsize[0]) * self.spritesize[1] #get vertical
        self.surface.blit(self.image, (0,0), (x, y, self.spritesize[0], self.spritesize[1]))