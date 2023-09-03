import pygame
import pygame.image
import pymunk
import pymunk.pygame_util

from pathlib import Path
import typing
import numpy as np
import math
import json

import utils
import os
import time
import copy
import csv

REFERENCE_PERIOD = 1.0/120.0

'''
GameObject:
Implements animation from files
Inherits from: pygame's sprite class

args:
    image: pygame surface object for sprite
kwargs:
    spritesize: tuple or array describing the dimensions of the sprite, defaults to the size of the whole image
    matrixsize: size of the animation matrix, defaults to 1x1 (no animation)
    framerate: fps of the animation
'''
class GameObject(pygame.sprite.Sprite):
    def __init__(self, image: pygame.surface, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        
        self.world = None
        self.ID = None #unique int to world that gets assigned when object is added
        
        self.image = image
        self.frame = 0
        self.subframe = 0
        self.framerate = kwargs.get('framerate', 60)
        self.frame_sequence = kwargs.get('frame_sequence', None)
        self.animate = True
        
        #set to spritesheet size of 1 by default
        self.spritesize = kwargs.get('spritesize', None)
        if not self.spritesize:
            self.spritesize = self.image.get_size()
            
        self.matrixsize = kwargs.get('matrixsize', None)
        if not self.matrixsize:
            self.matrixsize = (1,1)
        
        self.surface = pygame.Surface(self.spritesize).convert_alpha() #must preserve an undisturbed copy for rotations
        self.rect = self.surface.get_rect()
        
        self.screen_position = (0,0) #position of the object in the player's view (set externally)
        
        self.set_sprite_index(0) #init to zero
    
    '''
    Helper function, sets index of the sprite animation based on self.matrixsize
    
    args:
        index: index of the animation to set to
    '''
    def set_sprite_index(self, index: int):
        self.surface.fill((0,0,0,0)) #set transparent
        x = (index % self.matrixsize[0]) * self.spritesize[0] #get horizontal location of sprite
        y = (index // self.matrixsize[0]) * self.spritesize[1] #get vertical
        self.surface.blit(self.image, (0,0), (x, y, self.spritesize[0], self.spritesize[1]))
    
    '''
    Updates the sprite by incrementing it to the next animation frame
    Call this in the GRAPHICS loop
    
    args:
        period: period between frames
    '''
    def update(self, period):
        self.subframe += period
        if (self.subframe >= (1.0/self.framerate)): #keep animation consistent across fps
            self.subframe = 0
        
            if self.animate == True:
                if not self.frame_sequence:
                    self.frame += 1
                    if (self.frame) < self.matrixsize[0] * self.matrixsize[1]:
                        self.set_sprite_index(self.frame)
                    else:
                        self.set_sprite_index(0)
                        self.frame = 0
                else: #if frame sequence
                    self.set_sprite_index(self.frame_sequence[self.frame])
                    
                    if self.frame >= len(self.frame_sequence) - 1:
                        self.frame = 0
                    else:
                        self.frame += 1
                    
            elif self.animate == False:
                self.set_sprite_index(0)
                self.frame = 0
    
    '''
    Update function to be called during every physics cycle, does nothing by default
    Call this in the PHYSICS loop
    '''
    def physics_update(self):
        return None

'''
StaticObject:
Class for handling non-physics objects such as backgrounds and UI elements
Inherits from: GameObject

args:
    image: pygame surface object for sprite
kwargs:
    position: position on screen of the object
    angle: angle of the object
'''
class StaticObject(GameObject):
    def __init__(self, image: pygame.surface, **kwargs):
        GameObject.__init__(self, image, **kwargs)
        self.position = kwargs.get('position', (0,0))
        self.angle = kwargs.get('angle', 0)
    
    '''
    Draws the object to the screen
    
    args:
        surface: pygame surface to draw to
    '''
    def draw(self, surface: pygame.surface):
        self.rect.topleft = (self.position[0] - self.rect.width // 2, self.position[1] - self.rect.height // 2)
        
        if (self.angle == 0):
            surface.blit(self.surface, self.rect.topleft)
        else: #rotate and blit if angle != 0 (this is actually better than storing a rotated version persistantly)
            rotated_surface = pygame.transform.rotate(self.surface, math.degrees(-1* self.angle))
            new_rect = rotated_surface.get_rect(center = self.surface.get_rect(topleft = self.rect.topleft).center)
            surface.blit(rotated_surface, new_rect.topleft)

'''
Gauge:
Class for steam gauges

args:
    image: pygame surface for gauge
    needle: pygame surface for needle
'''
class Gauge(StaticObject):
    def __init__(self, image: pygame.surface, needle: pygame.surface, **kwargs):
        StaticObject.__init__(self, image, **kwargs)
        self.needle = StaticObject(needle, position = self.position)
        self.gauge_range = kwargs.get('gauge_range', 3.6)
        
        self.needle_position = kwargs.get('needle_position', 0)
        
    def draw(self, surface):
        StaticObject.draw(self, surface)
        self.needle.angle = math.radians((self.needle_position  * self.gauge_range) - ((self.gauge_range/3.6) * 180))
        self.needle.draw(surface)

'''
Button:
Class for UI buttons

args:
    image: pygame surface object for button

kwargs:
    callback: function to be executed when button is pressed
'''
class Button(StaticObject):
    def __init__(self, image: pygame.surface, **kwargs):
        StaticObject.__init__(self, image, **kwargs)
        self.callback = None
        self.pressed = False
        
    def set_callback(self, callback, *args):
        self.callback = callback
        self.callback_args = args
        
    '''
    Determine if mouse is inside button and highlight if so
    '''
    def draw(self, surface):
        if utils.in_rect(pygame.mouse.get_pos(), self.rect): #highlight on hover
            self.set_sprite_index(1)
            
            left, middle, right = pygame.mouse.get_pressed()
            if left:
                self.pressed = True
                if self.callback:
                    self.callback(self.callback_args)
            else:
                self.pressed = False
        else:
            self.set_sprite_index(0)
            self.pressed = False
            
        StaticObject.draw(self, surface)

'''
Entity:
Class for handling physics objects with pymunk integration
Inherits from: GameObject

args:
    space: pymunk space that the object exists in
    image: pygame surface object for sprite
kwargs:
    hitbox: path to .json file containing object's hitbox
    shape: string defining the shape of the object (defaults to a box if no file or shape arg is given)
    collision_type: NO IDEA WHAT THIS IS LOL I WROTE THIS A YEAR AGO
    density: object density for physics simulation
    elasticity: object elasticity for physics simulation
    friction: object friction for physics simulation
    position: position of the object
    velocity: velocity of the object
'''
class Entity(GameObject):
    def __init__(self, space: pymunk.Space, image: pygame.surface, **kwargs):
        GameObject.__init__(self, image, **kwargs)
        
        self.radius = self.rect.height // 2
        if self.rect.width >= self.rect.height:
            self.raduis = self.rect.width // 2

        self.box = None        
        self.body = pymunk.Body(0, 0, body_type = kwargs.get('body_type', pymunk.Body.DYNAMIC)) #DO NOT let user set mass or moment
        
        self.center_of_gravity = kwargs.get('center_of_gravity', (0,0))
        
        #determine hitboxes and moments
        if (kwargs.get('hitbox', None)): #load custom hitbox from json ((0,0) is topleft, not center)
            with open(kwargs.get('hitbox', None)) as f:
                data = json.load(f)
                size = data['size']
                vertices = []
                for vertex in data['vertices']: #offset to center
                    vertices.append([vertex[0] - size[0]//2, vertex[1] - size[1]//2])
                
                self.box = pymunk.Poly(self.body, vertices)
                
                if self.body.moment == 0: #auto-calc moment if not provided by user
                    self.body.moment = pymunk.moment_for_poly(mass = self.body.mass,
                                                              vertices = vertices,
                                                              offset = self.center_of_gravity)
                
        elif (kwargs.get('shape', None) == 'circle'):                
            self.box = pymunk.Circle(self.body, self.radius)
            
            if self.body.moment == 0: #auto-calc moment if not provided by user
                self.body.moment = pymunk.moment_for_circle(mass = self.body.mass,
                                                            inner_radius = 0,
                                                            outer_radius = self.radius)
        else:
            self.box = pymunk.Poly.create_box(self.body, (self.rect.width, self.rect.height))
        
            if self.body.moment == 0: #auto-calc moment if not provided by user
                self.body.moment = pymunk.moment_for_box(mass = self.body.mass,
                                                         size = (self.rect.width, self.rect.height))
        
        self.box.density = kwargs.get('density', 1)
        self.box.collision_type = kwargs.get('collision_type', 1) 
        self.box.elasticity = kwargs.get('elasticity', 0.1)
        self.box.friction = kwargs.get('friction', 0.5)
        self.body.position = kwargs.get('position', (0,0))
        self.body.velocity = kwargs.get('velocity', (0,0))
        
        self.hp = kwargs.get('hp', 100)
        self.max_hp = self.hp
        
        self.space = space
        
        if space:
            space.add(self.body, self.box)
    
    '''
    Destructor
    '''
    '''
    def __del__(self):
        self.space.remove(self.body)
    '''
    
    '''
    Set position of the object (this can maybe be removed)
    
    args:
        coords: tuple defining position to move to
    '''
    def set_position(self, coords: tuple[int,int]):
        self.body.position = coords
        self.body.velocity = (0, 0)
    
    '''
    Translate object
    
    args:
        offset: tuple defining the movement offset
    '''
    def translate(self, offset: tuple[int,int]):
        self.set_position((self.body.position[0] + offset[0], self.body.position[1] + offset[1]))
    
    '''
    Draws the object to the screen
    
    args:
        surface: pygame surface to draw to
    '''
    def draw(self, drawsurface: pygame.surface):
        #pygame draws from topleft while pymunk draws from center    
        self.rect.topleft = (self.body.position[0] - self.rect.width // 2, self.body.position[1] - self.rect.height // 2)
        
        if (self.body.angle == 0):
            drawsurface.blit(self.surface, self.rect.topleft)
        else: #rotate and blit if angle != 0 (this is actually better than storing a rotated version persistantly)
            rotated_surface = pygame.transform.rotate(self.surface, math.degrees(-1* self.body.angle))
            new_rect = rotated_surface.get_rect(center = self.surface.get_rect(topleft = self.rect.topleft).center)
            drawsurface.blit(rotated_surface, new_rect.topleft)

    def __str__(self):
        return("pos:{} vel:{} cg:{}".format(self.body.position, self.body.velocity, self.body.center_of_gravity))

'''
Weapon:
Class defining equippable weapons
Inherits from: Entity

args:
    space: pymunk space that the object exists in
    image: pygame surface object for sprite
    projectile_filepath: path to projectile file
kwargs:
    origin: object origin for attatching to a vehicle thru a pymunk joint (tuple)
    cooldown: time between firings
    projectile_velocity: velocity of the projectile
    projectile_density: density of the projectile
    recoil: firing recoil force 
'''
class Weapon(Entity):
    def __init__(self, space: pymunk.Space, image: pygame.surface, projectile_filepath: Path, **kwargs):
        Entity.__init__(self, space, image, **kwargs)
        
        self.projectile_filepath = projectile_filepath
        
        self.last_fired = 0
        
        self.origin = kwargs.get('origin', (0,0))
        self.cooldown = kwargs.get('cooldown', 1)
        self.projectile_velocity = kwargs.get('projectile_velocity', 500)
        self.projectile_density = kwargs.get('projectile_density', 250)
        self.recoil = kwargs.get('recoil', 500000)
        self.projectile_collision_type = kwargs.get('projectile_collision_type', 1)
        
    '''
    Shoot the cannon
    '''
    def fire(self):
        if (time.time() - self.last_fired >= self.cooldown):
            self.last_fired = time.time()
            
            L = -self.origin[0] + self.rect.width #get offset from mounting point
            
            self.world.add(Entity(self.space, load_image(self.projectile_filepath),
                            density = self.projectile_density, 
                            body_type = pymunk.Body.DYNAMIC, 
                            shape = 'circle',
                            position = (self.body.position[0] + (L * math.cos(self.body.angle)), 
                                        self.body.position[1] + (L * math.sin(self.body.angle))),
                            velocity = (self.projectile_velocity * math.cos(self.body.angle), 
                                        self.projectile_velocity * math.sin(self.body.angle)),
                            collision_type = self.projectile_collision_type)) #projectile collision type
            
            self.body.apply_force_at_local_point(force = (-self.recoil, 0), 
                                                 point = (L, 0)) #NOTE: force applied is local to body, not world. angle compensation is not needed
            
'''
Ship:
Class defining airship objects
Inherits From: Entity

args:
    space: pymunk space that the object exists in
    image: pygame surface object for sprite
kwargs:
    buoyancy: buoyancy of the ship
    center_of_gravity: relative location of the center of gravity
    center_of_buoyancy: relative location of the center of buoyancy
    max_power: maximum power of ship's engine
    turning: damping constant for pitching, higher = less power (BAD NAME, SHOULD CHANGE)
    fuel: amount of fuel onboard (0-100 nominally)
    
    alt_P: Proportional term for altitude PID algorithm
    alt_I: Integral term for altitude PID algorithm
    alt_D: Derivative term for altitude PID algorithm
    
    NPC: Boolean describing if the ship is an NPC or Player
'''
class Ship(Entity):
    def __init__(self, space: pymunk.Space, image: pygame.surface, **kwargs):
        Entity.__init__(self, space, image, **kwargs)

        #ship physics
        self.min_buoyancy = kwargs.get('min_buoyancy', 1e6)
        self.max_buoyancy = kwargs.get('max_buoyancy', 2e6)
        self.buoyancy = self.min_buoyancy + (self.max_buoyancy - self.min_buoyancy) / 2 #middle ground
        
        self.body.center_of_gravity = kwargs.get('center_of_gravity', (0, 0))
        self.center_of_buoyancy = kwargs.get('center_of_buoyancy', (0,0))
        self.max_power = kwargs.get('max_power', 200000)
        self.turning = kwargs.get('turning', 8)
        self.fuel = kwargs.get('fuel', 100)
        self.power = 0
        
        #weapon
        self.hardpoint_position = (22,20) #relative position of the weapon hardpoint
        self.joint = None
        self.cannon = None
        self.cannon_motor = None #motor for moving cannon
        
        #for PID
        #altitude
        self.alt_P = kwargs.get('alt_P', 1)
        self.alt_I = kwargs.get('alt_I', 0)
        self.alt_D = kwargs.get('alt_D', 0)
        
        self.PID_alt_setpoint = 0
        
        self.prev_alt_error = 0
        self.alt_error_sum = 0
        
        #position
        self.pos_P = kwargs.get('pos_P', 1)
        self.pos_I = kwargs.get('pos_I', 0)
        self.pos_D = kwargs.get('pos_D', 0)
        
        self.PID_pos_setpoint = 0
        
        self.prev_pos_error = 0
        self.pos_error_sum = 0
        
        #attributes
        self.NPC = kwargs.get('NPC', False)
        self.navigate = kwargs.get('navigate', False) #do PID or not
        self.target_ID = None #ID of target to pathfind to
        
        self.autopilot = False #allow altitude hold if true
        self.flipped = False #facing to the right (False) or left (True)
        
        #flipping
        self.original_image = self.image
        self.original_hardpoint = self.hardpoint_position
    
    '''
    Move ship by keypress
    
    args:
        keys: pygame scancodes
    '''
    def move(self, keys: pygame.key.ScancodeWrapper, period): #TODO, divorce period from this
        if not self.NPC:
            cg = self.body.center_of_gravity
            
            fuel_drain = 0.01
            
            if keys[pygame.K_q]:
                self.body.apply_force_at_local_point(force=(0, -self.max_power/self.turning), point=(cg[0]+30, 0))
                self.body.apply_force_at_local_point(force=(0, self.max_power/self.turning), point=(cg[0]-30, 0))
            if keys[pygame.K_e]:
                self.body.apply_force_at_local_point(force=(0, self.max_power/self.turning), point=(cg[0]+30, 0))
                self.body.apply_force_at_local_point(force=(0, -self.max_power/self.turning), point=(cg[0]-30, 0))
            if keys[pygame.K_w]:
                if not self.autopilot:
                    if self.buoyancy < self.max_buoyancy and self.fuel > 0:
                        self.buoyancy += 1000 * (period / REFERENCE_PERIOD) #adjust for framerate
                        self.fuel -= fuel_drain * (period / REFERENCE_PERIOD) #drain fuel when adjusting buoyancy
                else:
                    if (self.PID_alt_setpoint > 0):
                        self.PID_alt_setpoint -= 5 * (period / REFERENCE_PERIOD)
            if keys[pygame.K_s]:
                if not self.autopilot:
                    if self.buoyancy >= self.min_buoyancy and self.fuel > 0:
                        self.buoyancy -= 1000 * (period / REFERENCE_PERIOD)
                        self.fuel -= fuel_drain * (period / REFERENCE_PERIOD)
                else:
                    if (self.PID_alt_setpoint < 1000):
                        self.PID_alt_setpoint += 5 * (period / REFERENCE_PERIOD)
            
            #throttle
            if keys[pygame.K_a]: #throttle back
                if self.power > -self.max_power:
                    self.power -= 1600 * (period / REFERENCE_PERIOD)
                '''
                if (self.power > -self.max_power):
                    self.power -= 1600 * (period / REFERENCE_PERIOD)
                '''
            elif keys[pygame.K_d]: #throttle forward
                if self.power < self.max_power:
                    self.power += 1600 * (period / REFERENCE_PERIOD)
                '''
                if (self.power < self.max_power):
                    self.power += 1600 * (period / REFERENCE_PERIOD)
                '''
            else:
                if self.power > 0:
                    self.power -= 1600
                    if self.power < 1600:
                        self.power = 0
                    
                elif self.power < 0:
                    self.power += 1600
                    if self.power > -1600:
                        self.power = 0
                
            if keys[pygame.K_x]: #cut throttle
                self.power = 0
            
            #weapon motion controls
            if self.cannon:
                if keys[pygame.K_k]: #shoot
                    self.shoot()
            
                if keys[pygame.K_l]: #move cannon down
                    self.cannon_motor.rate = -1 #these rates are constant since they're processed in physics
                elif keys[pygame.K_j]: #move cannon up
                    self.cannon_motor.rate = 1 
                else: #don't move
                    self.cannon_motor.rate = 0
    
    '''
    Command the ship to hover at a certian altitude
    
    args:
        max_altitude: maximum altitude in the space (for determining error)
        t: time step (for derivative case)
    '''
    def PID_altitude(self, max_altitude, t):
        neutral_buoyancy = self.min_buoyancy + (self.max_buoyancy - self.min_buoyancy) / 2
        error = -(self.PID_alt_setpoint - self.body.position[1])/max_altitude
        
        k_P = self.alt_P * error
        k_I = self.alt_I * self.alt_error_sum
        k_D = self.alt_D * ((error - self.prev_alt_error)/t)
        
        self.buoyancy = neutral_buoyancy + (neutral_buoyancy * (k_P + k_I + k_D))
        
        if (self.buoyancy > self.max_buoyancy):
            self.buoyancy = self.max_buoyancy
        elif (self.buoyancy < self.min_buoyancy):
            self.buoyancy = self.min_buoyancy
        
        self.prev_alt_error = error
        self.alt_error_sum += error
        
        #print("kP={}, kI={}, kD={}".format(k_P,k_I,k_D))
    
    '''
    Command the ship to move to a certian position
    '''
    def PID_position(self, max_distance, t):
        error = (self.PID_pos_setpoint - self.body.position[0])/max_distance
    
        k_P = self.pos_P * error
        k_I = self.pos_I * self.pos_error_sum
        k_D = self.pos_D * ((error - self.prev_pos_error)/t)
        
        self.power = self.max_power * (k_P + k_I + k_D)
        
        if (self.power > self.max_power):
            self.power = self.max_power
        elif (self.power < -self.max_power):
            self.power = -self.max_power
            
        self.prev_pos_error = error
        self.pos_error_sum += error
        
        #print("kP={}, kI={}, kD={}".format(k_P,k_I,k_D))
    
    '''
    Write PID altitude data to csv file
    '''
    def write_PID_alt_csv(self, filename):
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([self.world.physics_step_count, self.PID_alt_setpoint, self.body.position[1], self.buoyancy])
    
    '''
    Helper function to get the number of objects between self and target
    '''
    def num_intersections(self, target_pos, ignore):
        m = utils.slope(self.body.position, target_pos)
        b = self.body.position[1] - m * self.body.position[0] #solve for intercept
        
        intersections = 0
            
        for object in self.world.entities.sprites():
            if (object.ID not in ignore): #filter out objects to ignore
                i_point = utils.intersects(m, b, object.rect)
                if i_point:
                    if utils.x_between(self.body.position, target_pos, i_point): #if intersection point is between self and target
                        intersections += 1
                        #print("Intersects {} at {}".format(object.filename, utils.intersects(m, b, object.rect)))
                        
        return intersections
    
    '''
    Generate position solution for pathfinding to target
    
    args:
        target_ID: ID of the entity to pathfind to
    '''
    def pathfind(self, target_ID):
        POS_INCREMENT = 10
    
        target = self.world.get_entity(target_ID)
        if target:
            pathfinding_pos = target.body.position
        else:
            self.navigate = False #terminate pathfinding if target died
            return
        
        if (self.NPC and target):
            intersections = self.num_intersections(pathfinding_pos, [self.ID, target_ID])
            
            if intersections > 0: #if there is not a direct path to the target, search above 
                while intersections != 0 and pathfinding_pos[1] > POS_INCREMENT: #search above until there is a clear path
                    pathfinding_pos = (pathfinding_pos[0], pathfinding_pos[1] - POS_INCREMENT) 
                    intersections = self.num_intersections(pathfinding_pos, [self.ID, target_ID])
                    
            if intersections > 0: #if searching above failed
                pathfinding_pos = (pathfinding_pos[0], target.body.position[1])
                while intersections != 0 and pathfinding_pos[1] < (self.world.map.get_height() - POS_INCREMENT):
                    pathfinding_pos = (pathfinding_pos[0], pathfinding_pos[1] + POS_INCREMENT) 
                    intersections = self.num_intersections(pathfinding_pos, [self.ID, target_ID])
            
            self.PID_alt_setpoint = pathfinding_pos[1]
            self.PID_pos_setpoint = pathfinding_pos[0]
            
            if (self.body.position[0] > target.body.position[0] and self.flipped == False):
                self.flip()
            elif (self.body.position[0] < target.body.position[0] and self.flipped == True):
                self.flip()
    
    '''
    Update the position of the ship
    
    args:
        period: period between frames
    '''
    def update(self, period): #do entity motion
        Entity.update(self, period)
        
        if self.fuel <= 0:
            self.fuel = 0
            self.power = 0
            self.animate = False
    
    '''
    Do ship physics
    '''
    def physics_update(self): #must update physics each time since constant forces are applied
        if (self.NPC and self.navigate): #do PID if NPC
            self.PID_altitude(self.world.map.get_height(), self.world.physics_step)
            self.PID_position(self.world.map.get_width(), self.world.physics_step)
        elif (not self.NPC and self.autopilot):
            self.PID_altitude(self.world.map.get_height(), self.world.physics_step)
    
        if (self.body.angular_velocity != 0): #rotation damping
            self.body.angular_velocity /= 1.01
        
        buoyancy = self.buoyancy
        
        cb = self.center_of_buoyancy
        cg = self.body.center_of_gravity
        
        angle = self.body.angle
        drag_coeff = 0.5 * 1.2 * 50
        drag = (drag_coeff * -self.body.velocity[0] * abs(self.body.velocity[0]), 
                drag_coeff * -self.body.velocity[1] * abs(self.body.velocity[1]))
        
        self.body.apply_force_at_local_point(force=(-buoyancy * math.cos(-angle + 2*math.pi/4), -buoyancy * math.sin(-angle + 2*math.pi/4)), point=(cb[0], cb[1])) #lift
        self.body.apply_force_at_local_point(force=drag, point = cg) #drag
        
        if (abs(self.power) > self.max_power/10 or self.NPC): #do engine
            self.body.apply_force_at_local_point(force=(self.power,0), point=(cg[0], cg[1]))
        
            if self.fuel > 0:
                self.fuel -= 1e-8 * abs(self.power) #drain fuel
        
    '''
    Attatch a cannon to the craft's hardpoint
    
    args:
        weapon: weapon object to attatch
    '''
    def attatch_weapon(self, weapon: Weapon):
        weapon.set_position((self.body.position[0] + self.hardpoint_position[0] - weapon.origin[0], 
                             self.body.position[1] + self.hardpoint_position[1] - weapon.origin[1]))
        
        self.cannon = weapon
        self.joint = pymunk.constraints.PivotJoint(self.body, self.cannon.body,
                                              self.hardpoint_position, (-self.cannon.origin[0], -self.cannon.origin[1]))
        self.space.add(self.joint)
        
        self.cannon_motor = pymunk.constraints.SimpleMotor(self.body, self.cannon.body, 0)
        self.space.add(self.cannon_motor)

    '''
    Shoot the cannon
    '''
    def shoot(self):
        if self.cannon:
            self.cannon.fire()
    
    '''  
    Flip
    '''
    def flip(self):
        if not self.flipped:
            self.image = pygame.transform.flip(self.original_image, True, False)
            self.hardpoint_position = (-self.original_hardpoint[0], self.original_hardpoint[1])
            self.flipped = True
        else:
            self.image = self.original_image
            self.hardpoint_position = self.original_hardpoint
            self.flipped = False
            
        new_vertices = []
            
        for vertex in self.box.get_vertices():
            new_vertices.append((-vertex.x, vertex.y))
        
        #flip bounding box
        density = self.box.density #preserve material properties
        collision_type = self.box.collision_type
        elasticity = self.box.elasticity
        friction = self.box.friction
        position = self.body.position
        velocity = self.body.velocity
        center_of_gravity = self.body.center_of_gravity
        
        self.space.remove(self.body)
        self.space.remove(self.box)
        
        self.box = None
        self.body = pymunk.Body(0, 0, body_type = pymunk.Body.DYNAMIC)
        self.box = pymunk.Poly(self.body, new_vertices)
        self.body.moment = pymunk.moment_for_poly(mass = self.body.mass,
                                                      vertices = new_vertices,
                                                      offset = self.center_of_gravity)

        self.body.velocity = velocity
        self.box.collision_type = collision_type
        self.box.elasticity = elasticity
        self.box.friction = friction
        self.box.density = density
        
        self.space.add(self.body, self.box)
        
        self.body.center_of_gravity = center_of_gravity #must set after addition to space
        self.body.position = position #must set after adjusting CG

        if self.cannon: #this kind of sucks but it works
            cannon_copy = copy.copy(self.cannon)
            self.world.add(cannon_copy)

            self.world.entities.remove(self.cannon)
            self.space.remove(self.cannon.body)
            self.space.remove(self.cannon_motor)
            self.space.remove(self.joint)
            
            cannon_copy.space = self.space
            self.space.add(cannon_copy.body)
            self.attatch_weapon(cannon_copy)
            self.cannon.body.angle = 3.14159 - self.cannon.body.angle #mirror about y axis
        
    '''
    Handle collisions and deal damage
    '''
    def collision_handler(self, arbiter, space, data):
        mag_impulse = math.sqrt(arbiter.total_impulse[0] ** 2 + arbiter.total_impulse[1] ** 2)
        if mag_impulse > 10000: #filter out things like rubbing
            damage = (0.5 * mag_impulse)/self.body.mass
        else:
            damage = 0
            
        self.hp -= damage
        print("hp:{} impulse{}".format(self.hp, mag_impulse))
        return True

'''
Invisible barrier for physics
'''
class Barrier:
    def __init__(self, size, location):
        self.body = pymunk.Body(0, 0, body_type = pymunk.Body.KINEMATIC)
        self.box = pymunk.Poly.create_box(self.body, size)
        
'''
EntityGroup:
Class for storing entities in one location
Inherits from: pygame's sprite class

args:
    *sprites: all sprites to be stored in the class
'''
class EntityGroup(pygame.sprite.Group):
    def __init__(self, *sprites):
        pygame.sprite.Group.__init__(self, *sprites)
    
    '''
    Draws the object to the screen
    
    args:
        surface: pygame surface to draw to
    '''
    def draw(self, surface):
        for sprite in self.sprites():
            sprite.draw(surface)

'''
Load image from file and return
'''
def load_image(filepath):
    return pygame.image.load(filepath).convert_alpha()

'''
Load entity from file and return it

args:
    filepath: path to file for entity
    space: pymunk space
'''
def load_entity(filepath: Path, space, **kwargs):
    original_directory = os.getcwd()
    os.chdir(os.path.dirname(filepath)) #change current working directory

    with open(os.path.basename(filepath)) as f:
        entity_data = json.load(f)
    
    if entity_data['type'] == 'Ship':
        object = Ship(space, load_image(entity_data['image_filename']), **entity_data, **kwargs)
    elif entity_data['type'] == 'Weapon':
        entity_data['projectile_filepath'] = os.path.join(os.path.dirname(filepath), entity_data['projectile_filepath']) #hacky fix so we have the full directory
        object = Weapon(space, load_image(entity_data['image_filename']), **entity_data, **kwargs)
    else:
        object = Entity(space, load_image(entity_data['image_filename']), **entity_data, **kwargs)
    
    os.chdir(original_directory) #reset directory
    return object
    
'''
Merge two entities into one

args:
    space: space to add merged entity to
    entity1: first entitiy to merge
    entity2: second entity to merge
    direction: direction to merge in (x or y)
'''
def merge(space, entity1, entity2, direction, **kwargs): #TODO: make this work with animations
    if direction == 'y':
        im1 = pygame.image.tobytes(entity1.image, 'RGBA')
        im2 = pygame.image.tobytes(entity2.image, 'RGBA')
        size = (entity1.image.get_width(), entity1.image.get_height() + entity2.image.get_height())
        new_image = pygame.image.frombytes(im1 + im2, size, 'RGBA')
    elif direction == 'x':
        im1 = pygame.image.tobytes(entity1.image, 'RGBA')
        im2 = pygame.image.tobytes(entity2.image, 'RGBA')
        size = (entity1.image.get_width() + entity2.image.get_width(), entity1.image.get_height())
        
        img_bytes = utils.interleave(im1, im2, entity1.image.get_width() * 4, entity2.image.get_width() * 4)
        new_image = pygame.image.frombytes(img_bytes, size, 'RGBA')
    else:
        raise ValueError

    new_entity = Entity(space, new_image, position = entity1.body.position, **kwargs)
    
    if entity1.space:
        entity1.space.remove(entity1.body) #remove parents from physics space
        entity1.space = None
    
    if entity2.space:
        entity2.space.remove(entity2.body)
        entity2.space = None
    
    return new_entity
    
'''
Merge tile with itself n times
'''
def merge_n(space, entity, count, direction, **kwargs):
    new_entity = entity
    
    for i in range(count):
        new_entity = merge(space, entity, new_entity, direction, **kwargs)
        
    return new_entity
    
'''
Tile an object but do not merge
'''
def tile_n(map, count, direction, space, image, **kwargs):
    
    for i in range(count):
        tile = Entity(space, image, **kwargs)
        
        if direction == 'y':
            tile.body.position = (tile.body.position[0], tile.body.position[1] - (count * tile.image.get_width() // 2) + (i * tile.image.get_width()))
        elif direction == 'x':
            tile.body.position = (tile.body.position[0] - (count * tile.image.get_height() // 2) + (i * tile.image.get_height()), tile.body.position[1])
        else:
            raise ValueError
        
        map.add(tile)