'''
Module: collisions.py
Defines CollisionSystem which handles 
collision events between two particles.
'''

import heapq
import worker

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
    
    # comparators
    def __lt__(self, that):
        return self.time <= that.time
    def __eq__(self, that):
        return self.time == that.time

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
        
        # initialize last event
        assert(len(particles) >= 2)
        self.lastEvt = Event(-1.0, self.particles[0], self.particles[1])

        # initalize pq with initial predictions
        for particle in particles:
        	self.predict(particle, 0.0, 10000)	

    # Inserts all predicted collisions with a given particle as Events 
    # into priority queue. Event time is the time since simulation began.
    def predict(self, a, simTime, limit):
        if a is None:
            return
        
        # insert predicted collision with every other 
        # particle as an event into the priority queue 
        # if collision time is between simTime and limit
        for b in self.particles:
            dt = a.timeToHit(b)
            minTime = max(simTime - 1.0, simTime + dt) # collision shouldn't occur before current simTime
            evt = Event(minTime, a, b)

            if simTime + dt <= limit: 
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

    # Checks if event needs to be processed and adds it to the work_queue
    def queueCollisionEvents(self, nextLogicTick):   
        while len(self.pq) > 0 and self.pq[0].time < nextLogicTick:
            # grab top event from priority queue
            evt = heapq.heappop(self.pq)
            
            if evt.isValid() and evt != self.lastEvt:
                self.lastEvt = evt 
            else:
                continue
            
            work_item = (evt, nextLogicTick)
            worker.work_queue.put(work_item)
