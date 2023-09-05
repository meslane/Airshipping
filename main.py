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
    pygame.mixer.init()
    
    pygame.display.set_caption("Airshipping")
    window = pygame.display.set_mode([640,360], pygame.SCALED | pygame.RESIZABLE)
    screen = pygame.Surface((640,360))
    consolas = pygame.font.SysFont("Consolas", 14)

    space = pymunk.Space()
    space.gravity = (0,400)

    '''
    Overworld
    '''
    map = world.load_map(os.path.join('Assets', 'Maps', 'world1.map'), screen, space, do_physics = True)
    
    #init UI steam gauges
    temp_gauge = entity.Gauge(entity.load_image(os.path.join('Art', 'temp_gauge.png')), entity.load_image(os.path.join('Art', 'pointer.png')), position=(245,35), gauge_range = 2.9)
    fuel_gauge = entity.Gauge(entity.load_image(os.path.join('Art', 'fuel_gauge.png')), entity.load_image(os.path.join('Art', 'pointer.png')), position=(320,35), gauge_range = 2.9)
    alt_gauge = entity.Gauge(entity.load_image(os.path.join('Art', 'empty_gauge.png')), entity.load_image(os.path.join('Art', 'pointer.png')), position=(395,35), gauge_range = 2.9)
    autopilot_gauge = entity.Gauge(entity.load_image(os.path.join('Art', 'alt_gauge.png')), entity.load_image(os.path.join('Art', 'smallpointer.png')), position=(395,35), gauge_range = 2.9)
    
    lift_gauge = entity.Gauge(entity.load_image(os.path.join('Art', 'lift_gauge.png')), entity.load_image(os.path.join('Art', 'pointer.png')), position=(40,322), gauge_range = 2.65)
    
    map.add_UI(temp_gauge)
    map.add_UI(fuel_gauge)
    map.add_UI(autopilot_gauge)
    map.add_UI(alt_gauge)
    map.add_UI(lift_gauge)
    #map.add_UI(engine_gauge)
    
    #map entities
    
    ship = entity.load_entity(os.path.join('Assets\Player_Ship', 'blimp.info'), space, position = (500,820))
    map.add(ship)
    map.key_callback = ship.move
    ship.PID_alt_setpoint = 500
    ship.PID_pos_setpoint = 1000
    ship.NPC = False
    
    cannon = entity.load_entity(os.path.join('Assets\Cannon_1', 'cannon.info'), space)
    map.add(cannon)
    ship.attatch_weapon(cannon)

    for i in range(10):
        enemy = entity.load_entity(os.path.join('Assets\Enemy_Ship_1', 'Enemy_1.info'), space, 
        position = (random.randint(100,4000),random.randint(100,900)), 
        NPC = True)
        enemy.navigate = True
        enemy.target_ID = ship.ID
        map.add(enemy)
    
    map.focus = ship.ID
                                
    '''
    Main Menu
    '''
    main_menu = world.World(screen, (640, 360), None,
                            background_color = (79,103,129))
                            
    start_button = entity.Button(entity.load_image(os.path.join('Assets', 'Buttons', 'New_Game.png')),
                                spritesize = (300,30),
                                matrixsize = (1,2),
                                position = (640//2, 360//2 - 30))
    #start_button.set_callback(print, "Hello world!")
    main_menu.add_UI(start_button)
    
    load_button = entity.Button(entity.load_image(os.path.join('Assets', 'Buttons', 'Load_Game.png')),
                                spritesize = (300,30),
                                matrixsize = (1,2),
                                position = (640//2, 360//2 + 30))
    main_menu.add_UI(load_button)
    
    '''
    Pause Menu
    '''
    pause_menu = world.World(screen, (640, 360), None,
                            background_color = (79,103,129))
    
    state = "Menu"
    run = True
    showFPS = True
    tick = 0
    
    pidfile = 'Telemetry/pid{}.csv'.format(int(time.time()))
    
    while run:
        startloop = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYUP and state == "Game":
                if event.key == pygame.K_p:
                    if ship.autopilot:
                        ship.autopilot = False
                    else:
                        ship.autopilot = True
                if event.key == pygame.K_ESCAPE:
                    state = "Paused"
            elif event.type == pygame.KEYUP and state == "Paused":
                if event.key == pygame.K_ESCAPE:
                    state = "Game"
                
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
        elif (state == "Paused"):
            pass
        
        '''
        Game state machine actions
        '''
        if (state == "Game"):
            #update gauges
            temp_gauge.needle_position = 100 * ((ship.max_hp - ship.hp)/ship.max_hp)
            fuel_gauge.needle_position = ship.fuel
            alt_gauge.needle_position = 100 * utils.percent((1000,0), ship.body.position[1])
            autopilot_gauge.needle_position = 100 * utils.percent((1000,0), ship.PID_alt_setpoint)
            lift_gauge.needle_position = 100 * utils.percent((ship.min_buoyancy,ship.max_buoyancy), ship.buoyancy)
            #engine_gauge.needle_position = (ship.power / 4000) + 50
            
            #tick (THIS GOES LAST)
            map.tick(startloop)
            #ship.write_PID_alt_csv(pidfile)
        elif (state == "Menu"):
            main_menu.tick(startloop)
        elif (state == "Paused"):
            pause_menu.tick(startloop)
        
        
        tick += 1

if __name__ == "__main__":
    main(sys.argv)