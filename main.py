import pygame
import pymunk 

import sys
import os
import time
import random

#engine imports
import entity
import world

'''
class Needles:
    def __init__(self, position):
        self.position = position
        self.gauges = pygame.image.load(os.path.join('Art', 'gauges.png')).convert()
        self.alt = entity.Entity(os.path.join('Art', 'pointer.png'))
        self.fuel = entity.Entity(os.path.join('Art', 'pointer.png'))
        self.temp = entity.Entity(os.path.join('Art', 'pointer.png'))
        self.alt.set_position((position[0] + 179, position[1] + 7))
        self.fuel.set_position((position[0] + 105, position[1] + 7))
        self.temp.set_position((position[0] + 31, position[1] + 7))
        
    def set(self, temp, fuel, alt):
        self.temp.center_rotate((-2.9 * temp) + 145)
        self.fuel.center_rotate((-2.9 * fuel) + 145)
        self.alt.center_rotate((-2.9 * alt) + 145)
        
    def draw(self, screen):
        screen.blit(self.gauges, self.position)
        self.alt.draw(screen)
        self.fuel.draw(screen)
        self.temp.draw(screen)
'''
def collide(arbiter, space, data):
    print("collided")
    print(data)
    return True

def main(argv):
    pygame.init()
    
    pygame.display.set_caption("Airshipping")
    window = pygame.display.set_mode([640,360], pygame.SCALED | pygame.RESIZABLE)
    screen = pygame.Surface((640,360))
    
    #map = pygame.Surface((2560, 1440))
    
    
    space = pymunk.Space()
    space.gravity = (0,400)
    #handler = space.add_collision_handler(1,1)
    #handler.begin = collide
    
    consolas = pygame.font.SysFont("Consolas", 14)
    
    #pointers = Needles((320 - 107, 286))

    map = world.World((1000, 1000))
    
    map.add(entity.Entity(space, os.path.join('Art', 'floor.png'),
                          body_type = pymunk.Body.KINEMATIC))
    map.entities.sprites()[-1].set_position((500,900))
    
    map.add(entity.Entity(space, os.path.join('Art', 'airshipsmall.png'), 
                            spritesize=(108,64), matrixsize=(2,2), 
                            mass = 1000, moment = 10000, body_type = pymunk.Body.DYNAMIC,
                            hitbox=os.path.join('Art','airship.box'),
                            animation_step=6))
    map.entities.sprites()[-1].set_position((500,820))
    
    map.add(entity.Entity(space, os.path.join('Art', 'wall.png'),
                        mass = 0,  body_type = pymunk.Body.DYNAMIC))
    map.entities.sprites()[-1].set_position((616,770))
    
    for i in range(20):
        map.add(entity.Entity(space, os.path.join('Art', 'box.png'),
                        mass = 1,  body_type = pymunk.Body.DYNAMIC))
        map.entities.sprites()[-1].set_position((600, 890 - (i * 15)))
    
    '''
    map.add(entity.Entity(space, os.path.join('Art', 'airshipsmall.png'), 
                            spritesize=(108,64), matrixsize=(2,2), 
                            mass = 1000, moment = 10000, body_type = pymunk.Body.DYNAMIC,
                            hitbox=os.path.join('Art','airship.box')))
    map.entities.sprites()[-1].set_position((210,-300))
    map.entities.sprites()[-1].body.velocity = (0, 50)
    
    map.add(entity.Entity(space, os.path.join('Art', 'airshipsmall.png'), 
                            spritesize=(108,64), matrixsize=(2,2), 
                            mass = 1000, moment = 10000, body_type = pymunk.Body.DYNAMIC,
                            hitbox=os.path.join('Art','airship.box')))
    map.entities.sprites()[-1].set_position((-500,-200))
    map.entities.sprites()[-1].body.velocity = (520, 0)
    map.entities.sprites()[-1].body.angular_velocity = 12
    
    map.add(entity.Entity(space, os.path.join('Art', 'wall.png'),
                        mass = 0,  body_type = pymunk.Body.DYNAMIC))
    map.entities.sprites()[-1].set_position((336,225))
    
    for i in range(100):
        map.add(entity.Entity(space, os.path.join('Art', 'box.png'),
                        mass = 1,  body_type = pymunk.Body.DYNAMIC))
        map.entities.sprites()[-1].set_position((320, 344 - (i * 16)))
    
    map.add(entity.Entity(space, os.path.join('Art', 'cannonball.png'),
                          shape='circle', body_type = pymunk.Body.DYNAMIC,
                          density = 50))
    map.entities.sprites()[-1].set_position((-500, 0))
    map.entities.sprites()[-1].body.velocity = (800,0)
    map.entities.sprites()[-1].body.angular_velocity = 12
    '''
    
    map.focus = 1

    gauges = entity.StaticObject(os.path.join('Art', 'gauges.png'), position=(320,35))

    run = True
    fps = 0
    frame = 0
    clock = pygame.time.Clock()
    while run:
        startloop = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        '''        
        if (frame % 60 == 0):
            map.translate((-20,0))
        '''        
                
        map.map.fill((170,255,255))
        
        #entities.update()
        #entities.draw(map.map)
        
        #this goes last in the loop
        #options = pymunk.pygame_util.DrawOptions(screen)
        #space.debug_draw(options)
        #screen.blit(map, (0,0), (entities.sprites()[0].body.position[0] - 640 // 2, entities.sprites()[0].body.position[1] - 360 // 2, 640, 360))
        #map.focus_camera(entities.sprites()[0])
        keys = pygame.key.get_pressed()
        power = 2000000
        turning = 16
        cg = map.entities.sprites()[1].body.center_of_gravity
        if keys[pygame.K_q]:
            map.entities.sprites()[1].body.apply_force_at_local_point(force=(0, -power/turning), point=(cg[0]+30, cg[1]))
            map.entities.sprites()[1].body.apply_force_at_local_point(force=(0, power/turning), point=(cg[0]-30, cg[1]))
        if keys[pygame.K_e]:
            map.entities.sprites()[1].body.apply_force_at_local_point(force=(0, power/turning), point=(cg[0]+30, cg[1]))
            map.entities.sprites()[1].body.apply_force_at_local_point(force=(0, -power/turning), point=(cg[0]-30, cg[1]))
        if keys[pygame.K_w]:
            map.entities.sprites()[1].body.apply_force_at_local_point(force=(0,-power), point=(cg[0], cg[1]))
        if keys[pygame.K_s]:
            map.entities.sprites()[1].body.apply_force_at_local_point(force=(0,power), point=(cg[0], cg[1]))
        if keys[pygame.K_a]:
            map.entities.sprites()[1].body.apply_force_at_local_point(force=(-power,0), point=(cg[0], cg[1]))
        if keys[pygame.K_d]:
            map.entities.sprites()[1].body.apply_force_at_local_point(force=(power,0), point=(cg[0], cg[1]))
        
        map.draw(screen)
        
        gauges.draw(screen)
        
        frames = consolas.render("{} fps".format(round(fps,1)),True, (255,255,255))
        screen.blit(frames, (5, 5))
        
        window.blit(pygame.transform.scale(screen, window.get_rect().size), (0, 0))
        pygame.display.flip()
        clock.tick(120)
        space.step(1.0/120.0)
        
        fps = int(1/(time.time() - startloop + 0.000001))
        frame += 1
    
if __name__ == "__main__":
    main(sys.argv)