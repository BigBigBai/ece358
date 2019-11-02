from collections import deque


class LanNode:
    def __init__(self, events):
        self.events = deque(events)
        self.collisions = 0
        self.busy_count = 0
