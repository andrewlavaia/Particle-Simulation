'''Program: bouncingballs.py
Provides simple event simulation using a
priority queue to check for collisions
'''

import random
import math
import heapq
from graphics import  *

class Ball:
    def __init__(self, x, y, vx, vy, r, windowWidth, windowHeight):
        self.x = x                          # position
        self.y = y                         
        self.vx = vx                        # velocity  
        self.vy = vy
        self.radius = r                     # size of Ball in pixels
        self.mass = 1                       # used for collision physics
        self.maxWidth = windowWidth         # highest possible x position
        self.maxHeight = windowHeight       # highest possible y position
        self.collisionCnt = 0               # number of pending collisions
 
    # Moves ball by time * speed
    def move(self, dt):
        # if collision with wall, reverse speed 
        if self.x + (self.vx * dt) < self.radius or self.x + (self.vx * dt) > self.maxWidth - self.radius:
            self.vx = -self.vx;
        if self.y + (self.vy * dt) < self.radius or self.y + (self.vy * dt) > self.maxHeight - self.radius:
            self.vy = -self.vy;

        # move ball by speed * delta time   
        self.x = self.x + (self.vx * dt)
        self.y = self.y + (self.vy * dt)

    # Calculates time until collision with another Ball
    def timeToHit(that):
        if self == that:
            return math.inf 
        # distance
        dx = that.x - self.x
        dy = that.y - self.y;
        
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
        d = (dvdr*dvdr) - dvdv * (drdr - sigma*sigma)
        if d < 0:
            return math.inf;
        return -(dvdr + math.sqrt(d)) / dvdv

    def bounceOff(that):
        dx = that.x - self.x
        dy = that.y - self.y;
        dvx = that.vx - self.vx 
        dvy = that.vy - self.vy
        dvdr = dx*dvx + dy*dvy
        dist = self.radius + that.radius

        # calculate impulse J
        # J = 2 * mass[i] * mass[j] (Δv * Δr) / σ(mass[i] + mass[j])
        J = 2 * self.mass * that.mass * dvdr / ((self.mass + that.mass) * dist)
        Jx = J * dx / dist
        Jy = J * dy / dist
        self.vx += Jx / self.mass
        self.vy += Jy / self.mass
        that.vx -= Jx / that.mass
        that.vy -= Jy / that.mass

        # increase collision count
        self.collisionCnt = self.collisionCnt + 1
        that.collisionCnt = that.collisionCnt + 1

class Event:
    def __init__(self, t, a, b):
        self.time = t    
        self.a = a
        self.b = b
        self.countA = 0
        self.countB = 0

    def compareTo(that):
        return self.time - that.time

    def isValid():
        pass

class CollisionSystem:
    pq = []             # priority queue    
    t = 0.0             # simulation clock time 
    balls = []          # List of balls

    # Adds all predicted collision times with this object to priority queue
    def predict(a):
        if a == None:
            return

        # insert collision time with all other balls into priority queue
        for ball in balls:
            dt = a.timeToHit(ball)
            heapq.heappush(pq, Event(t + dt, a, balls[i]))

        # insert time to hit walls into priority queue

    # inserts predicted collision times into priority queue
    # and processes the events
    def simulate():
        for ball in balls:
            predict(ball)
        heapq.heappush(pq, Event(0, None, None)) # needed so pq is never empty


def main():
    win = GraphWin('Bouncing Balls', 500, 500)
    win.setBackground('white')

    # Create a list of random balls
    balls = []
    n = 50
    for i in range(1, n):
        ballRadius = 5
        randX = random.uniform(0 + ballRadius, win.width - ballRadius)
        randY = random.uniform(0 + ballRadius, win.height - ballRadius)
        randVX = random.uniform(-1, 1)
        randVY = random.uniform(-1, 1)
        balls.append(Ball(randX, randY, randVX, randVY, ballRadius, win.width, win.height))
    
    # Create a list of Circles
    circles = []
    for ball in balls:
        c = Circle(Point(ball.x, ball.y), ball.radius)
        circles.append(c)
        c.draw(win)
 

    # Simulation Loop
    while win.checkMouse() == None: 
        i = 0
        for ball in balls:
            ball.move(2)
            circles[i].move(ball.x - circles[i].getCenter().getX(), ball.y - circles[i].getCenter().getY())
            i = i + 1
    
    win.close
    
main()