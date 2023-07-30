import pygame
import pymunk
import pymunk.pygame_util

import time
import json

import world
import entity


'''
Scene:
Class for containing a scene

args:
    map: world object containing dynamic objects
    UI: dict containing all UI objects

'''
class Scene:
    def __init__(self, screen, map, space, **kwargs):
        self.screen = screen
        self.map = map
        self.space = space
        self.UI = entity.EntityGroup()
        
        self.key_callback = kwargs.get('key_callback', None) #function to be called when the user presses a key
        
        self.max_fps = kwargs.get('max_fps', 120)
        self.do_physics = kwargs.get('do_physics', False)
        self.physics_step = kwargs.get('physics_step', 1.0/480.0)
        self.background_color = kwargs.get('background_color', (0,0,0))
        
        self.clock = pygame.time.Clock()
        
        self.fps = 120
        self.frame_period = 1/120
    
    def add_UI(self, UI_element):
        self.UI.add(UI_element)
    
    '''
    Advance one frame and do physics
    
    args:
        startloop: time at the start of the loop (for calculating time delta)
    '''
    def tick(self, startloop):
        self.map.map.fill(self.background_color)
        
        if self.key_callback:
            keys = pygame.key.get_pressed()
            self.key_callback(keys, self.frame_period)
        
        #update entitiy animations
        self.map.draw(self.screen, self.frame_period)
        
        #draw UI
        self.UI.draw(self.screen)
        
        #do physics
        self.clock.tick(120)
        
        #"oversample" physics
        #we do this because pymunk is happiest when the physics time step is constant
        #this does result in more time error when FPS is higher, but it's an acceptable trade
        if self.do_physics:
            for i in range(int(self.frame_period/self.physics_step)):
                self.map.physics()
                self.space.step(self.physics_step) #more steps for lower FPS
        
        #calculate period for next frame
        self.fps = int(1.0/(time.time() - startloop + 0.000001))
        self.frame_period = 1.0/self.fps

'''
Class for managing scenes and their transitions
'''
class SceneManager: #TODO: use function pointer to contain a dict of scenes
    def __init__(self, screen):
        self.screen = screen
