import itertools
from heapq import heappop, heappush


class Heap:
    def __init__(self):
        self.pq = []  # list of entries arranged in a heap
        self.entry_finder = {}  # mapping of tasks to entries
        self.open = set()
        self.REMOVED = "<removed-task>"  # placeholder for a removed task
        self.counter = itertools.count()  # unique sequence count

    def __len__(self):
        return len(self.pq)

    def add_node(self, priority, task):
        # 'Add a new task or update the priority of an existing task'
        if task in self.entry_finder:
            self.remove_task(task)
        count = next(self.counter)
        entry = [priority, count, task]
        self.entry_finder[task] = entry
        heappush(self.pq, entry)
        self.open.add(task)

    def remove_task(self, task):
        # 'Mark an existing task as REMOVED.  Raise KeyError if not found'
        entry = self.entry_finder.pop(task)
        entry[-1] = self.REMOVED

    def pop_task(self):
        # 'Remove and return the lowest priority task. Raise KeyError if empty'
        while self.pq:
            priority, _, task = heappop(self.pq)
            if task is not self.REMOVED:
                del self.entry_finder[task]
                self.open.remove(task)
                return task
        raise KeyError("pop from an empty priority queue")


class HeapDijks(Heap):
    def pop_task(self):
        # 'Remove and return the lowest priority task. Raise KeyError if empty'
        while self.pq:
            priority, _, task = heappop(self.pq)
            if task is not self.REMOVED:
                del self.entry_finder[task]
                return priority, task
        raise KeyError("pop from an empty priority queue")
