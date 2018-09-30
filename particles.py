'''
Module: particles.py
Defines particles for use in particle simulation
'''

import math
import random
from graphics import Point, Circle, Rectangle, color_rgb

# Defines a Particle object which can be used in the Collision Simulator
class Particle:
    def __init__(self, window, 
            radius = None, x = None, y = None, 
            vx = None, vy = None, mass= None,
            color = None, shape = "Circle", width = None, height = None):

        # set window to draw and render
        self.window = window
        self.window_width = self.window.width
        self.window_height = self.window.height

        # set default values
        if radius == None and shape == "Circle":
            radius = 5.0
        if shape == "Circle":
            width = radius * 2.0
        elif width == None:
            width = 10.0    
        if shape == "Circle":
            height = radius * 2.0
        elif height == None:
            height = 10.0  
        if x == None:
            x = random.uniform(0 + width/2.0, self.window_width - height/2.0)
        if y == None:
            y = random.uniform(0 + width/2.0, self.window_height - height/2.0)
        if vx == None:
            vx = random.uniform(-200.0, 200.0)
        if vy == None:
            vy = random.uniform(-200.0, 200.0)
        if mass == None:
            mass = 1.0
        if color == None:
            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)
            color = color_rgb(red, green, blue)

        self.x = x                      # position
        self.y = y                        
        self.vx = vx                    # speed
        self.vy = vy
        self.mass = mass                # used for collision physics
        self.radius = radius
        self.width = width    
        self.height = height
        self.shape_type = shape

        # set limits on speed and collisions
        # self.max_speed = 1000000.0

        if shape == "Circle":
            self.shape = Circle(Point(self.x, self.y), radius)
        elif shape == "Rect":
            self.shape = Rectangle(Point(self.x - width/2.0, self.y - height/2.0), 
                Point(self.x + width/2.0, self.y + height/2.0))
        else:
            assert(False)
        
        self.shape.setFill(color)
        self.shape.setOutline(color)

        self.collisionCnt = 0               # number of collisions - used to
                                            # check whether event has become
                                            # invalidated
 
    # equality comparator
    def __eq__(self, other):
        return ((self.x, self.y, self.collisionCnt) ==
                (other.x, other.y, other.collisionCnt))

    # ignore the following attributes when pickling     
    def __getstate__(self):
        state = self.__dict__.copy()
        if state.get('shape'):
            del state['shape']
        if state.get('window'):
            del state['window']
        return state

    # Moves particle by time * speed
    def move(self, dt):   
        self.x = self.x + (self.vx * dt)
        self.y = self.y + (self.vy * dt)

    # Draws the.shape to a window
    def draw(self):
        # self.shape.draw(self.window)
        pass
    
    # Moves.shape to current position on window 
    def render(self):    
        # self.shape.move(self.x - self.shape.getCenter().getX(), self.y - self.shape.getCenter().getY())
        pass

    def pythagorean(self, side1, side2):
        return math.sqrt((side1 * side1) + (side2 * side2)) 

    def calcAngle(self, dy, dx):
        radians = math.atan2(dy, dx) # between -pi and pi
        degrees = radians * 180/math.pi
        if degrees > 90:
            degrees = 450 - degrees
        else:
            degrees = 90 - degrees
        return degrees

    def distFromCenter(self, deg):
        if self.shape_type == "Circle":
            return self.radius
        
        twoPI = math.pi * 2
        theta = deg * math.pi / 180
  
        while theta < -math.pi:
            theta += twoPI
  
        while theta > math.pi:
            theta -= twoPI
            
        rectAtan = math.atan2(self.height, self.width)
        tanTheta = math.tan(theta)

        region = 0  
        if (theta > -rectAtan) and (theta <= rectAtan):
            region = 1
        elif (theta > rectAtan) and (theta <= (math.pi - rectAtan)):
            region = 2
        elif (theta > (math.pi - rectAtan)) or (theta <= -(math.pi - rectAtan)):
            region = 3
        else:
            region = 4
    
        edgePoint = Point(self.width/2.0, self.height/2.0)
        xFactor = 1
        yFactor = 1
        
        if region == 1 or region == 2:
            yFactor = -1
        elif region == 3 or region == 4:
            xFactor = -1
        
        if region == 1 or region == 3:
            edgePoint.x = edgePoint.x + (xFactor * (self.width / 2.0))                # "Z0"
            edgePoint.y = edgePoint.y + (yFactor * (self.width / 2.0) * tanTheta)
        else:
            edgePoint.x = edgePoint.x + (xFactor * (self.height / (2.0 * tanTheta)))  # "Z1"
            edgePoint.y = edgePoint.y + (yFactor * (self.height /  2.0))
        
        return self.pythagorean(edgePoint.x - (self.width/2.0), 
                                edgePoint.y - (self.height/2.0)) 

    # Calculates time until collision with another Particle
    
    # Need a new collision detection algorithm for rectangles...
    #  This algo is not computing correctly for long rectangles
    #  because it is computing the angle from the center
    #  and not the edge (ie particle traveling straight up 
    #  won't hit left or right edges of long rectangle because
    #  the angle calc tells it to use the vertical distance) 
    def timeToHit(self, that):
        if self == that:
            return math.inf 

        # distance
        dx = that.x - self.x # switch to distance between nearest points?
        dy = that.y - self.y
        
        # speed
        dvx = that.vx - self.vx 
        dvy = that.vy - self.vy
        
        # collision prediction
        dvdr = dx*dvx + dy*dvy
        if dvdr > 0: 
            return math.inf
        dvdv = dvx*dvx + dvy*dvy
        drdr = dx*dx + dy*dy
        
        dist_from_center1 = self.distFromCenter(self.calcAngle(dx, dy))
        dist_from_center2 = that.distFromCenter(that.calcAngle(-dx, -dy)) 
        sigma = dist_from_center1 + dist_from_center2
        
        d = (dvdr*dvdr) - (dvdv * (drdr - sigma*sigma))
        if d <= 0: 
            return math.inf
        
        if dvdv == 0:    
            return math.inf # both particles are stationary 

        return -1 * (dvdr + math.sqrt(d)) / dvdv

    # calculates time (in ms) until collision with horizontal wall
    def timeToHitHWall(self):
        menu_height = 20.0
        if self.vy > 0:
            return (self.window_height - self.height/2 - self.y - menu_height) / self.vy 
        elif (self.vy < 0):
            return (0.0 + self.height/2 - self.y) / self.vy
        elif (self.vy == 0):
            return math.inf

    # calculates time (in ms) until collision with vertical wall
    def timeToHitVWall(self):
        if (self.vx > 0):
            return (self.window_width - self.width/2 - self.x) / self.vx
        elif (self.vx < 0):
            return (0.0 + self.width/2 - self.x) / self.vx
        elif (self.vx == 0):
            return math.inf

    #  adjusts velocity vector given a force from collision
    def moveByForce(self, that, fx, fy):
        self.vx = self.vx + (fx / self.mass)
        self.vy = self.vy + (fy / self.mass)

        # limit speed to max speed
        # if self.vx > self.max_speed:
        #     self.vx = self.max_speed
        # elif self.vx < -1 * self.max_speed:
        #     self.vx = -1 * self.max_speed
        # if self.vy > self.max_speed:
        #     self.vy = self.max_speed
        # elif self.vy < -1 * self.max_speed:
        #     self.vy = -1 * self.max_speed

        self.collisionCnt = self.collisionCnt + 1


    # adjusts velocity vectors of two objects after a collision
    def bounceOff(self, that):
        dx = that.x - self.x
        dy = that.y - self.y
        dvx = that.vx - self.vx 
        dvy = that.vy - self.vy

        # dot product
        dvdr = dx*dvx + dy*dvy

        # calculate distance between centers
        dist = self.pythagorean(dx, dy)
        
        # calculate magnitude of force
        J = 2 * self.mass * that.mass * dvdr / ((self.mass + that.mass) * dist)
        fx = J * dx / dist
        fy = J * dy / dist

        self.moveByForce(that, fx, fy)
        that.moveByForce(self, -fx, -fy)

    # adjusts velocity of object after colliding with vertical wall
    def bounceOffVWall(self):
        self.vx = -1 * self.vx
        self.collisionCnt = self.collisionCnt + 1

    # adjusts velocity of object after colliding with horizontal wall
    def bounceOffHWall(self):
        self.vy = -1 * self.vy 
        self.collisionCnt = self.collisionCnt + 1

