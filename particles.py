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
            vx = None, vy = None, m = None,
            color = None, shape = "Circle"):

        # set default values
        if (radius == None):
            radius = 5.0
        if (x == None):
            x = random.uniform(0 + radius, window.width - radius)
        if (y == None):
            y = random.uniform(0 + radius, window.height - radius)
        if (vx == None):
            vx = random.uniform(-200.0, 200.0)
        if (vy == None):
            vy = random.uniform(-200.0, 200.0)
        if (m == None):
            m = 1.0
        if (color == None):
            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)
            color = color_rgb(red, green, blue)
        
        # initialize instance properties
        
        self.x = x                      # position
        self.y = y                        
        self.vx = vx                    # speed
        self.vy = vy
        self.mass = m                   # used for collision physics
        self.radius = radius
        self.half_width = radius        # distance from edge to center
        self.half_height = radius

        # set limits on speed and collisions
        self.max_speed = 1000000.0

        # set window to draw and render
        self.window = window
        if shape == "Circle":
            self.shape = Circle(Point(self.x, self.y), radius)
        elif shape == "Square":
            self.shape = Rectangle(Point(self.x - radius, self.y - radius), 
                Point(self.x + radius, self.y + radius))
        else:
            assert(False)
        
        self.shape.setFill(color)
        self.shape.setOutline(color)

        self.collisionCnt = 0               # number of collisions - used to
                                            # check whether event has become
                                            # invalidated
 
    # equality comparator
    def __eq__(self, other):
        return ((self.x, self.y, self.shape, self.collisionCnt) ==
                (other.x, other.y, other.shape, other.collisionCnt))

    # Moves particle by time * speed
    def move(self, dt):   
        self.x = self.x + (self.vx * dt)
        self.y = self.y + (self.vy * dt)

    # Draws the.shape to a window
    def draw(self):
        self.shape.draw(self.window)
    
    # Moves.shape to current position on window 
    def render(self):    
        self.shape.move(self.x - self.shape.getCenter().getX(), self.y - self.shape.getCenter().getY())

    # Calculates time until collision with another Particle
    def timeToHit(self, that):
        if self == that:
            return math.inf 

        # distance
        dx = that.x - self.x
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

        # how to handle corners of square particle collisions? 
        # distance from center changes depending on whether 
        # collision was on side or the corner

        # attempt 1
        # denom1 = abs(self.vx) + abs(self.vy)
        # denom2 = abs(that.vx) + abs(that.vy)
        # sigma1 = (self.half_width * abs(self.vx)/denom1) + (self.half_height * abs(self.vy)/denom1)
        # sigma2 = (that.half_width * abs(that.vx)/denom2) + (that.half_height * abs(that.vy)/denom2) 
        # sigma1 = dx * dx
        # sigma2 = dy * dy
        # sigma = math.sqrt(sigma1 + sigma2) 

        # attempt 2
        # side1 = (self.x - that.x) * (self.x - that.x)
        # side2 = (self.y - that.y) * (self.y - that.y)
        # sigma = math.sqrt(side1 + side2) 
        # if square and if angle = 0, 90, 180 etc
        # sigma = self.radius + that.radius
        
        # attempt 3
        # radians = math.atan2(dy, dx) # between -pi and pi
        # degrees = radians * 180/math.pi
        # if degrees > 90:
        #     degrees = 450 - degrees
        # else:
        #     degrees = 90 - degrees
        # print(radians, degrees)
        
        sigma = self.radius + that.radius
        
        d = (dvdr*dvdr) - (dvdv * (drdr - sigma*sigma))
        if d <= 0: 
            return math.inf
        
        if dvdv == 0:    
            return math.inf # both particles are stationary 

        return -1 * (dvdr + math.sqrt(d)) / dvdv

    # calculates time (in ms) until collision with horizontal wall
    def timeToHitHWall(self):
        if self.vy > 0:
            return (self.window.height - self.half_height - self.y) / self.vy
        elif (self.vy < 0):
            return (0.0 + self.half_height - self.y) / self.vy
        elif (self.vy == 0):
            return math.inf

    # calculates time (in ms) until collision with vertical wall
    def timeToHitVWall(self):
        if (self.vx > 0):
            return (self.window.width - self.half_width - self.x) / self.vx
        elif (self.vx < 0):
            return (0.0 + self.half_width - self.x) / self.vx
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
        # pythagorean
        # dist = self.radius + that.radius
        side1 = (self.x - that.x)*(self.x - that.x)
        side2 = (self.y - that.y)*(self.y - that.y)
        dist = math.sqrt(side1 + side2) 
        
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


# !!! Find out why speed is dying upon hitting an immovable or wall

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

    # double force for that object
    # needed, otherwise collisions with walls lose energy
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

class SquareParticle(Particle):
    def __init__(self, window, radius = None, 
        x = None, y = None, vx = None, vy = None, mass = None, color = None):

        super().__init__(window, radius, x, y, vx, vy, mass, color, shape = "Square")  

class Wall(Particle):
    def __init__(self, window, 
        radius = None, x = None, y = None, color = None):

        super().__init__(window, 1.0, x, y, 0.0, 0.0, 1.0, color, shape = "Square") 
        
    # let other particles calculate time to hit
    def timeToHit(self, that):
        return math.inf
    def timeToHitVWall(self):
        return math.inf 
    def timeToHitHWall(self):
        return math.inf 

    # double force for that object
    # needed, otherwise collisions with walls lose energy
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