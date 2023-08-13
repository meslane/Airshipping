import pygame
import pymunk
import time

import entity

'''
World:
    class containing information about the current game world

args:
    screen: pygame surface object to draw to
    size: size of the map (tuple)
    space: pymunk physics space to simulate
kwargs:
    camera: location of the camera in the world
'''
class World:
    def __init__(self, screen, size, space, **kwargs):
        self.screen = screen
        self.map = pygame.Surface(size)
        self.space = space
        
        self.camera = kwargs.get('camera', (size[0] //2, size[1] // 2))
        self.entities = entity.EntityGroup()
        self.UI = entity.EntityGroup()
        self.focus = None
        
        self.max_fps = kwargs.get('max_fps', 120)
        self.do_physics = kwargs.get('do_physics', False)
        self.physics_step = kwargs.get('physics_step', 1.0/480.0)
        self.background_color = kwargs.get('background_color', (0,0,0))
        
        self.key_callback = kwargs.get('key_callback', None)
        
        self.clock = pygame.time.Clock()
        
        self.fps = 120
        self.frame_period = 1/120
        
        self.next_ID = 0
    
    '''
    Add an entity to the world
    
    args:
        entity: the entity object to add
    '''
    def add(self, entity):
        entity.world = self
        entity.ID = self.next_ID
        self.next_ID += 1
        self.entities.add(entity)
        
    '''
    Add a UI element to the world
    
    args:
        UI_element: element to add
    '''
    def add_UI(self, UI_element):
        UI_element.world = self
        UI_element.ID = self.next_ID
        self.next_ID += 1
        self.UI.add(UI_element)
    
    '''
    Search for entities by ID and return a reference if the entity exists
    
    args:
        ID: entity ID number
    '''
    def get_entity(self, ID):
        for entity in self.entities.sprites():
            if entity.ID == ID:
                return entity
                
        return None
    
    '''
    Translate all entities within the world
    
    args:
        offset: offset for the translation (tuple)
    '''
    def translate(self, offset):
        for entity in self.entities:
            entity.translate(offset)
    
    '''
    Determine if a point lies inside a box
    '''
    def in_rect(self, point, rect):
        x_offset = -self.camera[0] + self.screen.get_width()/2
        y_offset = -self.camera[1] + self.screen.get_height()/2

        if (point[0] >= rect[0] + x_offset) and (point[0] <= (rect[0] + rect[2]) + x_offset): #x
            if (point[1] >= rect[1] + y_offset) and (point[1] <= (rect[1] + rect[3]) + y_offset): #y
                return True
        
        return False
    
    '''
    Draw to a pygame surface
    
    args:
        screen: surface to draw to
    '''
    def draw(self, screen, period):
        screen_rect = screen.get_rect()
        map_rect = self.map.get_rect()
        
        if self.focus:
            entity_pos = self.get_entity(self.focus).body.position
            entity_radius = self.get_entity(self.focus).radius
            
            self.camera = self.get_entity(self.focus).body.position
        
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
        self.UI.draw(self.screen)
    
    '''
    Do physics for all entities
    '''
    def physics(self):
        for entity in self.entities:
            entity.physics_update()
            
    '''
    Advance one frame and do physics
    
    args:
        startloop: time at the start of the loop (for calculating time delta)
    '''
    def tick(self, startloop):
        self.map.fill(self.background_color)
        
        if self.key_callback:
            keys = pygame.key.get_pressed()
            self.key_callback(keys, self.frame_period)
        
        #update entitiy animations
        self.draw(self.screen, self.frame_period)
        
        #do physics
        self.clock.tick(120)
        
        #"oversample" physics
        #we do this because pymunk is happiest when the physics time step is constant
        #this does result in more time error when FPS is higher, but it's an acceptable trade
        if self.do_physics:
            for i in range(int(self.frame_period/self.physics_step)):
                self.physics()
                self.space.step(self.physics_step) #more steps for lower FPS
        
        #calculate period for next frame
        self.fps = int(1.0/(time.time() - startloop + 1e-8))
        self.frame_period = 1.0/(self.fps + 1e-8)