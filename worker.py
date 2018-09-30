import multiprocessing as mp
import time

def processQueue(particles, pq, nextLogicTick):
    print("{0} started".format(mp.current_process().name))
    time.sleep(1)
    while (True):
        while not pq.empty(): # and pq[0].time < nextLogicTick.value:
            print(mp.current_process().name, len(particles), pq.qsize(), nextLogicTick.value)

            # grab top event from priority queue
            # print(pq.qsize())
            evt = pq.get()
            # evt = heapq.heappop(pq)
            print("{0} grabbed event with {1} and {2} off the queue".format(mp.current_process().name, evt.a, evt.b))

            # if evt.isValid() and evt != self.lastEvt:
            #     self.lastEvt = evt 
            # else:
            #     continue

            if not evt.isValid():
                continue
            
            a = evt.a
            b = evt.b

            if a is not None and b is not None: 
                a.bounceOff(b)
                # CollisionSystem.predict(a, nextLogicTick, 10000, particles, pq)
                # CollisionSystem.predict(b, nextLogicTick, 10000, particles, pq)
            elif a is not None and b is None:
                a.bounceOffVWall()
                # CollisionSystem.predict(a, nextLogicTick, 10000, particles, pq)
            elif a is None and b is not None:
                b.bounceOffHWall()
                # CollisionSystem.predict(b, nextLogicTick, 10000, particles, pq)