class Immovable(Particle):
    def __init__(self, window, 
        radius = None, x = None, y = None, color = None):

        # call base class constructor
        super().__init__(window, radius, x, y, 0.0, 0.0, 1.0, color)

    # let other particles calculate time to hit
    def timeToHit(self, that):
        return math.inf
    def timeToHitVWall(self):
        return math.inf 
    def timeToHitHWall(self):
        return math.inf 

    # double force for "that" particle
    # needed otherwise collisions with this particle lose energy
    def moveByForce(self, that, fx, fy):
        that.vx = that.vx - (fx / self.mass)
        that.vy = that.vy - (fy / self.mass)
        self.collisionCnt = self.collisionCnt + 1

    def bounceOff(self, that):
        pass
    def bounceOffVWall(self):
        pass
    def bounceOffHWall(self):
        pass

class RectParticle(Particle):
    def __init__(self, window, radius = None, 
        x = None, y = None, vx = None, vy = None, 
        mass = None, color = None, width = None, height = None):

        super().__init__(window, radius, x, y, vx, vy, mass, color, 
            shape = "Rect", width = width, height = height)  

class Wall(Particle):
    def __init__(self, window, 
        radius = None, x = None, y = None, color = None):

        super().__init__(window, 1.0, x, y, 0.0, 0.0, 1.0, color, shape = "Rect") 
        
    # let other particles calculate time to hit
    def timeToHit(self, that):
        return math.inf
    def timeToHitVWall(self):
        return math.inf 
    def timeToHitHWall(self):
        return math.inf 

    # double force for "that" particle
    # needed otherwise collisions with this particle lose energy
    def moveByForce(self, that, fx, fy):
        that.vx = that.vx - (fx / self.mass)
        that.vy = that.vy - (fy / self.mass)
        self.collisionCnt = self.collisionCnt + 1

    def bounceOff(self, that):
        pass
    def bounceOffVWall(self):
        pass
    def bounceOffHWall(self):
        pass