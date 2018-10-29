'''
Module: particles.py
Defines particles for use in particle simulation
'''

import math
import random
from graphics import Point, Circle, Rectangle, color_rgb
from walls import LineSegment
import math_utils

# Defines a Particle object which can be used in the Collision Simulator
class Particle:
    def __init__(self, index, window,
            radius = None, x = None, y = None,
            vx = None, vy = None, mass= None,
            color = None, shape = "Circle", width = None, height = None):

        self.index = index
        self.window_width = window.width
        self.window_height = window.height

        # set default values
        if radius == None and shape == "Circle":
            radius = 5.0
        if shape == "Circle":
            width = radius * 2.0
        elif width == None:
            width = 10.0
        if shape == "Circle":
            height = radius * 2.0
        elif height == None:
            height = 10.0
        if x == None:
            x = random.uniform(0 + width/2.0, self.window_width - height/2.0)
        if y == None:
            y = random.uniform(0 + width/2.0, self.window_height - height/2.0)
        if vx == None:
            vx = random.uniform(-200.0, 200.0)
        if vy == None:
            vy = random.uniform(-200.0, 200.0)
        if mass == None:
            mass = 1.0
        if color == None or color == "random":
            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)
            color = color_rgb(red, green, blue)

        self.x = x                      # position
        self.y = y
        self.vx = vx                    # speed
        self.vy = vy
        self.mass = mass                # used for collision physics
        self.radius = radius
        self.width = width
        self.height = height
        self.shape_type = shape
        self.color = color

        # set limits on speed and collisions
        # self.max_speed = 1000000.0

        self.collisionCnt = 0               # number of collisions - used to
                                            # check whether event has become
                                            # invalidated

    # equality comparator
    def __eq__(self, other):
        return self.index == other.index

    # Moves particle by time * speed
    def move(self, dt):
        self.x = self.x + (self.vx * dt)
        self.y = self.y + (self.vy * dt)

    def direction(self):
        return math_utils.degrees_clockwise(self.vy, self.vx)

    def distFromCenter(self, deg):
        if self.shape_type == "Circle":
            return self.radius

        twoPI = math.pi * 2
        theta = deg * math.pi / 180

        while theta < -math.pi:
            theta += twoPI

        while theta > math.pi:
            theta -= twoPI

        rectAtan = math.atan2(self.height, self.width)
        tanTheta = math.tan(theta)

        region = 0
        if (theta > -rectAtan) and (theta <= rectAtan):
            region = 1
        elif (theta > rectAtan) and (theta <= (math.pi - rectAtan)):
            region = 2
        elif (theta > (math.pi - rectAtan)) or (theta <= -(math.pi - rectAtan)):
            region = 3
        else:
            region = 4

        edgePoint = Point(self.width/2.0, self.height/2.0)
        xFactor = 1
        yFactor = 1

        if region == 1 or region == 2:
            yFactor = -1
        elif region == 3 or region == 4:
            xFactor = -1

        if region == 1 or region == 3:
            edgePoint.x = edgePoint.x + (xFactor * (self.width / 2.0))                # "Z0"
            edgePoint.y = edgePoint.y + (yFactor * (self.width / 2.0) * tanTheta)
        else:
            edgePoint.x = edgePoint.x + (xFactor * (self.height / (2.0 * tanTheta)))  # "Z1"
            edgePoint.y = edgePoint.y + (yFactor * (self.height /  2.0))

        return math_utils.pythag(edgePoint.x - (self.width/2.0),
                                edgePoint.y - (self.height/2.0))

    # Calculates time until collision with another Particle

    # Need a new collision detection algorithm for rectangles...
    #  This algo is not computing correctly for long rectangles
    #  because it is computing the angle from the center
    #  and not the edge (ie particle traveling straight up
    #  won't hit left or right edges of long rectangle because
    #  the angle calc tells it to use the vertical distance)
    def timeToHit(self, that):
        # distance
        dx = that.x - self.x # switch to distance between nearest points?
        dy = that.y - self.y

        # speed
        dvx = that.vx - self.vx
        dvy = that.vy - self.vy

        # collision prediction
        dvdr = dx*dvx + dy*dvy
        if dvdr >= 0:
            return math.inf
        dvdv = dvx*dvx + dvy*dvy
        drdr = dx*dx + dy*dy

        dist_from_center1 = self.distFromCenter(self.direction())
        dist_from_center2 = that.distFromCenter(180.0 - that.direction())
        sigma = dist_from_center1 + dist_from_center2

        d = (dvdr*dvdr) - (dvdv * (drdr - sigma*sigma))
        if d <= 0:
            return math.inf

        if dvdv == 0:
            return math.inf # both particles are stationary

        return -1 * (dvdr + math.sqrt(d)) / dvdv

    # calculates time (in ms) until collision with a wall
    def timeToHitWall(self, wall):
        if wall.wall_type == "HWall":
            return self.timeToHitHWall(wall)
        elif wall.wall_type == "VWall":
            return self.timeToHitVWall(wall)
        else:
            return self.timeToHitLineSegment(wall)

    # calculates time (in ms) until collision with horizontal wall
    def timeToHitHWall(self, wall):
        if self.y < wall.y and self.vy > 0:
            return (wall.y - self.height/2 - self.y) / self.vy
        elif self.y > wall.y and self.vy < 0:
            return (wall.y + self.height/2 - self.y) / self.vy
        else:
            return math.inf

    # calculates time (in ms) until collision with vertical wall
    def timeToHitVWall(self, wall):
        if self.x < wall.x and self.vx > 0:
            return (wall.x - self.width/2 - self.x) / self.vx
        elif self.x > wall.x and self.vx < 0:
            return (wall.x + self.width/2 - self.x) / self.vx
        else:
            return math.inf

    def closestPointOnLineSegment(self, line):
        dx = self.x - line.p0.x
        dy = self.y - line.p0.y
        
        # get unit vector
        unit_x = line.dx / line.length
        unit_y = line.dy / line.length

        # calculate dot product and check end points
        dot = (dx * unit_x) + (dy * unit_y)
        if dot < 0:
            return line.p0
        elif dot > line.length:
            return line.p1
        
        # project vector onto line
        x_dist = dot * unit_x        
        y_dist = dot * unit_y

        return Point(line.p0.x + x_dist, line.p0.y + y_dist)
        
    def timeToHitLineSegment(self, line):
        # get closest point of circle to line segment
        line_point = self.closestPointOnLineSegment(line)
        dx = line_point.x - self.x
        dy = line_point.y - self.y
        if (dx * dx + dy * dy) < (self.radius * self.radius): # point is within circle
            return math.inf 
        deg = math_utils.degrees_clockwise(dy, dx)
        adj0 = Point(self.radius * math.sin(math.radians(deg)), self.radius * math.cos(math.radians(deg)))
        p0 = Point(self.x + adj0.x, self.y + adj0.y) 

        # get two extra points that are 90 degrees from traveling angle
        deg = self.direction()
        adj1 = Point(self.radius * math.sin(math.radians(deg + 90.0)), self.radius * math.cos(math.radians(deg + 90.0)))
        adj2 = Point(self.radius * math.sin(math.radians(deg - 90.0)), self.radius * math.cos(math.radians(deg - 90.0)))
        p1 = Point(self.x + adj1.x, self.y + adj1.y) 
        p2 = Point(self.x + adj2.x, self.y + adj2.y) 

        scalar_factor = 1000.0
        q0 = Point(
            self.x + adj0.x + (scalar_factor * self.vx),
            self.y + adj0.y + (scalar_factor * self.vy)
        )
        q1 = Point(
            self.x + adj1.x + (scalar_factor * self.vx),
            self.y + adj1.y + (scalar_factor * self.vy)
        )
        q2 = Point(
            self.x + adj2.x + (scalar_factor * self.vx),
            self.y + adj2.y + (scalar_factor * self.vy)
        )

        projected_path0 = LineSegment(p0, q0)
        projected_path1 = LineSegment(p1, q1)
        projected_path2 = LineSegment(p2, q2)
        collision_point0 = projected_path0.intersection(line)
        collision_point1 = projected_path1.intersection(line)
        collision_point2 = projected_path2.intersection(line)

        t0, t1, t2 = math.inf, math.inf, math.inf
        if collision_point0 is not None:
            if self.vx != 0:
                d0 = collision_point0.x - p0.x
                t0 = d0 / self.vx
            else:
                d0 = collision_point0.y - p0.y
                t0 = d0 / self.vy
        if collision_point1 is not None:
            if self.vx != 0:
                d1 = collision_point1.x - p1.x
                t1 = d1 / self.vx
            else:
                d1 = collision_point1.y - p1.y
                t1 = d1 / self.vy
        if collision_point2 is not None:
            if self.vx != 0:
                d2 = collision_point2.x - p2.x
                t2 = d2 / self.vx
            else:
                d2 = collision_point2.y - p2.y
                t2 = d2 / self.vy

        return min(t0, t1, t2)

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
        dist = math_utils.pythag(dx, dy)

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

    def bounceOffLineSegment(self, line):
        angle = line.angle
        precision = 10

        # compute normal vector
        normal_x = -round(math.sin(angle), precision)
        normal_y = round(math.cos(angle), precision)

        # dot product
        dot = normal_x * self.vx + normal_y * self.vy

        self.vx = self.vx - 2 * dot * normal_x
        self.vy = self.vy - 2 * dot * normal_y

        self.collisionCnt += 1

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

    # double force for "that" particle
    # needed otherwise collisions with this particle lose energy
    def moveByForce(self, that, fx, fy):
        that.vx = that.vx - (fx / self.mass)
        that.vy = that.vy - (fy / self.mass)

    def bounceOff(self, that):
        pass
    def bounceOffVWall(self):
        pass
    def bounceOffHWall(self):
        pass

