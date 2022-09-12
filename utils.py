import math

def percent(range, value):
    return (value - range[0])/(range[1] - range[0])
    
def sign(n):
    if n != 0:
        return n/n
    else:
        return 0
    