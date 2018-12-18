'''
Module: collisions.py
Defines CollisionSystem which handles 
collision events between two particles.
'''

from worker import WorkRequest
import multiprocessing as mp
import time
import heapq

# Defines an Event that will occur at time t between particles a and b
# if neither a & b are None -> collision with another particle
# if one of a or b is None -> collision with wall
# if both a & b are None -> do nothing
class Event:
    def __init__(self, t, a, b, cntA, cntB):
        self.time = t  # time from start of simulation
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
        if (self.b is not None and isinstance(self.b, int) and self.countB != particles[self.b].collisionCnt):
            return False
        return True

# Collision System is used to predict when and how particles will collide
class CollisionSystem:
    # Inserts all predicted collisions with a given particle as Events into the queue.
    def predict(a, next_logic_tick, limit, particles, walls, result_q):
        if a is None:
            return
        
        # insert predicted collision with every other 
        # particle as an event into the priority queue 
        # if collision time is between next_logic_tick and limit
        for b in particles:
            if a == b:
                continue
            dt = a.timeToHit(b)
            minTime = max(next_logic_tick - 25.0, next_logic_tick + dt) # collision shouldn't occur before current next_logic_tick
            evt = Event(minTime, a.index, b.index, a.collisionCnt, b.collisionCnt)

            if next_logic_tick + dt <= limit: 
                result_q.put(evt)
        
        # insert collision time with every wall into the queue
        for wall in walls:
            dt = a.timeToHitWall(wall)
            minTime = max(next_logic_tick - 25.0, next_logic_tick + dt) # collision shouldn't occur before current next_logic_tick            
            evt = Event(minTime, a.index, wall, a.collisionCnt, None)
            if next_logic_tick + dt <= limit:
                result_q.put(evt)

    def processCompletedWork(result_q, pq):
        while not result_q.empty():
            evt = result_q.get()
            heapq.heappush(pq, evt)

    def processWorkRequests(work_q, result_q): 
        # print("{0} started".format(mp.current_process().name))
        while True:
            work = work_q.get() # blocks automatically when q is empty
            # print("{0} is working. {1} requests remaining.".format(mp.current_process().name, work_q.qsize()))
            CollisionSystem.predict(work.particles[work.particle_index], work.time, work.limit, work.particles, work.walls, result_q)

    def processCollisionEvents(particles, walls, pq, nextLogicTick, work_q, result_q):  
        lastEvt = None
        while len(pq) > 0 and pq[0].time < nextLogicTick:
            evt = heapq.heappop(pq)
            
            if evt.isValid(particles) and (lastEvt is None or evt != lastEvt):
                lastEvt = evt # prevents infinite collision errors
            else:
                continue

            a = evt.a
            b = evt.b
            if isinstance(b, int):
                particles[a].bounceOff(particles[b])
                work_q.put(WorkRequest(a, nextLogicTick, 10000, particles, walls))
                work_q.put(WorkRequest(b, nextLogicTick, 10000, particles, walls))    
            elif b.wall_type == "VWall":
                particles[a].bounceOffVWall()
                work_q.put(WorkRequest(a, nextLogicTick, 10000, particles, walls))
            elif b.wall_type == "HWall":
                particles[a].bounceOffHWall()
                work_q.put(WorkRequest(a, nextLogicTick, 10000, particles, walls))
            elif b.wall_type == "LineSegment":
                particles[a].bounceOffLineSegment(b)
                work_q.put(WorkRequest(a, nextLogicTick, 10000, particles, walls))