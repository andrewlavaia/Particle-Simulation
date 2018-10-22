import math

def angle(dy, dx):
    radians = math.atan2(dy, dx) # between -pi and pi
    degrees = radians * 180/math.pi
    if degrees > 90:
        degrees = 450 - degrees
    else:
        degrees = 90 - degrees
    return degrees

def pythag(side1, side2):
    return math.sqrt((side1 * side1) + (side2 * side2))