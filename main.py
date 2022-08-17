import pygame
import sys
import os
import time

import entity

def main(argv):
    pygame.init()
    
    pygame.display.set_caption("Airshipping")
    window = pygame.display.set_mode([640,360], pygame.SCALED | pygame.RESIZABLE)
    screen = pygame.Surface((640,360))
    
    gauges = pygame.image.load(os.path.join('Art', 'gauges.png')).convert()
    consolas = pygame.font.SysFont("Consolas", 14)
    
    alt = entity.Entity(os.path.join('Art', 'pointer.png'))
    alt.set_position((599, 293))
    
    spritetest = entity.Entity(os.path.join('Art/shitposts', 'sussy.png'), spritesize=(125,105), matrixsize=(5,1))
    spritetest.set_position((300,100))
    
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
        
        screen.blit(gauges, (640 - 220, 360-74))
        
        alt.center_rotate(frame % 360)
        alt.draw(screen)
        
        spritetest.set_sprite_index(frame % 5)
        spritetest.center_rotate(frame % 360)
        
        if (spritetest.rect.topleft[1] > 0):
            spritetest.translate((-10,-10))
        else:
            spritetest.set_position((300,300))
        spritetest.draw(screen)
        
        #this goes last in the loop
        window.blit(pygame.transform.scale(screen, window.get_rect().size), (0, 0))
        pygame.display.flip()
        
        fps = int(1/(time.time() - startloop + 0.000001))
        print(fps)
        frame += 1
    
if __name__ == "__main__":
    main(sys.argv)