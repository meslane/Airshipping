import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, filepath):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filepath).convert()
        self.rect = self.image.get_rect()
        
    def center_rotate(self, surface, topleft, angle):
        rotated_image = pygame.transform.rotate(self.image, angle)
        new_rect = rotated_image.get_rect(center = self.image.get_rect(topleft = topleft).center)
        surface.blit(rotated_image, new_rect.topleft)