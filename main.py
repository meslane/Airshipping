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

def main(argv):
    pygame.init()
    
    pygame.display.set_caption("Airshipping")
    window = pygame.display.set_mode([640,360], pygame.SCALED | pygame.RESIZABLE)
    screen = pygame.Surface((640,360))
    consolas = pygame.font.SysFont("Consolas", 14)

    space = pymunk.Space()
    space.gravity = (0,400)

    '''
    Overworld
    '''
    map = world.World(screen, (10000, 1000), space,
                      do_physics = True,
                      background_color = (170,255,255))
    
    #init UI steam gauges
    temp_gauge = entity.Gauge(os.path.join('Art', 'temp_gauge.png'), os.path.join('Art', 'pointer.png'), position=(245,35), gauge_range = 2.9)
    fuel_gauge = entity.Gauge(os.path.join('Art', 'fuel_gauge.png'), os.path.join('Art', 'pointer.png'), position=(320,35), gauge_range = 2.9)
    alt_gauge = entity.Gauge(os.path.join('Art', 'alt_gauge.png'), os.path.join('Art', 'pointer.png'), position=(395,35), gauge_range = 2.9)
    
    lift_gauge = entity.Gauge(os.path.join('Art', 'lift_gauge.png'), os.path.join('Art', 'pointer.png'), position=(135,322), gauge_range = 2.65)
    engine_gauge = entity.Gauge(os.path.join('Art', 'engine_order_2.png'), os.path.join('Art', 'bigpointer.png'), position=(50,310), gauge_range = 2.65)
    
    map.add_UI(temp_gauge)
    map.add_UI(fuel_gauge)
    map.add_UI(alt_gauge)
    map.add_UI(lift_gauge)
    map.add_UI(engine_gauge)
    
    #map entities
    map.add(entity.Entity(space, os.path.join('Art', 'floor.png'),
                          body_type = pymunk.Body.KINEMATIC,
                          position = (500,900)))
    
    ship = entity.load_entity(os.path.join('Assets\Player_Ship', 'blimp.info'), space, position = (500,820))
    map.add(ship)
    map.key_callback = ship.move
    ship.PID_alt_setpoint = 500
    ship.PID_pos_setpoint = 1000
    ship.NPC = False
    ship.flip()
    
    cannon = entity.load_entity(os.path.join('Assets\Cannon_1', 'cannon.info'), space)
    map.add(cannon)
    ship.attatch_weapon(cannon)
    
    enemy = entity.load_entity(os.path.join('Assets\Enemy_Ship_1', 'Enemy_1.info'), space, position = (500, 700), NPC = True)
    enemy.PID_alt_setpoint = 300
    enemy.PID_pos_setpoint = 1000
    enemy.navigate = True
    map.add(enemy)
    
    
    map.add(entity.Entity(space, os.path.join('Art', 'wall.png'),
                        density = 10,  body_type = pymunk.Body.DYNAMIC,
                        position = (616,770)))
    
    for i in range(20):
        map.add(entity.Entity(space, os.path.join('Art', 'box.png'),
                        density = 1,  body_type = pymunk.Body.DYNAMIC,
                        position = (600, 890 - (i * 15))))
    
    map.focus = 1
    
    '''
    Main Menu
    '''
    main_menu = world.World(screen, (640, 360), None,
                            background_color = (79,103,129))
                            
    start_button = entity.Button(os.path.join('Assets', 'Buttons', 'Start_Game.png'),
                                spritesize = (300,30),
                                matrixsize = (1,2),
                                position = (640//2, 360//2))
    start_button.set_callback(print, "Hello world!")
    main_menu.add_UI(start_button)
    
    state = "Menu"
    run = True
    showFPS = True
    tick = 0
    while run:
        startloop = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_f:
                    ship.flip()
                
        #game info text rendering
        if showFPS:
            frames = consolas.render("{} fps".format(round(map.fps,1)),True, (255,255,255))
            position = consolas.render("{:0.2f}, {:0.2f}".format(ship.body.position[0], ship.body.position[1]), 
                                                                 True, (255,255,255))
            screen.blit(frames, (5, 5))
            screen.blit(position, (5, 30))
        
        #draw window
        window.blit(pygame.transform.scale(screen, window.get_rect().size), (0, 0))
        pygame.display.flip()
        
        '''
        Game state machine transitions
        '''
        if (state == "Game"):
            pass
        elif (state == "Menu"):
            if start_button.pressed:
                state = "Game"
        
        '''
        Game state machine actions
        '''
        if (state == "Game"):
            #update gauges
            fuel_gauge.needle_position = ship.fuel
            alt_gauge.needle_position = 100 * utils.percent((1000,0), ship.body.position[1])
            lift_gauge.needle_position = 100 * utils.percent((ship.min_buoyancy,ship.max_buoyancy), ship.buoyancy)
            engine_gauge.needle_position = (ship.power / 4000) + 50
            
            #tick (THIS GOES LAST)
            map.tick(startloop)
        
        elif (state == "Menu"):
            main_menu.tick(startloop)
            

if __name__ == "__main__":
    main(sys.argv)