from collections import deque
from numpy import arange

from utils import constants as c, utils
from classes.events import ArrivalEvent, ObserverEvent


class EventQueue:
    def __init__(self, min_rho, max_rho, queue_size=None):
        self.min_rho = min_rho
        self.max_rho = max_rho
        self.queue_size = queue_size

        self.events = []
        self.counts = {
            c.EVENT_ARRIVAL: 0,
            c.EVENT_DEPARTURE: 0,
            c.EVENT_OBSERVER: 0
        }
        self.idle_t = 0
        self.loss_t = 0
        self.timer = 0
        self.curr_service_timer = 0
        self.queue = deque()
        self.queue_size_sum = 0

    def run_des(self):
        for rho in arange(self.min_rho, self.max_rho + 0.05, 0.1):
            self.clean_des()

            lam = rho * c.C / c.L
            a = lam * 5

            self.generate_arrival_events(lam)
            self.generate_observer_events(a)
            self.events.sort(key=lambda e: e.event_time, reverse=True)

            while not (len(self.events) == 0 and len(self.queue) == 0) and self.timer < c.T:
                self.process_next_event()

            self.print_results(rho, lam)

    def clean_des(self):
        self.events = []
        self.counts = {
            c.EVENT_ARRIVAL: 0,
            c.EVENT_DEPARTURE: 0,
            c.EVENT_OBSERVER: 0
        }
        self.idle_t = 0
        self.loss_t = 0
        self.timer = 0
        self.curr_service_timer = 0
        self.queue = deque()
        self.queue_size_sum = 0

    def generate_arrival_events(self, lam):
        curr_time = 0
        arrival_events = []
        while curr_time < c.T:
            inter_arrival_time = utils.get_random_variable(1 / lam)
            curr_time += inter_arrival_time

            length = utils.get_random_variable(c.L)
            service_time = length / c.C
            arrival_events.append(ArrivalEvent(curr_time, service_time))

        self.events += arrival_events

    def generate_observer_events(self, a):
        curr_time = 0
        observer_events = []
        while curr_time < c.T:
            curr_time += utils.get_random_variable(1 / a)
            observer_events.append(ObserverEvent(curr_time))

        self.events += observer_events

    def process_next_event(self):
        if len(self.queue) > 0 and self.curr_service_timer + self.queue[0] < self.events[-1].event_time:
            self.timer += self.queue.popleft()
            self.curr_service_timer = self.timer
            self.counts[c.EVENT_DEPARTURE] += 1
        else:
            curr_event = self.events.pop()
            self.timer = curr_event.event_time
            if curr_event.event_type == c.EVENT_ARRIVAL:
                if self.queue_size and len(self.queue) >= self.queue_size:
                    self.loss_t += 1
                else:
                    self.queue.append(curr_event.service_time)
            else:
                self.queue_size_sum += len(self.queue)
                if len(self.queue) == 0:
                    self.idle_t += 1
            self.counts[curr_event.event_type] += 1

    def print_results(self, rho, lam):
        print("\nrho: %.2f" % rho)
        if self.queue_size:
            print("K:", self.queue_size)
        print("lambda: %.0f" % lam)
        print("N_a:", self.counts[c.EVENT_ARRIVAL])
        print("N_d:", self.counts[c.EVENT_DEPARTURE])
        print("N_o:", self.counts[c.EVENT_OBSERVER])
        print("idle count:", self.idle_t)
        if self.queue_size:
            print("dropped count:", self.loss_t)
        print("E[N]:", self.queue_size_sum * 1.0 / self.counts[c.EVENT_OBSERVER])
        print("P_IDLE:", self.idle_t * 1.0 / self.counts[c.EVENT_OBSERVER])
        if self.queue_size:
            print("P_LOSS:", self.loss_t * 1.0 / self.counts[c.EVENT_ARRIVAL])
