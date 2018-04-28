'''
Module: particles.py
Defines different types of particles
for use in particle simulation
'''

import math
import random
from graphics import Point, Circle 

# Defines a Ball object which can be used in the Collision Simulator
class Ball:
    def __init__(self, x, y, vx, vy, r, windowWidth, windowHeight):
        self.x = x                          # position
        self.y = y                         
        self.vx = vx                        # velocity  
        self.vy = vy
        self.radius = r                     # size of Ball in pixels
        self.mass = 1                       # used for collision physics
        self.circle = Circle(Point(x, y), r)
        self.maxX = windowWidth         	# highest possible x position
        self.maxY = windowHeight       		# highest possible y position
        
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
    def draw(self, window):
        self.circle.draw(window)
    
    # Moves Circle to current position on window 
    def render(self, window):    
        self.circle.move(self.x - self.circle.getCenter().getX(), self.y - self.circle.getCenter().getY())

    # Calculates time (in ms) until collision with another Ball
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
            return (self.maxY - self.radius - self.y) / self.vy
        elif (self.vy < 0):
            return (0.0 + self.radius - self.y) / self.vy
        elif (self.vy == 0):
            return math.inf

    # calculates time (in ms) until collision with vertical wall
    def timeToHitVWall(self):
        if (self.vx > 0):
            return (self.maxX - self.radius - self.x) / self.vx
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

