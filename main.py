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
import scene

def main(argv):
    pygame.init()
    
    pygame.display.set_caption("Airshipping")
    window = pygame.display.set_mode([640,360], pygame.SCALED | pygame.RESIZABLE)
    screen = pygame.Surface((640,360))
    consolas = pygame.font.SysFont("Consolas", 14)

    space = pymunk.Space()
    space.gravity = (0,400)

    map = world.World((10000, 1000), space)
    
    main_scene = scene.Scene(screen, map, space, 
                             do_physics = True,
                             background_color = (170,255,255))

    #init UI steam gauges
    temp_gauge = entity.Gauge(os.path.join('Art', 'temp_gauge.png'), os.path.join('Art', 'pointer.png'), position=(245,35), gauge_range = 2.9)
    fuel_gauge = entity.Gauge(os.path.join('Art', 'fuel_gauge.png'), os.path.join('Art', 'pointer.png'), position=(320,35), gauge_range = 2.9)
    alt_gauge = entity.Gauge(os.path.join('Art', 'alt_gauge.png'), os.path.join('Art', 'pointer.png'), position=(395,35), gauge_range = 2.9)
    
    lift_gauge = entity.Gauge(os.path.join('Art', 'lift_gauge.png'), os.path.join('Art', 'pointer.png'), position=(135,322), gauge_range = 2.65)
    engine_gauge = entity.Gauge(os.path.join('Art', 'engine_order_2.png'), os.path.join('Art', 'bigpointer.png'), position=(50,310), gauge_range = 2.65)
    
    main_scene.add_UI(temp_gauge)
    main_scene.add_UI(fuel_gauge)
    main_scene.add_UI(alt_gauge)
    main_scene.add_UI(lift_gauge)
    main_scene.add_UI(engine_gauge)
    
    #map entities
    map.add(entity.Entity(space, os.path.join('Art', 'floor.png'),
                          body_type = pymunk.Body.KINEMATIC,
                          position = (500,900)))
    
    ship = entity.load_entity(os.path.join('Assets\Player_Ship', 'blimp.info'), space, position = (500,820))
    map.add(ship)
    main_scene.key_callback = ship.move
    
    cannon = entity.load_entity(os.path.join('Assets\Cannon_1', 'cannon.info'), space, map = map)
    map.add(cannon)
    ship.attatch_weapon(cannon)
    
    map.add(entity.Entity(space, os.path.join('Art', 'wall.png'),
                        density = 10,  body_type = pymunk.Body.DYNAMIC,
                        position = (616,770)))
    
    for i in range(20):
        map.add(entity.Entity(space, os.path.join('Art', 'box.png'),
                        density = 1,  body_type = pymunk.Body.DYNAMIC,
                        position = (600, 890 - (i * 15))))
    
    map.focus = 1
    
    run = True
    while run:
        startloop = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        #update gauges
        fuel_gauge.needle_position = ship.fuel
        alt_gauge.needle_position = 100 * utils.percent((1000,0), ship.body.position[1])
        lift_gauge.needle_position = 100 * utils.percent((1200000,1500000), ship.buoyancy)
        engine_gauge.needle_position = (ship.power / 4000) + 50
        
        #game info text rendering
        frames = consolas.render("{} fps".format(round(main_scene.fps,1)),True, (255,255,255))
        position = consolas.render("{:0.2f}, {:0.2f}".format(ship.body.position[0], ship.body.position[1]), 
                                                             True, (255,255,255))
        screen.blit(frames, (5, 5))
        screen.blit(position, (5, 30))
        
        #draw window
        window.blit(pygame.transform.scale(screen, window.get_rect().size), (0, 0))
        pygame.display.flip()
        
        #tick (THIS GOES LAST)
        main_scene.tick(startloop)
        
    
if __name__ == "__main__":
    main(sys.argv)