import math

def degrees_clockwise(dy, dx):
    ''' returns rotation degrees assuming 0 is 12 o'clock '''
    radians = math.atan2(dy, dx) # between -pi and pi
    degrees = radians * 180/math.pi
    if degrees > 90:
        degrees = 450 - degrees
    else:
        degrees = 90 - degrees
    return degrees

def angle(dy, dx):
    ''' returns radians in cartesian coordinates '''
    radians = math.atan2(dy, dx)
    return radians

def pythag(side1, side2):
    return math.sqrt((side1 * side1) + (side2 * side2))