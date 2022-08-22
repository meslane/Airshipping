import pygame
import pymunk 

import sys
import os
import time
import random

#engine imports
import entity

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
    return True

def main(argv):
    pygame.init()
    
    pygame.display.set_caption("Airshipping")
    window = pygame.display.set_mode([640,360], pygame.SCALED | pygame.RESIZABLE)
    screen = pygame.Surface((640,360))
    
    space = pymunk.Space()
    space.gravity = (0,100)
    handler = space.add_collision_handler(1,1)
    handler.begin = collide
    
    consolas = pygame.font.SysFont("Consolas", 14)
    
    #pointers = Needles((320 - 107, 286))
    
    airship = entity.Entity(space, os.path.join('Art', 'airshipsmall.png'), 
                            spritesize=(108,64), matrixsize=(2,2), 
                            mass = 1000, moment = 10000, body_type = pymunk.Body.DYNAMIC)
    airship.set_position((335,-50))
    airship.body.velocity = (0, 50)
    #airship.body.angular_velocity = 10
    
    airship2 = entity.Entity(space, os.path.join('Art', 'airshipsmall.png'), 
                            spritesize=(108,64), matrixsize=(2,2), 
                            body_type = pymunk.Body.KINEMATIC)
    airship2.set_position((280,300))
    #airship2.body.velocity = (0, -50)
    
    run = True
    fps = 0
    frame = 0
    clock = pygame.time.Clock()
    while run:
        startloop = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        screen.fill((170,255,255))
                
        frames = consolas.render("{} fps".format(round(fps,1)),True, (255,255,255))
        screen.blit(frames, (5, 5))
        
        airship.set_sprite_index(frame // 3 % 4)
        airship.draw(screen)
        
        #airship2.set_sprite_index(frame // 3 % 4)
        airship2.draw(screen)
        #airship.center_rotate(space, frame % 360)
        
        if airship.body.position[1] > 400:
            airship.body.velocity = (-10, -300)
        
        #pointers.set(0, 100 - (frame / 30), 350 - airship.rect.topleft[1] / 3.6)
        #pointers.draw(screen)
        
        #this goes last in the loop
        window.blit(pygame.transform.scale(screen, window.get_rect().size), (0, 0))
        pygame.display.flip()
        clock.tick(120)
        space.step(1.0/60.0)
        
        fps = int(1/(time.time() - startloop + 0.000001))
        frame += 1
    
if __name__ == "__main__":
    main(sys.argv)