import pygame
import math
import numpy

def distance(a, b):
    return math.sqrt(((b[0] - a[0]))**2 + ((b[1] - a[1]))**2 + ((b[2] - a[2]))**2)

def redmean(a, b):
    r = 0.5 * (a[0] + b[0])

    return math.sqrt((2+(r/256))*(a[0]-b[0])**2 + 4*(a[2]-b[2])**2 + (2+((255-r)/256))*(a[1]-b[1])**2)

def getNearestColor(pixel, palette):
    nearest = palette[0][0]
    for row in palette:
        for color in row:
            if redmean(color.astype(float), pixel.astype(float)) <= redmean(nearest.astype(float), pixel.astype(float)):
                nearest = color

    return nearest
            
def main():
    pygame.init()
    window = pygame.display.set_mode([200,200], pygame.RESIZABLE)
    pygame.display.set_caption("Posterizer")
    
    palname = str(input("palette>"))
    filename = str(input("image>"))
    
    pal = pygame.surfarray.pixels3d(pygame.image.load(palname).convert())
    image = pygame.image.load(filename).convert()
    imarray = pygame.surfarray.pixels3d(image)
    
    window = pygame.display.set_mode(image.get_size(), pygame.SCALED | pygame.RESIZABLE)
    
    for i, row in enumerate(imarray):
        for j, pixel in enumerate(row):
            imarray[i][j] = getNearestColor(pixel, pal)
    
    newimage = pygame.surfarray.make_surface(imarray)
    
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
                
        window.blit(newimage, (0, 0))
        pygame.display.flip()
        
if __name__ == "__main__":
    main()