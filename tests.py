import unittest
from graphics import *
from collision import *
from particles import *

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.window = GraphWin('Particle Simulation', 10, 10)
        self.particles = []
        for i in range(0, 5):
            self.particles.append(Particle(self.window))
        self.cs = CollisionSystem(self.particles)

    def test_checkPQ(self):
        for x in self.cs.pq:
            self.assertTrue(x.isValid())
        self.assertTrue(len(self.cs.pq) == 30) # 4 particle collisions + 2 wall collisions each
        self.cs.pq[0].a.bounceOff(self.cs.pq[0].b)
        self.assertFalse(self.cs.pq[0].isValid())

if __name__ == '__main__':
    unittest.main()