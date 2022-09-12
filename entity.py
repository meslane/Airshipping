import pygame
import pymunk
import pymunk.pygame_util

from pathlib import Path
import typing
import numpy as np
import math
import json

import utils

class GameObject(pygame.sprite.Sprite):
    def __init__(self, filepath: Path, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load(filepath).convert_alpha()
        self.animation_step = kwargs.get('animation_step', 0)
        self.frame = 0
        
        #set to spritesheet size of 1 by default
        self.spritesize = kwargs.get('spritesize', None)
        if not self.spritesize:
            self.spritesize = self.image.get_size()
            
        self.matrixsize = kwargs.get('matrixsize', None)
        if not self.matrixsize:
            self.matrixsize = (1,1)
        
        self.surface = pygame.Surface(self.spritesize).convert_alpha() #must preserve an undisturbed copy for rotations
        self.rect = self.surface.get_rect()
        
        self.set_sprite_index(0) #init to zero
    
    def set_sprite_index(self, index: int):
        self.surface.fill((0,0,0,0)) #set transparent
        x = (index % self.matrixsize[0]) * self.spritesize[0] #get horizontal location of sprite
        y = (index // self.matrixsize[0]) * self.spritesize[1] #get vertical
        self.surface.blit(self.image, (0,0), (x, y, self.spritesize[0], self.spritesize[1]))
    
    def update(self):
        if self.animation_step > 0:
            self.frame += 1
            if (self.frame // self.animation_step) < self.matrixsize[0] * self.matrixsize[1]:
                self.set_sprite_index(self.frame // self.animation_step)
            else:
                self.set_sprite_index(0)
                self.frame = 0

class StaticObject(GameObject):
    def __init__(self, filepath: Path, **kwargs):
        GameObject.__init__(self, filepath, **kwargs)
        self.position = kwargs.get('position', (0,0))
        self.angle = kwargs.get('angle', 0)
    
    def draw(self, surface: pygame.surface):
        self.rect.topleft = (self.position[0] - self.rect.width // 2, self.position[1] - self.rect.height // 2)
        
        if (self.angle == 0):
            surface.blit(self.surface, self.rect.topleft)
        else: #rotate and blit if angle != 0 (this is actually better than storing a rotated version persistantly)
            rotated_surface = pygame.transform.rotate(self.surface, math.degrees(-1* self.angle))
            new_rect = rotated_surface.get_rect(center = self.surface.get_rect(topleft = self.rect.topleft).center)
            surface.blit(rotated_surface, new_rect.topleft)
    
class Entity(GameObject):
    def __init__(self, space: pymunk.Space, filepath: Path, **kwargs):
        GameObject.__init__(self, filepath, **kwargs)
        
        self.radius = self.rect.height // 2
        if self.rect.width >= self.rect.height:
            raduis = self.rect.width // 2

        self.box = None        
        self.body = pymunk.Body(kwargs.get('mass', 0), 
                                kwargs.get('moment', 0), 
                                body_type = kwargs.get('body_type'))
        
        if (kwargs.get('hitbox', None)): #load custom hitbox from json ((0,0) is topleft, not center)
            with open(kwargs.get('hitbox', None)) as f:
                data = json.load(f)
                size = data['size']
                vertices = []
                for vertex in data['vertices']: #offset to center
                    vertices.append([vertex[0] - size[0]//2, vertex[1] - size[1]//2])
                
                self.box = pymunk.Poly(self.body, vertices)
        elif (kwargs.get('shape', None) == 'circle'):                
            self.box = pymunk.Circle(self.body, self.radius)
        else:
            self.box = pymunk.Poly.create_box(self.body, (self.rect.width, self.rect.height))
        
        self.box.collision_type = kwargs.get('collision_type', 1) 
        self.box.density = kwargs.get('density', 1)
        self.box.elasticity = kwargs.get('elasticity', 0.1)
        self.box.friction = kwargs.get('friction', 0.5)
        
        space.add(self.body, self.box)
    
    def set_position(self, coords: tuple[int,int]):
        self.body.position = coords
    
    def translate(self, offset: tuple[int,int]):
        self.set_position((self.body.position[0] + offset[0], self.body.position[1] + offset[1]))
        
    def draw(self, drawsurface: pygame.surface):
        #pygame draws from topleft while pymunk draws from center    
        self.rect.topleft = (self.body.position[0] - self.rect.width // 2, self.body.position[1] - self.rect.height // 2)
        
        if (self.body.angle == 0):
            drawsurface.blit(self.surface, self.rect.topleft)
        else: #rotate and blit if angle != 0 (this is actually better than storing a rotated version persistantly)
            rotated_surface = pygame.transform.rotate(self.surface, math.degrees(-1* self.body.angle))
            new_rect = rotated_surface.get_rect(center = self.surface.get_rect(topleft = self.rect.topleft).center)
            drawsurface.blit(rotated_surface, new_rect.topleft)
            #pygame.draw.rect(drawsurface, (0, 255, 0), new_rect, 2)
        
        #pygame.draw.rect(drawsurface, (255, 0, 0), self.rect, 2)
        
class Ship(Entity):
    def __init__(self, space: pymunk.Space, filepath: Path, **kwargs):
        Entity.__init__(self, space, filepath, **kwargs)
        self.buoyancy = kwargs.get('buoyancy', 1360000)
        self.body.center_of_gravity = kwargs.get('center_of_gravity', (0, 0))
        self.center_of_buoyancy = kwargs.get('center_of_buoyancy', (0,0))
        
    def move(self, keys: pygame.key.ScancodeWrapper):
        power = 200000
        turning = 8
        
        cg = self.body.center_of_gravity
        
        if keys[pygame.K_q]:
            self.body.apply_force_at_local_point(force=(0, -power/turning), point=(cg[0]+30, 0))
            self.body.apply_force_at_local_point(force=(0, power/turning), point=(cg[0]-30, 0))
        if keys[pygame.K_e]:
            self.body.apply_force_at_local_point(force=(0, power/turning), point=(cg[0]+30, 0))
            self.body.apply_force_at_local_point(force=(0, -power/turning), point=(cg[0]-30, 0))
        if keys[pygame.K_w]:
            if self.buoyancy < 1500000:
                self.buoyancy += 1000
        if keys[pygame.K_s]:
            if self.buoyancy >= 1200000:
                self.buoyancy -= 1000
        if keys[pygame.K_a]:
            self.body.apply_force_at_local_point(force=(-power,0), point=(cg[0], cg[1]))
        if keys[pygame.K_d]:
            self.body.apply_force_at_local_point(force=(power,0), point=(cg[0], cg[1]))
        
    def update(self):
        Entity.update(self)
        
        if (self.body.angular_velocity != 0): #rotation damping
            self.body.angular_velocity /= 1.01

        print(self.buoyancy)
        cb = self.center_of_buoyancy
        angle = self.body.angle
        drag_coeff = 0.5 * 1.2 * 50
        drag = (drag_coeff * -self.body.velocity[0] * abs(self.body.velocity[0]), drag_coeff * -self.body.velocity[1] * abs(self.body.velocity[1]))
        self.body.apply_force_at_local_point(force=(-self.buoyancy * math.cos(-angle + 2*math.pi/4), -self.buoyancy * math.sin(-angle + 2*math.pi/4)), point=(cb[0], cb[1]))
        self.body.apply_force_at_local_point(force=drag, point = self.body.center_of_gravity) #drag
        
        print(self.body.velocity)
        
class EntityGroup(pygame.sprite.Group):
    def __init__(self, *sprites):
        pygame.sprite.Group.__init__(self, *sprites)
        
    def draw(self, surface):
        for sprite in self.sprites():
            sprite.draw(surface)