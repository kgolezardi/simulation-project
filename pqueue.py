import heapq
import itertools


class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.counter = itertools.count()
        self.entry_finder = {}
        self._size = 0

    def size(self):
        return self._size

    def push(self, priority, x):
        count = next(self.counter)
        entry = [priority, count, x]
        self.entry_finder[x] = entry
        heapq.heappush(self.heap, entry)
        self._size += 1

    def empty(self):
        return self._size == 0

    def pop(self):
        while len(self.heap) > 0:
            priority, count, x = heapq.heappop(self.heap)
            if x is not None:
                del self.entry_finder[x]
                self._size -= 1
                return priority, x
        raise KeyError

    def remove(self, x):
        entry = self.entry_finder.pop(x)
        self._size -= 1
        entry[-1] = None

