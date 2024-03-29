import pygame
import pymunk
import time
import math
import os
import json
import random

import entity
import game_audio

explosion_colors = [(251,146,43), (79,103,129), (175,191,210)]

'''
Task:
    class containing tasks for scheduling
    
args:
    callback: function to call
    period: period of time between function calls
'''
class Task:
    def __init__(self, callback, period, *args):
        self.callback = callback
        self.period = period
        self.args = args
        
        self.last_run = 0
        
    def run(self):
        self.callback(self.args)

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
        
        self.physics_step_count = 0 #increments every physics step
        
        self.key_callback = kwargs.get('key_callback', None)
        
        self.clock = pygame.time.Clock()
        
        self.fps = 120
        self.frame_period = 1/120
        
        self.next_ID = 0
        
        #do tasks
        self.tasks = []
        self.tasks.append(Task(self.pathfind, 1))
        self.tasks.append(Task(self.cull_dead, 0.05))
        self.tasks.append(Task(self.cull_particles, 0.1))
        
        #collision handlers dict
        self.handlers = {}
    
    '''
    Add an entity to the world
    
    args:
        entity: the entity object to add
    '''
    def add(self, object):
        object.world = self
        object.ID = self.next_ID
        self.next_ID += 1
        self.entities.add(object)
        
        #add collision handler for ship
        if isinstance(object, entity.Ship):
            object.box.collision_type = object.ID
            self.handlers[object.ID] = self.space.add_collision_handler(2, object.ID)
            self.handlers[object.ID].post_solve = object.collision_handler
        
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
    Remove entity from world and space before deleting
    '''
    def kill_entity(self, ID):
        object = self.get_entity(ID)
        
        if isinstance(object, entity.Ship): #spawn frags
            impulse_mag = 0.3e5 #impulse for explosion
        
            game_audio.play_sound('explosion')
        
            for frag in object.frags:
                if object.flipped:
                    new_position = [object.body.position[0] - frag['relative_position'][0], 
                                    object.body.position[1] + frag['relative_position'][1]]
                else:
                    new_position = [object.body.position[0] + frag['relative_position'][0], 
                                    object.body.position[1] + frag['relative_position'][1]]
            
                frag_object = entity.Entity(self.space, entity.load_image(frag['image']),
                                            hitbox = frag['box'],
                                            position = new_position)
                self.add(frag_object)
                                    
                if object.flipped:
                    frag_object.flip()
                
                #explode
                dir_mag = math.sqrt(frag['relative_position'][0] ** 2 + frag['relative_position'][1] ** 2)
                impulse = [(frag['relative_position'][0]/dir_mag) * impulse_mag, 
                           (frag['relative_position'][1]/dir_mag) * impulse_mag]
                
                if object.flipped:
                    impulse[0] *= -1
                
                frag_object.body.apply_impulse_at_local_point(impulse)
                
            for i in range(200):
                p = entity.Particle(self.space, 1, explosion_colors[random.randint(0,2)], -200, 
                position = (object.body.position[0] + random.randint(-10,10),
                            object.body.position[1] + random.randint(-10,10)), 
                lifespan = random.uniform(1,5), 
                velocity = (random.randint(-impulse_mag/200,impulse_mag/200), 
                            random.randint(-impulse_mag/200,impulse_mag/200)))
                self.add(p)
        
            if object.cannon:
                #self.kill_entity(object.cannon.ID)
                self.space.remove(object.cannon_motor)
                self.space.remove(object.joint)
        
        self.space.remove(object.body, object.box)
        self.entities.remove(object)
        
        if ID in self.handlers:
            del self.handlers[ID]
        
        del object
    
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
        
        if self.focus and self.get_entity(self.focus):
            entity_pos = self.get_entity(self.focus).body.position
            entity_radius = self.get_entity(self.focus).radius
            
            self.camera = self.get_entity(self.focus).body.position
        
        #remove out of bounds entities:
        for entity in self.entities:
            entity_pos = entity.body.position
            
            if (entity_pos[0] < 0):
                #self.entities.remove(entity)
                self.kill_entity(entity.ID)
            elif (entity_pos[0] > map_rect.width):
                #self.entities.remove(entity)
                self.kill_entity(entity.ID)
            elif (entity_pos[1] < 0):
                #self.entities.remove(entity)
                self.kill_entity(entity.ID)
            elif (entity_pos[1] > map_rect.height):
                #self.entities.remove(entity)
                self.kill_entity(entity.ID)
        
        view_x = round(self.camera[0]) - (screen_rect.width // 2) #MUST ROUND or it looks jittery
        view_y = round(self.camera[1]) - (screen_rect.height // 2)
        
        if view_x < 0: #don't show an out of bounds area with the camera
            view_x = 0
        if view_y < 0:
            view_y = 0
        if (view_x + screen_rect.width) > self.map.get_width():
            view_x = (self.map.get_width() - screen_rect.width)
        if (view_y + screen_rect.height) > self.map.get_height():
            view_y = (self.map.get_height() - screen_rect.height)
        
        self.entities.update(period)

        self.entities.draw(self.map)        
        screen.blit(self.map, (0,0), (view_x, view_y, screen_rect.width, screen_rect.height)) #draw and center around focus
        self.UI.draw(self.screen)
    
    '''
    Do physics for all entities
    '''
    def physics(self):
        for entity in self.entities:
            entity.physics_update()
    
    '''
    Do pathfinding for all entities
    '''
    def pathfind(self, *args):
        for object in self.entities.sprites(): #pathfind entities
            if isinstance(object, entity.Ship) and object.NPC and object.target_ID:
                object.pathfind(object.target_ID)
    
    '''
    Kill all dead entities
    '''
    def cull_dead(self, *args):
        for object in self.entities.sprites():
            if isinstance(object, entity.Ship) and object.hp <= 0:
                self.kill_entity(object.ID)
    
    
    '''
    Kill all expired particles
    '''
    def cull_particles(self, *args):
        curtime = time.time()
    
        for object in self.entities.sprites():
            if isinstance(object, entity.Particle) and (curtime >= object.birthday + object.lifespan):
                self.kill_entity(object.ID)
    
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
                self.physics_step_count += 1
        
        #scheduler code to run tasks
        for task in self.tasks:
            if startloop - task.last_run >= task.period:
                task.last_run = startloop
                task.run()
        
        #calculate period for next frame
        self.fps = int(1.0/(time.time() - startloop + 1e-8))
        self.frame_period = 1.0/(self.fps + 1e-8)
        
'''
Loads a map of 16x16 tiles from a map file and returns it as a World object
'''
def load_map(filepath, screen, space, **kwargs):
    original_directory = os.getcwd()
    os.chdir(os.path.dirname(filepath)) #change current working directory

    with open(os.path.basename(filepath)) as f:
        map_data = json.load(f)
    
    with open(os.path.basename(map_data["tiledict"])) as f:
        dict_file = json.load(f)
    
    tiledict = {}
    for tile in dict_file:
        pixel_tuple = tuple(map(int, tile.split(', ')))
        tiledict[pixel_tuple] = {'image_file': dict_file[tile]['image_file']} #load image into dict
        
        if 'hitbox' in dict_file[tile]: #load hitbox if specified in tile dict
            tiledict[pixel_tuple]['hitbox'] = dict_file[tile]['hitbox']
        else:
            tiledict[pixel_tuple]['hitbox'] = None
            
        if 'physics' in dict_file[tile]: #load physics settings if specified
            if dict_file[tile]['physics'] == 'dynamic':
                tiledict[pixel_tuple]['physics'] = pymunk.Body.DYNAMIC
            elif dict_file[tile]['physics'] == 'kinematic':
                tiledict[pixel_tuple]['physics'] = pymunk.Body.KINEMATIC
            else:
                tiledict[pixel_tuple]['physics'] = None
        else:
            tiledict[pixel_tuple]['physics'] = pymunk.Body.KINEMATIC
    
    mapimage = entity.load_image(map_data['mapimage']) #load map image to surface
    
    world_map = World(screen, (mapimage.get_width() * 16, mapimage.get_height() * 16), space,
                      background_color = map_data["background_color"], **kwargs) #create world from image dimensions
    
    for y in range(mapimage.get_height()):
        for x in range(mapimage.get_width()):
            pixel = tuple(mapimage.get_at((x,y)))
            if pixel in tiledict: #if this pixel corresponds to an object in the dict, add as object
                if tiledict[pixel]['physics'] == None: #make background object if specified
                    tile_space = None #don't simulate physics
                    tile_bodytype = pymunk.Body.KINEMATIC
                else:
                    tile_space = space
                    tile_bodytype = tiledict[pixel]['physics']
            
                world_map.add(entity.Entity(tile_space, entity.load_image(tiledict[pixel]['image_file']),
                          body_type = tile_bodytype,
                          hitbox = tiledict[pixel]['hitbox'],
                          position = ((x * 16) + 8,(y * 16) + 8))) #load object
    
    os.chdir(original_directory) #reset directory
    return world_map