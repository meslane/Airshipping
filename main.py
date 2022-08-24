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
    
    #pointers = Needles((320 - 107, 286))
    
    airships = []
    
    airships.append(entity.Entity(space, os.path.join('Art', 'airshipsmall.png'), 
                            spritesize=(108,64), matrixsize=(2,2), 
                            mass = 1000, moment = 10000, body_type = pymunk.Body.DYNAMIC,
                            hitbox=os.path.join('Art','airship.box')))
    airships[0].set_position((200,-150))
    airships[0].body.velocity = (0, 50)
    
    
    airships.append(entity.Entity(space, os.path.join('Art', 'airshipsmall.png'), 
                            spritesize=(108,64), matrixsize=(2,2), 
                            mass = 1000, moment = 10000, body_type = pymunk.Body.DYNAMIC,
                            hitbox=os.path.join('Art','airship.box')))
    airships[1].set_position((210,-300))
    airships[1].body.velocity = (0, 50)
    
    airships.append(entity.Entity(space, os.path.join('Art', 'airshipsmall.png'), 
                            spritesize=(108,64), matrixsize=(2,2), 
                            mass = 1000, moment = 10000, body_type = pymunk.Body.DYNAMIC,
                            hitbox=os.path.join('Art','airship.box')))
    airships[2].set_position((-500,-200))
    airships[2].body.velocity = (520, 0)
    airships[2].body.angular_velocity = 12
    
    floor = entity.Entity(space, os.path.join('Art', 'floor.png'),
                          body_type = pymunk.Body.KINEMATIC)
    floor.set_position((320,360-8))
    
    wall = entity.Entity(space, os.path.join('Art', 'wall.png'),
                        mass = 0,  body_type = pymunk.Body.DYNAMIC)
    wall.set_position((336,225))
    
    boxes = []
    
    ball = entity.Entity(space, os.path.join('Art', 'cannonball.png'),
                          shape='circle', body_type = pymunk.Body.DYNAMIC,
                          density = 50)
    ball.set_position((-500, 0))
    ball.body.velocity = (800,0)
    ball.body.angular_velocity = 12
    
    for i in range(20):
        boxes.append(entity.Entity(space, os.path.join('Art', 'box.png'),
                        mass = 1,  body_type = pymunk.Body.DYNAMIC))
        boxes[i].set_position((320, 344 - (i * 16)))
    
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
        

        for airship in airships:
            airship.draw(space,screen)
            airship.set_sprite_index(frame // 4 % 4)
        
        for box in boxes:
            box.draw(space,screen)
        
        floor.draw(space, screen)
        wall.draw(space, screen)
        ball.draw(space, screen)
        
        #this goes last in the loop
        #options = pymunk.pygame_util.DrawOptions(screen)
        #space.debug_draw(options)
        window.blit(pygame.transform.scale(screen, window.get_rect().size), (0, 0))
        pygame.display.flip()
        clock.tick(120)
        space.step(1.0/120.0)
        
        fps = int(1/(time.time() - startloop + 0.000001))
        frame += 1
    
if __name__ == "__main__":
    main(sys.argv)