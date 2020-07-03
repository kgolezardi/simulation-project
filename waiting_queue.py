from pqueue import PriorityQueue


class WaitingQueue:
    ENTER = 0
    EXIT = 1

    def __init__(self):
        self.queue = PriorityQueue()
        self.log = []

    def push(self, current_time, p):
        self.queue.push([p.healthy, current_time], p)
        self.log.append((self.ENTER, current_time))

    def empty(self):
        return self.queue.empty()

    def pop(self, current_time):
        v = self.queue.pop()[-1]
        self.log.append((self.EXIT, current_time))
        return v

    def remove(self, current_time, p):
        self.queue.remove(p)
        self.log.append((self.EXIT, current_time))

    def size(self):
        return self.queue.size()

    def summerize_log(self):
        points = []
        count = 0
        last_time = 0
        for event, time in self.log:
            if time != last_time:
                points.append((last_time, count))
            last_time = time
            if event == self.ENTER:
                count += 1
            else:
                count -= 1
        points.append((last_time, count))
        return points
