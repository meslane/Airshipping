import pygame
import pymunk

import entity

'''
World:
    class containing information about the current game world

args:
    size: size of the map (tuple)
kwargs:
    camera: location of the camera in the world
'''
class World:
    def __init__(self, size, **kwargs):
        self.map = pygame.Surface(size)
        self.camera = kwargs.get('camera', (size[0] //2, size[1] // 2))
        self.entities = entity.EntityGroup()
        self.focus = None
        self.tick = 0
    
    '''
    Add an entity to the world
    
    args:
        entity: the entity object to add
    '''
    def add(self, entity):
        self.entities.add(entity)
     
    '''
    Translate all entities within the world
    
    args:
        offset: offset for the translation (tuple)
    '''
    def translate(self, offset):
        for entity in self.entities:
            entity.translate(offset)
    
    '''
    Draw to a pygame surface
    
    args:
        screen: surface to draw to
    '''
    def draw(self, screen, period):
        screen_rect = screen.get_rect()
        map_rect = self.map.get_rect()
        
        if self.focus:
            entity_pos = self.entities.sprites()[self.focus].body.position
            entity_radius = self.entities.sprites()[self.focus].radius
            
            self.camera = self.entities.sprites()[self.focus].body.position
        
        #remove out of bounds entities:
        for entity in self.entities:
            entity_pos = entity.body.position
            
            if (entity_pos[0] < 0):
                self.entities.remove(entity)
            elif (entity_pos[0] > map_rect.width):
                self.entities.remove(entity)
            elif (entity_pos[1] < 0):
                self.entities.remove(entity)
            elif (entity_pos[1] > map_rect.height):
                self.entities.remove(entity)
        
        view_x = self.camera[0] - (screen_rect.width // 2)
        view_y = self.camera[1] - (screen_rect.height // 2)
        
        if view_x < 0:
            view_x = 0
        if view_y < 0:
            view_y = 0
        
        self.entities.update(period)

        self.entities.draw(self.map)
        screen.blit(self.map, (0,0), (view_x, view_y, screen_rect.width, screen_rect.height))
    
    '''
    Do physics for all entities
    '''
    def physics(self):
        for entity in self.entities:
            entity.physics_update()