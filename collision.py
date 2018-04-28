'''Module: collisions.py
Defines CollisionSystem which provides a 
a simulation method to visually depict 
collisions between two particles.
'''

import time
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
    FPS = 120          

    def __init__(self, particles):
        self.pq = []                		# priority queue    
        self.evtTime = 0.0         			# simulation clock time      
        self.particles = list(particles)    # defensive copy of list of particles
        self.lastFrameTime = time.time()	# time that last frame occurred


    # Adds all predicted collision times with this particle to priority queue
    def predict(self, a, limit):
        if a is None:
            return
        
        # insert predicted collision time with every other 
        # particle into the priority queue
        for b in self.particles:
            dt = a.timeToHit(b)
            evt = Event(self.evtTime + dt, a, b)
            if self.evtTime + dt <= limit:
                heapq.heappush(self.pq, evt)
        
        # insert collision time with every wall into 
        # the priority queue
        dt = a.timeToHitVWall()
        evt = Event(self.evtTime + dt, a, None)
        if self.evtTime + dt <= limit:
            heapq.heappush(self.pq, evt)
        dt = a.timeToHitHWall()
        evt = Event(self.evtTime + dt, None, a)
        if self.evtTime + dt <= limit:   
            heapq.heappush(self.pq, evt) 
        

    # Pre-populates priority queue with all predicted
    # collisions and performs the initial draw call for
    # each particle (each particle is only drawn once)
    def populatePQ(self, window):
        for particle in self.particles:
            particle.draw(window)
            self.predict(particle, 10000)

    # Processes the events in priority queue until
    # pq is empty or time limit reached    
    def simulate(self, window, limit):
        while self.evtTime < limit:
            # dt is the time delta in seconds (float)
            currentTime = time.time()
            elapsed = currentTime - self.lastFrameTime
            self.lastFrameTime = currentTime
            
            # force updates to be constant
            fixedFrameTime = 1.0/CollisionSystem.FPS
            sleepTime = fixedFrameTime - elapsed
            if sleepTime > 0:
                time.sleep(sleepTime)
            
            # update game logic
            for particle in self.particles:
                particle.move(fixedFrameTime)  # moves each particle in linear line   

            self.evtTime = self.evtTime + fixedFrameTime

            # process all events that occurred last frame
            while len(self.pq) > 0 and self.pq[0].time < self.evtTime:
                # grab top event from priority queue
                evt = heapq.heappop(self.pq)

                # skip event if no longer valid
                if not evt.isValid():
                    continue
                a = evt.a
                b = evt.b

                # process collisions 
                if a is not None and b is not None: 
                    a.bounceOff(b)
                    self.predict(a, 10000)
                    self.predict(b, 10000)
                elif a is not None and b is None:
                    a.bounceOffVWall()
                    self.predict(a, 10000)
                elif a is None and b is not None:
                    b.bounceOffHWall()
                    self.predict(b, 10000)
                elif a is None and b is None:
                    pass

            # draw updates to window
            self.redraw(window)

            # check if user wants to end simulation
            if window.checkMouse() is not None:
                return

    # Update position of all particles on window
    def redraw(self, window):
        for particle in self.particles:
            particle.update(window)  