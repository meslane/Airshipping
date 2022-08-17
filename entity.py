import pygame
from pathlib import Path
import typing
   
class Entity(pygame.sprite.Sprite):
    def __init__(self, filepath: Path, **kwargs):
        pygame.sprite.Sprite.__init__(self)
    
        self.image = pygame.image.load(filepath).convert_alpha()
        
        #set to spritesheet size of 1 by default
        self.spritesize = kwargs.get('spritesize', None)
        if not self.spritesize:
            self.spritesize = self.image.get_size()
            
        self.matrixsize = kwargs.get('matrixsize', None)
        if not self.matrixsize:
            self.matrixsize = (1,1)

        self.angle = 0
        
        self.surface = pygame.Surface(self.spritesize).convert_alpha() #must preserve an undisturbed copy for rotations
        self.rect = self.surface.get_rect()
        
        self.set_sprite_index(0) #init to zero
        
    def set_position(self, coords: tuple[int,int]):
        self.rect.topleft = coords
    
    def translate(self, offset):
        self.set_position((self.rect.topleft[0] + offset[0], self.rect.topleft[1] + offset[1]))
        
    def draw(self, drawsurface: pygame.surface):
        if (self.angle == 0):
            drawsurface.blit(self.surface, self.rect.topleft)
        else: #rotate and blit if angle != 0 (this is actually better than storing a rotated version persistantly)
            rotated_surface = pygame.transform.rotate(self.surface, self.angle)
            new_rect = rotated_surface.get_rect(center = self.surface.get_rect(topleft = self.rect.topleft).center)
            drawsurface.blit(rotated_surface, new_rect.topleft)
        
    def center_rotate(self, angle: float):
        self.angle = angle
        
    def set_sprite_index(self, index: int):
        self.surface.fill((0,0,0,0)) #set transparent
        x = (index % self.matrixsize[0]) * self.spritesize[0] #get horizontal location of sprite
        y = (index // self.matrixsize[0]) * self.spritesize[1] #get vertical
        self.surface.blit(self.image, (0,0), (x, y, self.spritesize[0], self.spritesize[1]))