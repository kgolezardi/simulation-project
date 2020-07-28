from enums import Log
from pqueue import PriorityQueue


class WaitingQueue:
    def __init__(self):
        self.queue = PriorityQueue()
        self.log = []

    def push(self, current_time, p):
        self.queue.push([p.healthy, current_time], p)
        self.log.append((Log.ENTER, p.healthy, current_time))

    def empty(self):
        return self.queue.empty()

    def pop(self, current_time):
        p = self.queue.pop()[-1]
        self.log.append((Log.EXIT, p.healthy, current_time))
        return p

    def remove(self, current_time, p):
        self.queue.remove(p)
        self.log.append((Log.EXIT, p.healthy, current_time))

    def size(self):
        return self.queue.size()
