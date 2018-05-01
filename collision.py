'''
Module: collisions.py
Defines CollisionSystem which handles 
collision events between two particles.
'''

import heapq

# Defines an Event that will occur at time t between particles a and b
# if neither a & b are None -> collision with another particle
# if one of a or b is None -> collision with wall
# if both a & b are None -> do nothing
class Event:
    def __init__(self, t, a, b):
        self.time = t    
        self.a = a
        self.b = b
        if a is not None:
            self.countA = a.collisionCnt
        else:
            self.countA = -1

        if b is not None:
            self.countB = b.collisionCnt
        else:
            self.countB = -1
    
    # comparator
    def __lt__(self, that):
        return self.time <= that.time

    # check if event was invalidated from prior collision
    def isValid(self):
        if (self.a is not None and self.countA != self.a.collisionCnt):
            return False
        if (self.b is not None and self.countB != self.b.collisionCnt):
            return False
        return True

# Collision System is used to predict when two particles will
# colide and store those events in a min priority queue.
# Also used to run simulation.
class CollisionSystem:
    def __init__(self, particles):
        self.pq = []                		# priority queue         
        self.particles = particles    		# list of particles as a reference

        # initalize pq with initial predictions
        for particle in particles:
        	self.predict(particle, 0.0, 10000)	

    # Adds all predicted collision times with this particle to priority queue
    def predict(self, a, simTime, limit):
        if a is None:
            return
        
        # insert predicted collision time with every other 
        # particle into the priority queue
        for b in self.particles:
            dt = a.timeToHit(b)
            minTime = -1/60.0 # should match FPS
            evt = Event(simTime + dt, a, b)
            if simTime + dt <= limit and dt > minTime:
                heapq.heappush(self.pq, evt)
        
        # insert collision time with every wall into 
        # the priority queue
        dt = a.timeToHitVWall()
        evt = Event(simTime + dt, a, None)
        if simTime + dt <= limit:
            heapq.heappush(self.pq, evt)
        dt = a.timeToHitHWall()
        evt = Event(simTime + dt, None, a)
        if simTime + dt <= limit:   
            heapq.heappush(self.pq, evt) 

    # Processes all events in priority queue that
    # occurred before a given time
    def processEvents(self, simTime):
    	while len(self.pq) > 0 and self.pq[0].time < simTime:
            # grab top event from priority queue
            evt = heapq.heappop(self.pq)

            # skip event if no longer valid
            if not evt.isValid():
                continue

            # process collisions 
            a = evt.a
            b = evt.b
            if a is not None and b is not None: 
                a.bounceOff(b)
                self.predict(a, simTime, 10000)
                self.predict(b, simTime, 10000)
            elif a is not None and b is None:
                a.bounceOffVWall()
                self.predict(a, simTime, 10000)
            elif a is None and b is not None:
                b.bounceOffHWall()
                self.predict(b, simTime, 10000)
            elif a is None and b is None:
                pass