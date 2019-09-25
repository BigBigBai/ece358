from collections import deque
from copy import copy
from numpy import arange

from utils import constants as c, utils
from classes.events import ArrivalEvent, DepartureEvent, ObserverEvent


class EventQueue:
    def __init__(self, min_rho, max_rho, step_size, max_queue_size=None):
        # Initialize rho range, optional max queue size (for M/M/1/K)
        self.min_rho = min_rho
        self.max_rho = max_rho
        self.step_size = step_size
        self.max_queue_size = max_queue_size

        # The queue of events
        self.events = deque()

        # Counts for each event type (N_a, N_d, N_o)
        self.counts = {
            c.EVENT_ARRIVAL: 0,
            c.EVENT_DEPARTURE: 0,
            c.EVENT_OBSERVER: 0
        }

        # Other counts/timers (idle time, dropped packets)
        self.idle_time = 0
        self.cumulative_idle_time = 0
        self.idle_start = 0
        self.loss_count = 0

        # Timers for running the DES
        self.timer = 0 # Current simulation time
        self.curr_service_timer = 0 # Tracks the departure of the previous packet (used to calculate current departure)

        # Current size of the packet queue
        self.queue_size = 0

        # Sum of queue sizes recorded at observation events (used to calculate E[N])
        self.queue_size_sum = 0

    ##
    # Runs the DES using the current EventQueue parameters (rho range and max queue size)
    # Parameters: none
    # Returns: none
    #
    def run_des(self):
        results = []
        for rho in arange(self.min_rho, self.max_rho + 0.05, self.step_size):
            # Reset the DES for each iteration
            self.clean_des()

            # Calculate rates for event inter-arrivals
            lam = rho * c.C / c.L
            a = lam * 5

            # Populate the event queue
            self.generate_arrival_events(lam)
            if self.max_queue_size:
                self.generate_departure_events_mm1k(self.events)
            else:
                self.generate_departure_events_mm1(self.events)
            self.generate_observer_events(a)

            # While there are still events to process and the simulation is not complete, process the next event
            self.queue_size = 0
            while not len(self.events) == 0 and self.timer < c.T:
                self.process_next_event()

            # Compute and print metrics
            metrics = self.compute_results(rho, self.max_queue_size)
            self.print_results(metrics)

            results.append(metrics)

        return results

    ##
    # Resets the EventQueue properties to prepare for the next iteration
    # Parameters: none
    # Returns: none
    #
    def clean_des(self):
        self.events = deque()
        self.counts = {
            c.EVENT_ARRIVAL: 0,
            c.EVENT_DEPARTURE: 0,
            c.EVENT_OBSERVER: 0
        }
        self.idle_time = 0
        self.cumulative_idle_time = 0
        self.idle_start = 0
        self.loss_count = 0
        self.timer = 0
        self.curr_service_timer = 0
        self.queue_size = 0
        self.queue_size_sum = 0

    ##
    # Generates a list of arrival events and adds it to the events queue
    # Parameters: lam -> lambda, determines the mean of the exponential distribution
    # Returns: none (modifies events queue)
    #
    def generate_arrival_events(self, lam):
        curr_time = 0
        arrival_events = deque()

        while curr_time < c.T:
            inter_arrival_time = utils.get_random_variable(1 / lam)
            curr_time += inter_arrival_time

            arrival_events.append(ArrivalEvent(curr_time))

        self.merge_into_events_queue(arrival_events)

    ##
    # Generates a list of departure events based on the arrival events and adds it to the events queue
    # This implementation is for the M/M/1 queue - no need to simulate the packet queue
    # Parameters: arrival_events -> The list of arrival events
    # Returns: none (modifies events queue)
    #
    def generate_departure_events_mm1(self, arrival_events):
        # Timer that keeps track of the last packet to be serviced (i.e. the previous departure)
        curr_service_time = 0
        departure_events = deque()

        for ae in arrival_events:
            # Service time is determined via an exponential distribution with mean = L
            length = utils.get_random_variable(c.L)
            service_time = length / c.C

            # If the next event arrives before the previous one departs, then the departure time of the next event is 
            # calculated from the previous departure
            # Otherwise, the packet queue is empty and the packet can be serviced as soon as it arrives
            if ae.event_time <= curr_service_time:
                departure_time = curr_service_time + service_time
            else:
                departure_time = ae.event_time + service_time

            # Update the previous departure timer
            curr_service_time = departure_time

            departure_events.append(DepartureEvent(departure_time))

        self.merge_into_events_queue(departure_events)

    ##
    # Generates a list of departure events based on the arrival events and adds it to the events queue
    # This implementation is for the M/M/1/K queue - the packet queue is simulated to determine which events are
    # actually serviced.
    # Parameters: arrival_events -> The list of arrival events
    # Returns: none (modifies events queue)
    #
    def generate_departure_events_mm1k(self, arrival_events):
        events_queue = copy(arrival_events)
        packet_queue = deque()
        curr_service_time = 0
        service_time_diff = 0
        timer = 0
        departure_events = deque()

        while (len(events_queue) > 0 or len(packet_queue) > 0) and curr_service_time < c.T:
            # If the first packet in the queue can finish servicing before the next arrival, finish servicing the packet
            if len(packet_queue) > 0 and \
                    (len(events_queue) == 0 or events_queue[0].event_time >= service_time_diff + packet_queue[0]):
                service_time = packet_queue.popleft()
                # Update timers
                timer += service_time
                curr_service_time = timer
                service_time_diff = curr_service_time
                # Add new event
                departure_events.append(DepartureEvent(curr_service_time))

            # Otherwise, attempt to add the arriving packet to the packet queue
            else:
                curr_event = events_queue.popleft()
                timer = curr_event.event_time
                # Update the service time of the packet in the queue to represent the amount of service time remaining
                # from the perspective of the arrival
                if len(packet_queue) > 0:
                    packet_queue[0] -= timer - service_time_diff
                    service_time_diff += timer - service_time_diff
                # If the queue is not full, add the packet
                if len(packet_queue) < self.max_queue_size:
                    # Service time is determined via an exponential distribution with mean = L
                    length = utils.get_random_variable(c.L)
                    service_time = length / c.C
                    packet_queue.append(service_time)

        self.merge_into_events_queue(departure_events)

    ##
    # Generates a list of observer events and adds it to the events queue
    # Parameters: a -> alpha, determines the mean of the exponential distribution
    # Returns: none (modifies events queue)
    #
    def generate_observer_events(self, a):
        curr_time = 0
        observer_events = deque()
        while curr_time < c.T:
            curr_time += utils.get_random_variable(1 / a)
            observer_events.append(ObserverEvent(curr_time))

        self.merge_into_events_queue(observer_events)

    ##
    # Merges a queue of events into the global event queue, maintaining sorting order by event time.
    # Parameters: new_events -> the event queue that is being merged into the global queue.
    # Returns: none
    #
    def merge_into_events_queue(self, new_events):
        combined_events = deque()
        while len(self.events) > 0 and len(new_events) > 0:
            if self.events[0].event_time <= new_events[0].event_time:
                combined_events.append(self.events.popleft())
            else:
                combined_events.append(new_events.popleft())
        if len(self.events) > 0:
            combined_events += self.events
        else:
            combined_events += new_events
        self.events = combined_events

    ##
    # Determines which event to process next, updates appropriate counters and timers
    # Parameters: none
    # Returns: none
    #
    def process_next_event(self):
        curr_event = self.events.popleft()
        self.timer = curr_event.event_time

        # Action is based on event type
        if curr_event.event_type == c.EVENT_ARRIVAL:
            # If the event is an arrival and the packet buffer is full, only increment the loss counter
            if self.max_queue_size and self.queue_size >= self.max_queue_size:
                self.loss_count += 1

            # Otherwise, add the packet to the buffer
            else:
                self.queue_size += 1
            self.idle_reset(curr_event)

        elif curr_event.event_type == c.EVENT_DEPARTURE:
            self.queue_size -= 1
            self.idle_reset(curr_event)

        else:
            # Record the size of the packet queue and increment idle count if necessary
            self.queue_size_sum += self.queue_size
            if self.queue_size == 0:
                self.idle_time = curr_event.event_time - self.idle_start

        self.counts[curr_event.event_type] += 1

    ##
    # Resets the idle timers
    # Parameters: event -> the current event
    # Returns: none
    #
    def idle_reset(self, event):
        self.cumulative_idle_time += self.idle_time
        self.idle_time = 0
        self.idle_start = event.event_time

    ##
    # Computes the metrics for the current iteration
    # Checks whether M/M/1/K-specific metrics should be generated
    # Parameters: rho -> the traffic intensity
    #             K -> the max queue size
    # Returns: metrics -> the corresponding metrics to be returned
    #
    def compute_results(self, rho, K=None):
        E_N = str(self.queue_size_sum * 1.0 / self.counts[c.EVENT_OBSERVER])
        if K:
            P_LOSS = str(self.loss_count * 1.0 / self.counts[c.EVENT_ARRIVAL])
            return [str(K), "%.2f" % rho, E_N, P_LOSS]
        else:
            P_IDLE = str(self.cumulative_idle_time * 1.0 / c.T)
            return ["%.2f" % rho, E_N, P_IDLE]

    ##
    # Prints the metrics for the current iteration
    # Parameters: metrics -> the metrics to be printed
    # Returns: none
    #
    def print_results(self, metrics):
        print(', '.join(metrics))
