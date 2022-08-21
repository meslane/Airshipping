import pygame
import sys
import os
import time
import random

import entity

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

def main(argv):
    pygame.init()
    
    pygame.display.set_caption("Airshipping")
    window = pygame.display.set_mode([640,360], pygame.SCALED | pygame.RESIZABLE)
    screen = pygame.Surface((640,360))
    
    consolas = pygame.font.SysFont("Consolas", 14)
    
    pointers = Needles((320 - 107, 286))
    
    airship = entity.Entity(os.path.join('Art', 'airshipsmall.png'), spritesize=(108,64), matrixsize=(2,2), physics=True)
    airship.set_position((0,300))
    airship.mass = 11000
    
    airship2 = entity.Entity(os.path.join('Art', 'airshipsmall.png'), spritesize=(108,64), matrixsize=(2,2), physics=True)
    airship2.set_position((550,300))
    airship2.mass = 10000
    
    run = True
    fps = 0
    frame = 0
    clock = pygame.time.Clock()
    while run:
        clock.tick(60)
        startloop = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        screen.fill((170,255,255))
                
        frames = consolas.render("{} fps".format(round(fps,1)),True, (255,255,255))
        screen.blit(frames, (5, 5))
        
        if pygame.sprite.collide_rect(airship, airship2):
            entity.collide(airship, airship2)
        
        airship.set_sprite_index(frame // 3 % 4)
        airship.update()
        airship.draw(screen)
        
        airship2.set_sprite_index(frame // 3 % 4)
        airship2.update()
        airship2.draw(screen)
        
        if airship.rect.topleft[1] > 400:
            airship.set_position((0,300))
            airship.velocity.y = -10
            airship.velocity.x = 4
            
        if airship2.rect.topleft[1] > 400:
            airship2.set_position((550,300))
            airship2.velocity.y = random.randint(-10,-5)
            airship2.velocity.x = -4
        
        pointers.set(0, 100 - (frame / 30), 350 - airship.rect.topleft[1] / 3.6)
        pointers.draw(screen)
        
        #this goes last in the loop
        window.blit(pygame.transform.scale(screen, window.get_rect().size), (0, 0))
        pygame.display.flip()
        
        fps = int(1/(time.time() - startloop + 0.000001))
        frame += 1
    
if __name__ == "__main__":
    main(sys.argv)