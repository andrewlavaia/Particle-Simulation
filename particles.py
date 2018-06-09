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
            color = None):

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
        self.radius = radius            # size
        self.x = x                      # position
        self.y = y                        
        self.vx = vx                    # speed
        self.vy = vy
        self.mass = m                   # used for collision physics

        # set min/max speed
        self.max_speed = 100.0

        # set window to draw and render
        self.window = window                
        self.shape = Circle(Point(self.x, self.y), radius)
        self.shape.setFill(color)
        self.shape.setOutline(color)

        self.collisionCnt = 0               # number of collisions - used to
                                            # check whether event has become
                                            # invalidated
 
    # equality comparator
    def __eq__(self, other):
        return ((self.x, self.y, self.shape, self.collisionCnt) ==
                (other.x, other.y, other.shape, other.collisionCnt))

    # Moves ball by time * speed
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
            return (self.window.height - self.radius - self.y) / self.vy
        elif (self.vy < 0):
            return (0.0 + self.radius - self.y) / self.vy
        elif (self.vy == 0):
            return math.inf

    # calculates time (in ms) until collision with vertical wall
    def timeToHitVWall(self):
        if (self.vx > 0):
            return (self.window.width - self.radius - self.x) / self.vx
        elif (self.vx < 0):
            return (0.0 + self.radius - self.x) / self.vx
        elif (self.vx == 0):
            return math.inf

    # adjusts velocity vectors of two objects after a collision
    def bounceOff(self, that):
        dx = that.x - self.x
        dy = that.y - self.y
        dvx = that.vx - self.vx 
        dvy = that.vy - self.vy

        # dot product
        dvdr = dx*dvx + dy*dvy
        dist = self.radius + that.radius

        # calculate magnitude of force
        J = 2 * self.mass * that.mass * dvdr / ((self.mass + that.mass) * dist)
        fx = J * dx / dist
        fy = J * dy / dist
        self.vx = self.vx + (fx / self.mass)
        self.vy = self.vy + (fy / self.mass)
        that.vx = that.vx - (fx / that.mass)
        that.vy = that.vy - (fy / that.mass)

        if self.vx > self.max_speed:
            self.vx = self.max_speed
        elif self.vx < -1 * self.max_speed:
            self.vx = -1 * self.max_speed
        if self.vy > self.max_speed:
            self.vy = self.max_speed
        elif self.vy < -1 * self.max_speed:
            self.vy = -1 * self.max_speed

        # increase collision count
        self.collisionCnt = self.collisionCnt + 1
        that.collisionCnt = that.collisionCnt + 1

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
        # initialize vx and vy to 0
        # initialize mass to 4 billion
        super().__init__(window, radius, x, y, 0, 0, 4000000000, color)      

class VWall(Immovable):
    def __init__(self, window, x, x2, y, y2, color = None):

        if (color == None):
            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)
            color = color_rgb(red, green, blue)
        
        # initialize instance properties
        self.x = x                      
        self.y = y
        self.x2 = x2
        self.y2 = y2
        self.radius = 1.0     # needed for collision calculations

        # stationary particles shouldn't move                        
        self.vx = 0.0     
        self.vy = 0.0                
        self.mass = 4000000000         

        # set window to draw and render
        self.window = window                
        self.shape = Rectangle(Point(self.x, self.y), Point(self.x + 1, self.y2))
        self.shape.setFill(color)
        self.shape.setOutline(color)

        self.collisionCnt = 0               # number of collisions - used to
                                            # check whether event has become
                                            # invalidated
