import pygame
import pymunk

import entity

class World:
    def __init__(self, size, **kwargs):
        self.map = pygame.Surface(size)
        self.camera = kwargs.get('camera', (size[0] //2, size[1] // 2))
        self.entities = entity.EntityGroup()
        self.focus = None
    
    def add(self, entity):
        self.entities.add(entity)
        
    def translate(self, offset):
        for entity in self.entities:
            entity.translate(offset)
        
    def draw(self, screen):
        screen_rect = screen.get_rect()
        map_rect = self.map.get_rect()
        
        if self.focus:
            entity_pos = self.entities.sprites()[self.focus].body.position
            entity_radius = self.entities.sprites()[self.focus].radius
            
            if (entity_pos[0] - entity_radius < 0): #out of bounds to the left
                #self.translate((map_rect.width//2, 0))
                exit()
            elif (entity_pos[0] + entity_radius > map_rect.width): #out of bounds to the right
                #self.translate((-1 * map_rect.width//2, 0))
                exit()
            elif (entity_pos[1] - entity_radius < 0): #out of bounds below
                #self.translate((0, map_rect.height//2))
                exit()
            elif (entity_pos[1] + entity_radius > map_rect.height): #out of bounds above
                #self.translate((0, -1 * map_rect.height//2))
                exit()
            
            
            self.camera = self.entities.sprites()[self.focus].body.position
        
        view_x = self.camera[0] - (screen_rect.width // 2)
        view_y = self.camera[1] - (screen_rect.height // 2)
        
        if view_x < 0:
            view_x = 0
        if view_y < 0:
            view_y = 0
        
        self.entities.update()
        self.entities.draw(self.map)
        screen.blit(self.map, (0,0), (view_x, view_y, screen_rect.width, screen_rect.height))