from graphics import Point
import math_utils

class WallBase:
    pass
    
class VWall(WallBase):
    def __init__(self, x):
        self.wall_type = "VWall"
        self.x = x

class HWall(WallBase):    
    def __init__(self, y):
        self.wall_type = "HWall"
        self.y = y

class LineSegment(WallBase):
    def __init__(self, point_0, point_1):
        self.id = id(self)
        self.wall_type = "LineSegment"
        self.p0 = point_0
        self.p1 = point_1
        self.dx = self.p1.x - self.p0.x
        self.dy = self.p1.y - self.p0.y
        self.angle = math_utils.angle(self.dy, self.dx)
        self.length = math_utils.pythag(self.dx, self.dy)

    def intersection(self, line):
        # https://stackoverflow.com/a/1968345/3160610
        p0 = self.p0
        p1 = self.p1
        q0 = line.p0
        q1 = line.p1
        s0 = Point(p1.x - p0.x, p1.y - p0.y)
        s1 = Point(q1.x - q0.x, q1.y - q0.y)

        try:
            s = (-s0.y * (p0.x - q0.x) + s0.x * (p0.y - q0.y)) / (-s1.x * s0.y + s0.x * s1.y)
            t = ( s1.x * (p0.y - q0.y) - s1.y * (p0.x - q0.x)) / (-s1.x * s0.y + s0.x * s1.y)            

        except ZeroDivisionError:
            # lines overlap so multiple collision points exist
            return p0

        if s >= 0 and s <= 1 and t >= 0 and t <= 1:
            collision_point = Point(p0.x + (t * s0.x), p0.y + (t * s0.y))
            return collision_point
        
        return None
    
    def __eq__(self, other):
        return self.id == other.id
