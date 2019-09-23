class QueueObject:
    def __init__(self, event_time, event_type):
        self.event_time = event_time
        self.event_type = event_type


class ArrivalEvent(QueueObject):
    def __init__(self, event_time, service_time):
        super().__init__(event_time, 'a')
        self.service_time = service_time


class ObserverEvent(QueueObject):
    def __init__(self, event_time):
        super().__init__(event_time, 'o')
