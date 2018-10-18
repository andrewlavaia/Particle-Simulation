import unittest
import math
from queue import Queue
from graphics import *
from collision import *
from particles import *

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.window = GraphWin('Test', 100, 100)
        self.particles = []
        self.particles.append(Particle(0, self.window, x = 30.0, y = 5.0, vx = 10, vy = 0))
        self.particles.append(Particle(1, self.window, x = 50.0, y = 5.0, vx = -10, vy = 0))
        self.walls = []
        self.walls.append(VWall(0))
        self.walls.append(VWall(self.window.width))
        self.walls.append(HWall(0))
        self.walls.append(HWall(self.window.height - 20.0))
        self.result_q = Queue() 

    def test_checkEvtsInQ(self):
        CollisionSystem.predict(self.particles[0], 0, math.inf, self.particles, self.walls, self.result_q)
        while not self.result_q.empty():
            evt = self.result_q.get()
            self.assertTrue(evt.isValid(self.particles))

    def test_checkQlen(self):
        CollisionSystem.predict(self.particles[0], 0, math.inf, self.particles, self.walls, self.result_q)
        self.assertTrue(self.result_q.qsize() == 5) # 1 particle collision + 4 wall collisions
        
    def test_checkEvtsAfterBounce(self):
        CollisionSystem.predict(self.particles[0], 0, math.inf, self.particles, self.walls, self.result_q)
        evt = self.result_q.get()
        self.particles[0].bounceOff(self.particles[1])
        self.assertFalse(evt.isValid(self.particles))

