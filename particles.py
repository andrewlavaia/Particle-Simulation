'''
Module: particles.py
Defines particles for use in particle simulation
'''

import math
import random
from graphics import Point, Circle, color_rgb

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
            vx = random.uniform(-100, 100)
        if (vy == None):
            vy = random.uniform(-100, 100)
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

        # set window to draw and render
        self.window = window                
        self.circle = Circle(Point(self.x, self.y), radius)
        self.circle.setFill(color)
        self.circle.setOutline(color)

        self.collisionCnt = 0               # number of collisions - used to
                                            # check whether event has become
                                            # invalidated
 
    # equality comparator
    def __eq__(self, other):
        return ((self.x, self.y, self.circle, self.collisionCnt) ==
                (other.x, other.y, other.circle, other.collisionCnt))

    # Moves ball by time * speed
    def move(self, dt):   
        self.x = self.x + (self.vx * dt)
        self.y = self.y + (self.vy * dt)

    # Draws the Circle to a window
    def draw(self):
        self.circle.draw(self.window)
    
    # Moves Circle to current position on window 
    def render(self):    
        self.circle.move(self.x - self.circle.getCenter().getX(), self.y - self.circle.getCenter().getY())

    # Calculates time (in ms) until collision with another Particle
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
        # d = (Δv*Δr)^2 − (Δv*Δv)(Δr*Δr − σ^2)
        dvdr = dx*dvx + dy*dvy
        if dvdr > 0: 
            return math.inf
        dvdv = dvx*dvx + dvy*dvy
        drdr = dx*dx + dy*dy
        sigma = self.radius + that.radius
        
        d = (dvdr*dvdr) - (dvdv * (drdr - sigma*sigma))
        if d <= 0: 
            return math.inf

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
        # J = 2 * mass[i] * mass[j] (Δv * Δr) / σ(mass[i] + mass[j])
        J = 2 * self.mass * that.mass * dvdr / ((self.mass + that.mass) * dist)
        fx = J * dx / dist
        fy = J * dy / dist
        self.vx = self.vx + (fx / self.mass)
        self.vy = self.vy + (fy / self.mass)
        that.vx = self.vx - (fx / that.mass)
        that.vy = self.vy - (fy / that.mass)

        # increase collision count
        self.collisionCnt = self.collisionCnt + 1
        that.collisionCnt = that.collisionCnt + 1

    # adjusts velocity of object after colliding with vertical wall
    def bounceOffVWall(self):
        self.vx = -1 * self.vx;
        self.collisionCnt = self.collisionCnt + 1

    # adjusts velocity of object after colliding with horizontal wall
    def bounceOffHWall(self):
        self.vy = -1 * self.vy; 
        self.collisionCnt = self.collisionCnt + 1

