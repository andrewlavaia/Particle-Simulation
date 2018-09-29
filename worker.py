import multiprocessing as mp

work_queue = mp.Queue()

def processQueue(work_queue, cs):
    print("{0} started".format(mp.current_process().name))
    while (True):
        if work_queue.empty():
            continue

        print("{0} has grabbed an item off the queue".format(mp.current_process().name))

        evt, nextLogicTick = work_queue.get()
        print(evt, nextLogicTick)

        a = evt.a
        b = evt.b
        if a is not None and b is not None: 
            a.bounceOff(b)
            cs.predict(a, nextLogicTick, 10000)
            cs.predict(b, nextLogicTick, 10000)
        elif a is not None and b is None:
            a.bounceOffVWall()
            cs.predict(a, nextLogicTick, 10000)
        elif a is None and b is not None:
            b.bounceOffHWall()
            cs.predict(b, nextLogicTick, 10000)