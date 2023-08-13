import math
import pygame

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
    
'''
Get the slope of a line between two points
'''
def slope(a, b):
    return (a[1] - b[1]) / ((a[0] - b[0]) + 1e-5)
   
'''
Get the point at which two lines intersect
'''
def intercept_point(m1, b1, m2, b2):
    #m = line slopes
    #b = line origins
    
    if (m1 == m2): #lines are parallel
        return None
    
    x = (b2 - b1)/(m1 - m2)
    y = m1 * (b2 - b1)/(m1 - m2) + b1
    
    return (x,y)
   
'''
Determine if line intersects rect and return the intersection point if true

args:
    m = slope of line
    b = intercept of line
    rect = target rect
    
returns:
    point at which line intersects or None if there is no intersection
'''
def intersects(m, b, rect):
    
    p1 = (rect[0], rect[1])
    p2 = (rect[0] + rect[2], rect[1])
    p3 = (rect[0], rect[1] + rect[3])
    p4 = (rect[0] + rect[2], rect[1] + rect[3])
    
    y1 = m * p1[0] + b
    y2 = m * p2[0] + b
    
    if (y1 >= p1[1] and y1 <= p3[1]): #left vertical
        return (p1[0], y1)
    elif (y2 >= p2[1] and y2 <= p4[1]): #right vertical
        return (p1[0], y2)
        
    i1 = intercept_point(m, b, 0, p1[1])
    i2 = intercept_point(m, b, 0, p3[1])
    
    if i1:
        if i1[0] >= p1[0] and i1[0] <= p2[0]: #top horizontal
            return intercept_point(m, b, 0, p1[1])
    if i2:
        if i2[0] >= p1[0] and i2[0] <= p2[0]: #bottom horizontal
            return intercept_point(m, b, 0, p3[1])
        
    return None
    
'''
Determine if a position p3 is between two other positions (in the X direction)

args:
    p1: first point
    p2: second point
    p3: point to evaluate for between-ness
    
returns:
    boolean denoting if the point lies between or not
'''
def x_between(p1, p2, p3):
    if p3[0] >= p2[0] and p3[0] >= p1[0]: #positive x
        return False
    elif p3[0] <= p2[0] and p3[0] <= p1[0]: #negative x
        return False
    if p3[1] >= p2[1] and p3[1] >= p1[1]: #positive y
        return False
    elif p3[1] <= p2[1] and p3[1] <= p1[1]: #negative y
        return False
            
    return True