class TestParticle(unittest.TestCase):
    def setUp(self):
        self.window = GraphWin('Test', 200, 200)
        self.a = Particle(0, self.window, x = 47.5, y = 5.0, vx = 10.0, vy = 0, radius = 5.0)
        self.b = Particle(1, self.window, x = 50.0, y = 5.0, vx = -10.0, vy = 0, radius = 5.0)
        self.c = Particle(2, self.window, x = 10.0, y = 10.0, vx = 0, vy = 0, radius = 5.0)
        self.d = Particle(3, self.window, x = 100, y = 75.0, vx = 0.0, vy = 10, radius = 5.0)
        self.e = Particle(4, self.window, x = 100, y = 500.0, vx = 0.0, vy = -10, radius = 5.0)
        self.f = Particle(5, self.window, width = 20.0, height = 20.0, x = 160, y = 500, vx = 0, vy = 0, shape = "Rect")
        self.g = Particle(6, self.window, width = 40.0, height = 20.0, x = 160, y = 700, vx = 0, vy = 0, shape = "Rect")

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
        self.assertTrue(self.a.timeToHit(self.b) == t)
        self.assertTrue(self.a.timeToHit(self.b) == -0.375)
        self.assertTrue(self.a.timeToHit(self.a) == math.inf)
        self.assertTrue(self.a.timeToHit(self.c) == math.inf)
        self.assertTrue(self.a.timeToHit(self.d) == math.inf)
        self.assertTrue(self.a.timeToHit(self.e) == math.inf)

    def test_timeToHitVWall(self):
        wall1 = VWall(0)
        wall2 = VWall(self.window.width)
        leftWallX = 0
        rightWallX = self.window.width
        self.assertTrue(self.a.timeToHitVWall(wall2) == (rightWallX - 5 - 47.5)/10.0)
        self.assertTrue(self.b.timeToHitVWall(wall1) == (leftWallX + 5 - 50.0)/-10.0)
        self.assertTrue(self.c.timeToHitVWall(wall2) == math.inf)
        self.assertTrue(self.d.timeToHitVWall(wall2) == math.inf)
        self.assertTrue(self.e.timeToHitVWall(wall2) == math.inf)
    
    def test_timeToHitHWall(self):
        menu_height = 20.0
        wall1 = HWall(0)
        wall2 = HWall(self.window.height - menu_height)
        topWallY = 0
        botWallY = self.window.height - menu_height
        self.assertTrue(self.a.timeToHitHWall(wall1) == math.inf)
        self.assertTrue(self.b.timeToHitHWall(wall1) == math.inf)
        self.assertTrue(self.c.timeToHitHWall(wall1) == math.inf)
        self.assertTrue(self.d.timeToHitHWall(wall2) == (botWallY - 5 - 75)/10.0)
        self.assertTrue(self.e.timeToHitHWall(wall1) == (topWallY + 5 - 500)/-10.0)

    def test_timeToLineSegment(self):
        # vertical walls
        line1 = LineSegment(Point(0.0, 0.0), Point(0.0, self.window.height))
        line2 = LineSegment(Point(self.window.width, 0.0), Point(self.window.width, self.window.height))
        leftWallX = 0
        rightWallX = self.window.width
        self.assertTrue(self.a.timeToHitLineSegment(line2) == (rightWallX - 5 - 47.5)/10.0)
        self.assertTrue(self.b.timeToHitLineSegment(line1) == (leftWallX + 5 - 50.0)/-10.0)
        self.assertTrue(self.c.timeToHitLineSegment(line2) == math.inf)
        self.assertTrue(self.d.timeToHitLineSegment(line2) == math.inf)
        self.assertTrue(self.e.timeToHitLineSegment(line2) == math.inf)

        # horizontal walls
        menu_height = 20.0
        line3 = LineSegment(Point(0.0, 0.0), Point(self.window.width, 0.0))
        line4 = LineSegment(
                Point(0.0, self.window.height - menu_height), 
                Point(self.window.width, self.window.height - menu_height)
        )
        topWallY = 0
        botWallY = self.window.height - menu_height
        self.assertTrue(self.a.timeToHitLineSegment(line3) == math.inf)
        self.assertTrue(self.b.timeToHitLineSegment(line3) == math.inf)
        self.assertTrue(self.c.timeToHitLineSegment(line3) == math.inf)
        self.assertTrue(self.d.timeToHitLineSegment(line4) == (botWallY - 5 - 75)/10.0)
        self.assertTrue(self.e.timeToHitLineSegment(line3) == (topWallY + 5 - 500)/-10.0)

        # vertical line
        p1 = Particle(0, self.window, x = 45.0, y = 10.0, vx = 10.0, vy = 0, radius = 5.0)
        p2 = Particle(0, self.window, x = 45.0, y = 19.0, vx = 10.0, vy = 0, radius = 5.0)
        p3 = Particle(0, self.window, x = 45.0, y = 20.0, vx = 10.0, vy = 0, radius = 5.0)
        p4 = Particle(0, self.window, x = 45.0, y = 30.0, vx = 10.0, vy = 0, radius = 5.0)
        p5 = Particle(0, self.window, x = 45.0, y = 40.0, vx = 10.0, vy = 0, radius = 5.0)
        p6 = Particle(0, self.window, x = 45.0, y = 41.0, vx = 10.0, vy = 0, radius = 5.0)
        p7 = Particle(0, self.window, x = 45.0, y = 50.0, vx = 10.0, vy = 0, radius = 5.0)

        line5 = LineSegment(Point(60.0, 20.0), Point(60.0, 40.0))
        self.assertTrue(p1.timeToHitLineSegment(line5) == math.inf)
        self.assertTrue(p2.timeToHitLineSegment(line5) == math.inf) # this should still hit edge of circle...
        self.assertTrue(p3.timeToHitLineSegment(line5) == (15.0 - 5.0)/10.0)
        self.assertTrue(p4.timeToHitLineSegment(line5) == (15.0 - 5.0)/10.0)
        self.assertTrue(p5.timeToHitLineSegment(line5) == (15.0 - 5.0)/10.0)
        self.assertTrue(p6.timeToHitLineSegment(line5) == math.inf) # this should still hit edge of circle...
        self.assertTrue(p7.timeToHitLineSegment(line5) == math.inf)

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

        self.assertTrue(round(self.g.distFromCenter(0), 2) == 20.0) # right
        self.assertTrue(round(self.g.distFromCenter(90), 2) == 10.0) # top
        self.assertTrue(round(self.g.distFromCenter(180), 2) == 20.0) # left
        self.assertTrue(round(self.g.distFromCenter(270), 2) == 10.0) # bottom
        self.assertTrue(round(self.g.distFromCenter(45), 6) == 14.142136) 
        self.assertTrue(round(self.g.distFromCenter(37.5), 6) == 16.426796) 
        self.assertTrue(round(self.g.distFromCenter(30), 2) == 20.0) 

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

    def test_line_intersection(self):
        p0 = Point(0.0, 0.0)
        p1 = Point(5.0, 0.0)
        p2 = Point(3.0, 3.0)
        p3 = Point(3.0, -3.0)
        p4 = Point(10.0, 0.0)
        p5 = Point(6.0, 0.0)
        p6 = Point(8.0, 0.0)
        line1 = LineSegment(p0, p1)
        line2 = LineSegment(p2, p3)
        line3 = LineSegment(p1, p0)
        line4 = LineSegment(p1, p4)
        line5 = LineSegment(p1, p5)
        line6 = LineSegment(p5, p6)

        # intersection, associative, commutative
        cp1 = line1.intersection(line2)
        cp2 = line2.intersection(line1)
        cp3 = line3.intersection(line2)
        cp4 = line2.intersection(line3)
        self.assertTrue(
            cp1.x == 3 and cp1.y == 0 
            and cp2.x == 3 and cp2.y == 0
            and cp3.x == 3 and cp3.y == 0
            and cp4.x == 3 and cp4.y == 0
        )

        # non-intersecting lines
        cp5 = line4.intersection(line2)
        self.assertTrue(cp5 == None)

        # overlapping lines 
        cp6 = line4.intersection(line5)
        cp7 = line5.intersection(line6)
        cp8 = line1.intersection(line4)
        self.assertTrue(cp6 == None and cp7 == None and cp8 == None)

