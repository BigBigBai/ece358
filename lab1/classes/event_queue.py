from collections import deque
from numpy import arange

from utils import constants as c, utils
from classes.events import ArrivalEvent, ObserverEvent


class EventQueue:
    def __init__(self, min_rho, max_rho, queue_size=None):
        # Initialize rho range, optional max queue size (for M/M/1/K)
        self.min_rho = min_rho
        self.max_rho = max_rho
        self.queue_size = queue_size

        # The queue of events
        self.events = []

        # Counts for each event type (N_a, N_d, N_o)
        self.counts = {
            c.EVENT_ARRIVAL: 0,
            c.EVENT_DEPARTURE: 0,
            c.EVENT_OBSERVER: 0
        }

        # Other counts (idle observations, dropped packets)
        self.idle_t = 0
        self.loss_t = 0

        # Timers for running the DES
        self.timer = 0 # Current simulation time
        self.curr_service_timer = 0 # Tracks the departure of the previous packet (used to calculate current departure)

        # Packet queue (records order in which packets should be processed)
        self.queue = deque()

        # Sum of queue sizes recorded at observation events (used to calculate E[N])
        self.queue_size_sum = 0

    ##
    # Runs the DES using the current EventQueue parameters (rho range and max queue size)
    # Parameters: none
    # Returns: none
    #
    def run_des(self):
        for rho in arange(self.min_rho, self.max_rho + 0.05, 0.1):
            # Reset the DES for each iteration
            self.clean_des()

            # Calculate rates for event inter-arrivals
            lam = rho * c.C / c.L
            a = lam * 5

            # Populate the event queue
            self.generate_arrival_events(lam)
            self.generate_observer_events(a)

            # Sort in reverse so that self.events.pop() is an O(1) operation
            self.events.sort(key=lambda e: e.event_time, reverse=True)

            # While there are still events to process and the simulation is not complete, process the next event
            while not (len(self.events) == 0 and len(self.queue) == 0) and self.timer < c.T:
                self.process_next_event()

            # Compute and print metrics
            self.print_results(rho, lam)

    ##
    # Resets the EventQueue properties to prepare for the next iteration
    # Parameters: none
    # Returns: none
    #
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

    ##
    # Generates a list of arrival events and adds it to the events queue
    # Parameters: lam -> lambda, determines the mean of the exponential distribution
    # Returns: none (modifies events queue)
    #
    def generate_arrival_events(self, lam):
        curr_time = 0
        arrival_events = []
        while curr_time < c.T:
            inter_arrival_time = utils.get_random_variable(1 / lam)
            curr_time += inter_arrival_time

            # Service time is also determine via an exponential distribution with mean = L
            length = utils.get_random_variable(c.L)
            service_time = length / c.C

            arrival_events.append(ArrivalEvent(curr_time, service_time))

        self.events += arrival_events

    ##
    # Generates a list of observer events and adds it to the events queue
    # Parameters: a -> alpha, determines the mean of the exponential distribution
    # Returns: none (modifies events queue)
    #
    def generate_observer_events(self, a):
        curr_time = 0
        observer_events = []
        while curr_time < c.T:
            curr_time += utils.get_random_variable(1 / a)
            observer_events.append(ObserverEvent(curr_time))

        self.events += observer_events

    ##
    # Determines which event to process next, updates appropriate counters and timers
    # Parameters: none
    # Returns: none
    #
    def process_next_event(self):
        # If there is a packet in the packet queue that can be serviced before the next event, pop and update timers
        # The curr_service_timer now reflects the departure time of this packet
        # This action is recorded as a departure, but no departure event is created
        if len(self.queue) > 0 and self.curr_service_timer + self.queue[0] < self.events[-1].event_time:
            self.timer += self.queue.popleft()
            self.curr_service_timer = self.timer
            self.counts[c.EVENT_DEPARTURE] += 1
        # Otherwise, process the next event (pop from event queue and update timer)
        else:
            curr_event = self.events.pop()
            self.timer = curr_event.event_time

            # Event is either arrival or observer
            if curr_event.event_type == c.EVENT_ARRIVAL:

                # If the event is an arrival and the packet buffer is full, only increment the loss counter
                if self.queue_size and len(self.queue) >= self.queue_size:
                    self.loss_t += 1

                # Otherwise, add the packet to the buffer
                else:
                    self.queue.append(curr_event.service_time)

            else:

                # Record the size of the packet queue and increment idle count if necessary
                self.queue_size_sum += len(self.queue)
                if len(self.queue) == 0:
                    self.idle_t += 1

            self.counts[curr_event.event_type] += 1

    ##
    # Computes and prints the metrics for the current iteration
    # Also prints the M/M/1/K-specific metrics if a max queue size was given
    # Parameters: rho -> the traffic intensity
    #             lam -> lambda, the rate parameter
    # Returns: none
    #
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
