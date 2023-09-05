import pygame

samples = {}

pygame.mixer.init()

samples['cannon'] = pygame.mixer.Sound("Assets\Audio\Cannon.wav")
samples['explosion'] = pygame.mixer.Sound("Assets\Audio\Explosion.wav")

def play_sound(trackname):
    samples[trackname].play()