'''
Module: collisions.py
Defines CollisionSystem which handles 
collision events between two particles.
'''

import worker
import time
import heapq

# Defines an Event that will occur at time t between particles a and b
# if neither a & b are None -> collision with another particle
# if one of a or b is None -> collision with wall
# if both a & b are None -> do nothing
class Event:
    def __init__(self, t, a, b, cntA, cntB):
        self.time = t    
        self.a = a
        self.b = b
        self.countA = cntA
        self.countB = cntB
    
    # comparators
    def __lt__(self, that):
        return self.time <= that.time
    def __eq__(self, that):
        return self.time == that.time and self.a == that.a and self.b == that.b

    # check if event was invalidated from prior collision
    def isValid(self, particles):
        if (self.a is not None and self.countA != particles[self.a].collisionCnt):
            return False
        if (self.b is not None and self.countB != particles[self.b].collisionCnt):
            return False
        return True

# Collision System is used to predict when two particles will
# colide and store those events in a min priority queue.
# Also used to run simulation.
class CollisionSystem:
    # def __init__(self, particles):
    #     self.pq = []                		# priority queue   
    #     self.particles = particles    		# list of particles as a reference
        
    #     # initialize last event
    #     assert(len(particles) >= 2)
    #     self.lastEvt = Event(-1.0, self.particles[0], self.particles[1])

    #     # initalize pq with initial predictions
    #     for particle in particles:
    #     	self.predict(particle, 0.0, 10000, particles, pq)	

    # Inserts all predicted collisions with a given particle as Events 
    # into priority queue. Event time is the time since simulation began.
    def predict(a, simTime, limit, particles, work_queue):
        if a is None:
            return
        
        # insert predicted collision with every other 
        # particle as an event into the priority queue 
        # if collision time is between simTime and limit
        for b in particles:
            dt = a.timeToHit(b)
            minTime = max(simTime - 1.0, simTime + dt) # collision shouldn't occur before current simTime
            evt = Event(minTime, a.index, b.index, a.collisionCnt, b.collisionCnt)

            if simTime + dt <= limit: 
                work_queue.put(evt)
        
        # insert collision time with every wall into the priority queue
        dt = a.timeToHitVWall()
        evt = Event(simTime + dt, a.index, None, a.collisionCnt, None)
        if simTime + dt <= limit:
            work_queue.put(evt)
        dt = a.timeToHitHWall()
        evt = Event(simTime + dt, None, a.index, None, a.collisionCnt)
        if simTime + dt <= limit:   
            work_queue.put(evt)

    def processWorkQueue(work_queue, pq):
        while not work_queue.empty():
            evt = work_queue.get()
            heapq.heappush(pq, evt)

    def processCollisionEvents(particles, pq, nextLogicTick, work_queue):  
        lastEvt = None
        while len(pq) > 0 and pq[0].time < nextLogicTick:
            evt = heapq.heappop(pq)
            
            if evt.isValid(particles) and (lastEvt is None or evt != lastEvt):
                lastEvt = evt 
            else:
                continue

            a = evt.a
            b = evt.b
            if a is not None and b is not None:
                particles[a].bounceOff(particles[b])
                CollisionSystem.predict(particles[a], nextLogicTick, 10000, particles, work_queue)
                CollisionSystem.predict(particles[b], nextLogicTick, 10000, particles, work_queue)
            elif a is not None and b is None:
                particles[a].bounceOffVWall()
                CollisionSystem.predict(particles[a], nextLogicTick, 10000, particles, work_queue)
            elif a is None and b is not None:
                particles[b].bounceOffHWall()
                CollisionSystem.predict(particles[b], nextLogicTick, 10000, particles, work_queue)