class TestCollisionSys(unittest.TestCase):
    def setUp(self):
        self.window = GraphWin('Test', 200, 200)
        self.a = Particle(0, self.window, x = 25.5, y = 5.0, vx = 10.0, vy = 0)
        self.b = Particle(1, self.window, x = 50.0, y = 5.0, vx = -10.0, vy = 0)
        self.c = Particle(2, self.window, x = 10.0, y = 10.0, vx = 0, vy = 0, radius = 5.0)
        self.d = Particle(3, self.window, x = 100, y = 75.0, vx = 0.0, vy = 10, radius = 5.0)
        self.e = Particle(4, self.window, x = 100, y = 500.0, vx = 0.0, vy = -10, radius = 5.0)
        self.particles = [self.a, self.b, self.c, self.d, self.e]
        self.walls = []
        self.walls.append(VWall(0))
        self.walls.append(VWall(self.window.width))
        self.walls.append(HWall(0))
        self.walls.append(HWall(self.window.height - 20.0))
        self.result_q = Queue()

    def test_predict(self):
        # no particle
        CollisionSystem.predict(None, 0, 10000, self.particles, self.walls, self.result_q)
        self.assertTrue(self.result_q.qsize() == 0)

        # no limit
        sz = self.result_q.qsize()
        CollisionSystem.predict(self.a, 0, math.inf, self.particles, self.walls, self.result_q)
        self.assertTrue(self.result_q.qsize() == (sz + 8)) # 4 wall collisions + 4 other particles 

        # with limit
        sz = self.result_q.qsize()
        CollisionSystem.predict(self.a, 0, 10000, self.particles, self.walls, self.result_q)
        self.assertTrue(self.result_q.qsize() == (sz + 2)) # only two possible collisions (1 wall, 1 particle) 

if __name__ == '__main__':
    unittest.main()