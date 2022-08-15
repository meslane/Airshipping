import pygame
import sys
import os
import time

import entity

def main(argv):
    pygame.init()
    
    pygame.display.set_caption("Airshipping")
    window = pygame.display.set_mode([640,360], pygame.RESIZABLE)
    screen = pygame.Surface((640,360))
    
    gauges = pygame.image.load(os.path.join('Art', 'gauges.png')).convert()
    consolas = pygame.font.SysFont("Consolas", 14)
    
    alt = entity.Entity(os.path.join('Art', 'pointer.png'))
    fuel = entity.Entity(os.path.join('Art', 'pointer.png'))
    temp = entity.Entity(os.path.join('Art', 'pointer.png'))
    
    run = True
    fps = 0
    frame = 0
    while run:
        startloop = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        screen.fill((170,255,255))
                
        frames = consolas.render("{} fps".format(round(fps,1)),True, (255,255,255))
        screen.blit(frames, (5, 5))
        
        screen.blit(gauges, (640 - 220, 360-74))
        alt.center_rotate(screen, (599, 293), frame % 300 - 150)
        fuel.center_rotate(screen, (525, 293), frame % 300 - 150)
        temp.center_rotate(screen, (451, 293), frame % 300 - 150)
        
        #this goes last in the loop
        window.blit(pygame.transform.scale(screen, window.get_rect().size), (0, 0))
        pygame.display.flip()
        
        fps = int(1/(time.time() - startloop + 0.000001))
        
        frame += 1
    
if __name__ == "__main__":
    main(sys.argv)