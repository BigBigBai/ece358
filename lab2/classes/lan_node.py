from collections import deque


class LanNode:
    def __init__(self, events):
        self.events = deque(events)
        self.collisions = 0
        self.busy_count = 0

        # Virtual event time that tracks the actual time of the first event in the queue.
        # This is done so that multiple events are not updated for each node, which greatly
        # decreases the runtime of the code
        self.next_event_time = events[0].event_time
