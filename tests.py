import unittest
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
        window = GraphWin('Test', 200, 200)
        self.a = Particle(window, x = 47.5, y = 5.0, vx = 10.0, vy = 0)
        self.b = Particle(window, x = 50.0, y = 5.0, vx = -10.0, vy = 0)

    def test_bounceOff(self):
        avx = self.a.vx
        avy = self.a.vy
        bvx = self.b.vx
        bvy = self.b.vy
        total = avx + avy + bvx + bvy
        self.a.bounceOff(self.b)
        newTotal = self.a.vx + self.a.vy + self.b.vx + self.b.vy
        self.assertTrue(total == newTotal)

if __name__ == '__main__':
    unittest.main()