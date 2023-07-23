import pygame
import pymunk 
import pymunk.pygame_util

import sys
import os
import time
import random
import math

#engine imports
import entity
import world
import utils


class Needles:
    def __init__(self, position, gauge_path, pointer_path, num_pointers, pointer_separation, **kwargs):
        self.position = position
        self.group = entity.EntityGroup()
        self.group.add(entity.StaticObject(gauge_path, position=position))
        self.num_pointers = num_pointers
        self.gauge_range = kwargs.get('gauge_range', 3.6)
        
        for i in range(self.num_pointers):
            self.group.add(entity.StaticObject(pointer_path, position=(position[0] - pointer_separation + (i * pointer_separation), position[1])))
    
    '''
    Selects surface to draw to and gauge value from 0 - 100
    '''
    def draw(self, surface, positions):
        for i in range(self.num_pointers):
            self.group.sprites()[i + 1].angle = math.radians((positions[i] * self.gauge_range) - ((self.gauge_range/3.6) * 180))
        self.group.draw(surface)

def collide(arbiter, space, data):
    print("collided")
    print(data)
    return True

def main(argv):
    pygame.init()
    
    pygame.display.set_caption("Airshipping")
    window = pygame.display.set_mode([640,360], pygame.SCALED | pygame.RESIZABLE)
    screen = pygame.Surface((640,360))

    space = pymunk.Space()
    space.gravity = (0,400)
    #handler = space.add_collision_handler(1,1)
    #handler.begin = collide
    
    consolas = pygame.font.SysFont("Consolas", 14)

    map = world.World((1000, 1000))
    
    #init UI steam gauges
    gauges = Needles((320,35), os.path.join('Art', 'gauges.png'), os.path.join('Art', 'pointer.png'), 3, 74, gauge_range = 2.9)
    engine_gauge = Needles((590,310), os.path.join('Art', 'engine_order_2.png'), os.path.join('Art', 'bigpointer.png'), 1, 0, gauge_range = 2.65)
    lift_gauge = Needles((505,322), os.path.join('Art', 'lift_gauge.png'), os.path.join('Art', 'pointer.png'), 1, 0, gauge_range = 2.65)
    
    #map entities
    map.add(entity.Entity(space, os.path.join('Art', 'floor.png'),
                          body_type = pymunk.Body.KINEMATIC))
    map.entities.sprites()[-1].set_position((500,900))
    
    map.add(entity.Ship(space, os.path.join('Art', 'blimp.png'), 
                            spritesize=(99,47), matrixsize=(2,2), 
                            mass = 1000, moment = 10000, body_type = pymunk.Body.DYNAMIC,
                            hitbox=os.path.join('Art','blimp.box'),
                            animation_step=6,
                            center_of_gravity = (0,20),
                            center_of_buoyancy = (0,-20)))
    map.entities.sprites()[-1].set_position((500,820))
    
    map.add(entity.Entity(space, os.path.join('Art', 'wall.png'),
                        mass = 0,  body_type = pymunk.Body.DYNAMIC))
    map.entities.sprites()[-1].set_position((616,770))
    
    cannon = entity.Weapon(space, os.path.join('Art', 'cannon.png'), os.path.join('Art', 'small_cannonball.png'), map, 
                           origin = (2,0), projectile_mass = 10000, recoil = 5e6)
    map.add(cannon)
    map.entities.sprites()[1].attatch_weapon(cannon)

    
    
    for i in range(20):
        map.add(entity.Entity(space, os.path.join('Art', 'box.png'),
                        mass = 1,  body_type = pymunk.Body.DYNAMIC))
        map.entities.sprites()[-1].set_position((600, 890 - (i * 15)))
    
    map.focus = 1

    run = True
    fps = 0
    frame = 0
    clock = pygame.time.Clock()
    #lift = 1000000
    while run:
        startloop = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        #game code start here
                
        map.map.fill((170,255,255))
        
        keys = pygame.key.get_pressed()
        map.entities.sprites()[1].move(keys)
        
        map.draw(screen)
        
        frames = consolas.render("{} fps".format(round(fps,1)),True, (255,255,255))
        position = consolas.render("{:0.2f}, {:0.2f}".format(map.entities.sprites()[1].body.position[0], 
                                                        map.entities.sprites()[1].body.position[1]), True, (255,255,255))
        screen.blit(frames, (5, 5))
        screen.blit(position, (5, 30))
        
        buoy = 100 * utils.percent((1200000,1500000),map.entities.sprites()[1].buoyancy)
        alt = 100 * utils.percent((1000,0),map.entities.sprites()[1].body.position[1])
        engine = (map.entities.sprites()[1].power / 4000) + 50
        print(map.entities.sprites()[1].power)
        
        gauges.draw(screen, [50,50,alt])
        engine_gauge.draw(screen, [engine])
        lift_gauge.draw(screen, [buoy])
        
        #this goes last in the loop
        window.blit(pygame.transform.scale(screen, window.get_rect().size), (0, 0))
        pygame.display.flip()
        clock.tick(120)
        space.step(1.0/120.0)
        
        fps = int(1/(time.time() - startloop + 0.000001))
        frame += 1
    
if __name__ == "__main__":
    main(sys.argv)