class RectParticle(Particle):
    def __init__(self, window, radius = None,
        x = None, y = None, vx = None, vy = None,
        mass = None, color = None, width = None, height = None):

        super().__init__(window, radius, x, y, vx, vy, mass, color,
            shape = "Rect", width = width, height = height)


# Defines a shape object to be used for drawing the 
# corresponding Particle object with the same index
class ParticleShape():
    def __init__(self, index, window, particle):
        self.index = index
        self.window = window
        self.x = particle.x
        self.y = particle.y
        self.color = particle.color
        self.radius = particle.radius
        self.height = particle.height
        self.width = particle.width

        if particle.shape_type == "Circle":
            self.shape = Circle(Point(self.x, self.y), self.radius)
        elif particle.shape_type == "Rect":
            self.shape = Rectangle(Point(self.x - self.width/2.0, self.y - self.height/2.0),
                Point(self.x + self.width/2.0, self.y + self.height/2.0))
        else:
            assert(False)

        self.shape.setFill(self.color)
        self.shape.setOutline(self.color)

    def draw(self):
        self.shape.draw(self.window)

    def render(self):
        self.shape.move(self.x - self.shape.getCenter().getX(), self.y - self.shape.getCenter().getY())

class ParticleFactory:
    def __init__(self, window, particles, particle_shapes):
        self.window = window
        self.particles = particles
        self.particle_shapes = particle_shapes
        self.count = 0

    def create(self, **kwargs):
        self.particles.append(Particle(self.count, self.window, **kwargs))
        self.particle_shapes.append(ParticleShape(self.count, self.window, self.particles[self.count]))
        self.count += 1

