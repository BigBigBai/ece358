class QueueObject:
    def __init__(self, event_time, event_type):
        self.event_time = event_time
        self.event_type = event_type


class ArrivalEvent(QueueObject):
    def __init__(self, event_time):
        super().__init__(event_time, 'a')


class DepartureEvent(QueueObject):
    def __init__(self, event_time):
        super().__init__(event_time, 'd')


class ObserverEvent(QueueObject):
    def __init__(self, event_time):
        super().__init__(event_time, 'o')
