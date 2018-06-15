import unittest
import math
from graphics import *
from collision import *
from particles import *

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.window = GraphWin('Test', 100, 100)
        self.particles = []
        self.particles.append(Particle(self.window, x = 30.0, y = 5.0, vx = 10, vy = 0))
        self.particles.append(Particle(self.window, x = 50.0, y = 5.0, vx = -10, vy = 0))
        self.cs = CollisionSystem(self.particles)

    def test_checkEvtsInPQ(self):        
        for x in self.cs.pq:
            self.assertTrue(x.isValid())

    def test_checkPQlen(self):
        self.cs.pq[0].a.bounceOff(self.cs.pq[0].b)
        self.assertTrue(len(self.cs.pq) == 4) # 1 particle collision + 1 wall collisions each
        
    def test_checkEvtsAfterBounce(self):
        self.cs.pq[0].a.bounceOff(self.cs.pq[0].b)
        self.assertFalse(self.cs.pq[0].isValid())

class TestParticle(unittest.TestCase):
    def setUp(self):
        self.window = GraphWin('Test', 200, 200)
        self.a = Particle(self.window, x = 47.5, y = 5.0, vx = 10.0, vy = 0, radius = 5.0)
        self.b = Particle(self.window, x = 50.0, y = 5.0, vx = -10.0, vy = 0, radius = 5.0)
        self.c = Particle(self.window, x = 10.0, y = 10.0, vx = 0, vy = 0, radius = 5.0)
        self.d = Particle(self.window, x = 100, y = 75.0, vx = 0.0, vy = 10, radius = 5.0)
        self.e = Particle(self.window, x = 100, y = 500.0, vx = 0.0, vy = -10, radius = 5.0)
        self.f = Particle(self.window, width = 20.0, height = 20.0, shape = "Rect")

    def test_bounceOff(self):
        avx = self.a.vx
        avy = self.a.vy
        bvx = self.b.vx
        bvy = self.b.vy
        total = avx + avy + bvx + bvy
        self.a.bounceOff(self.b)
        newTotal = self.a.vx + self.a.vy + self.b.vx + self.b.vy
        self.assertTrue(total == newTotal)

    def test_timeToHit(self):
        dx = 50.0 - 47.5
        dv = -10.0 - 10
        drdr = dx * dx
        dvdv = dv * dv
        dvdr = dx * dv
        
        sigma = 5.0 + 5.0
        d = (dvdr*dvdr) - (dvdv * (drdr - sigma*sigma))
        t = -1.0 * (dvdr + math.sqrt(d)) / dvdv

        self.assertTrue(self.a.timeToHit(self.b) == -0.375)
        self.assertTrue(self.a.timeToHit(self.b) == t)
        self.assertTrue(self.a.timeToHit(self.a) == math.inf)
        self.assertTrue(self.a.timeToHit(self.c) == math.inf)
        self.assertTrue(self.a.timeToHit(self.d) == math.inf)
        self.assertTrue(self.a.timeToHit(self.e) == math.inf)

    def test_timeToHitVWall(self):
        leftWallX = 0
        rightWallX = self.window.width
        self.assertTrue(self.a.timeToHitVWall() == (rightWallX - 5 - 47.5)/10.0)
        self.assertTrue(self.b.timeToHitVWall() == (leftWallX + 5 - 50.0)/-10.0)
        self.assertTrue(self.c.timeToHitVWall() == math.inf)
        self.assertTrue(self.d.timeToHitVWall() == math.inf)
        self.assertTrue(self.e.timeToHitVWall() == math.inf)
    
    def test_timeToHitHWall(self):
        topWallY = 0
        botWallY = self.window.height
        self.assertTrue(self.a.timeToHitHWall() == math.inf)
        self.assertTrue(self.b.timeToHitHWall() == math.inf)
        self.assertTrue(self.c.timeToHitHWall() == math.inf)
        self.assertTrue(self.d.timeToHitHWall() == (botWallY - 5 - 75)/10.0)
        self.assertTrue(self.e.timeToHitHWall() == (topWallY + 5 - 500)/-10.0)

    def test_distFromCenter(self):
        self.assertTrue(self.a.distFromCenter(0) == 5.0)
        self.assertTrue(self.a.distFromCenter(45) == 5.0)
        self.assertTrue(round(self.f.distFromCenter(0), 2) == 10.0) # right
        self.assertTrue(round(self.f.distFromCenter(90), 2) == 10.0) # top
        self.assertTrue(round(self.f.distFromCenter(180), 2) == 10.0) # left
        self.assertTrue(round(self.f.distFromCenter(270), 2) == 10.0) # bottom
        self.assertTrue(round(self.f.distFromCenter(360), 2) == 10.0) # bottom
        self.assertTrue(round(self.f.distFromCenter(45), 6) == 14.142136)
        self.assertTrue(round(self.f.distFromCenter(225), 6) == 14.142136)
        self.assertTrue(round(self.f.distFromCenter(-45), 6) == 14.142136)

    def test_calcAngle(self):
        self.assertTrue(self.a.calcAngle(0, 0) == 90) # default
        self.assertTrue(self.a.calcAngle(10, 0) == 0) # top
        self.assertTrue(self.a.calcAngle(0, 10) == 90) # right
        self.assertTrue(self.a.calcAngle(0, -10) == 270) # left 
        self.assertTrue(self.a.calcAngle(-10, 0) == 180) # bot
        self.assertTrue(self.a.calcAngle(0, 100) == 90) # dist doesn't matter if horizontal 
        self.assertTrue(self.a.calcAngle(100, 0) == 0) # dist doesn't matter if vertical 
        self.assertTrue(self.a.calcAngle(10, 10) == 45) # top right 
        self.assertTrue(self.a.calcAngle(10, -10) == 315) # top left 
        self.assertTrue(self.a.calcAngle(-10, -10) == 225) # bot left 
        self.assertTrue(self.a.calcAngle(-10, 10) == 135) # bot right 
        self.assertTrue(self.a.calcAngle(10, 10) + 180 == self.a.calcAngle(-10, -10))

class TestCollisionSys(unittest.TestCase):
    def setUp(self):
        self.window = GraphWin('Test', 200, 200)
        self.a = Particle(self.window, x = 25.5, y = 5.0, vx = 10.0, vy = 0)
        self.b = Particle(self.window, x = 50.0, y = 5.0, vx = -10.0, vy = 0)
        self.c = Particle(self.window, x = 10.0, y = 10.0, vx = 0, vy = 0, radius = 5.0)
        self.d = Particle(self.window, x = 100, y = 75.0, vx = 0.0, vy = 10, radius = 5.0)
        self.e = Particle(self.window, x = 100, y = 500.0, vx = 0.0, vy = -10, radius = 5.0)
        particles = [self.a, self.b, self.c, self.d, self.e]
        self.cs = CollisionSystem(particles)

    def test_predict(self):
        # no particle
        sz = len(self.cs.pq)
        self.cs.predict(None, 0, 10000)
        self.assertTrue(sz == len(self.cs.pq))

        # no limit
        sz = len(self.cs.pq)
        self.cs.predict(self.a, 0, math.inf)
        self.assertTrue(len(self.cs.pq) == (sz + 7)) # 2 wall collision + 5 other particles 

        # with limit
        sz = len(self.cs.pq)
        self.cs.predict(self.a, 0, 10000)
        self.assertTrue(len(self.cs.pq) == (sz + 2)) # only two possible collisions (1 wall, 1 particle) 

if __name__ == '__main__':
    unittest.main()