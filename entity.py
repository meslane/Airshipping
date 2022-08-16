import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, filepath):
        pygame.sprite.Sprite.__init__(self)
        
        self.original_image = pygame.image.load(filepath).convert() #must preserve an undisturbed copy for rotations
        self.original_rect = self.original_image.get_rect()
            
        self.image = self.original_image
        self.rect = self.original_rect
        
    def set_position(self, coords):
        self.original_rect.topleft = coords
        self.rect.topleft = coords
        
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        
    def center_rotate(self, angle):
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center = self.original_image.get_rect(topleft = self.original_rect.topleft).center)
        
class Spritesheet(pygame.sprite.Sprite):
    def __init__(self, filepath, spritesize, matrixsize):
        pygame.sprite.Sprite.__init__(self)
    
        self.image = pygame.image.load(filepath).convert_alpha()
        
        self.original_surface = pygame.Surface(spritesize).convert_alpha() #must preserve an undisturbed copy for rotations
        self.original_rect = self.original_surface.get_rect()
        
        self.surface = self.original_surface
        self.rect = self.original_rect
        
        self.spritesize = spritesize
        self.matrixsize = matrixsize
        
    def set_position(self, coords):
        self.original_rect.topleft = coords
        self.rect.topleft = coords
        
    def draw(self, surface):
        surface.blit(self.surface, self.rect.topleft)
        
    def center_rotate(self, angle):
        self.surface = pygame.transform.rotate(self.original_surface, angle)
        self.rect = self.surface.get_rect(center = self.original_surface.get_rect(topleft = self.original_rect.topleft).center)
        
    def set_sprite(self, index):
        self.surface.fill((0,0,0,0))
        self.original_surface.fill((0,0,0,0))
        x = (index % self.matrixsize[0]) * self.spritesize[0] #get horizontal location of sprite
        y = (index // self.matrixsize[0]) * self.spritesize[1] #get vertical
        self.original_surface.blit(self.image, (0,0), (x, y, self.spritesize[0], self.spritesize[1]))
        self.surface.blit(self.image, (0,0), (x, y, self.spritesize[0], self.spritesize[1]))