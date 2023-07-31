import math

def percent(range, value):
    return (value - range[0])/(range[1] - range[0])
    
def sign(n):
    if n != 0:
        return n/n
    else:
        return 0

'''
Determine if a point lies inside a box
'''
def in_rect(point, rect):
    if (point[0] >= rect[0]) and (point[0] <= (rect[0] + rect[2])): #x
        if (point[1] >= rect[1]) and (point[1] <= (rect[1] + rect[3])): #y
            return True
    
    return False