#!/usr/bin/env python3

# DES Simulator for an M/M/1 queue (i.e. infinite buffer)

from collections import deque
from numpy import arange

from utils import constants as c, utils
from classes.events import ArrivalEvent, ObserverEvent


for rho in arange(1.2, 1.25, 0.1):

    events = []

    lam = rho*c.C/c.L
    a = lam*5

    counts = {
        c.EVENT_ARRIVAL: 0,
        c.EVENT_DEPARTURE: 0,
        c.EVENT_OBSERVER: 0
    }
    idle_t = 0

    curr_time = 0
    while curr_time < c.T:
        inter_arrival_time = utils.get_random_variable(1/lam)
        curr_time += inter_arrival_time

        length = utils.get_random_variable(c.L)
        service_time = length / c.C
        events.append(ArrivalEvent(curr_time, service_time))

    curr_time = 0
    while curr_time < c.T:
        curr_time += utils.get_random_variable(1/a)
        events.append(ObserverEvent(curr_time))

    events.sort(key=lambda e: e.event_time, reverse=True)

    event_count = len(events)
    timer = 0
    curr_service_timer = 0
    queue = deque()
    queue_size_sum = 0
    while not (len(events) == 0 and len(queue) == 0) and timer < c.T:
        if len(queue) > 0 and curr_service_timer + queue[0] < events[-1].event_time:
            timer += queue.popleft()
            curr_service_timer = timer
            counts[c.EVENT_DEPARTURE] += 1
        else:
            curr_event = events.pop()
            timer = curr_event.event_time
            if curr_event.event_type == c.EVENT_ARRIVAL:
                queue.append(curr_event.service_time)
                # print(curr_event.event_time, "\t", queue[0], "\t", len(queue))
            else:
                queue_size_sum += len(queue)
                if len(queue) == 0:
                    idle_t += 1
            counts[curr_event.event_type] += 1

    print("\nrho: %.2f" % rho)
    print("lambda: %.0f" % lam)
    print("N_a:", counts[c.EVENT_ARRIVAL])
    print("N_d:", counts[c.EVENT_DEPARTURE])
    print("N_o:", counts[c.EVENT_OBSERVER])
    print("idle_t:", idle_t)
    print("E[N]:", queue_size_sum*1.0/counts[c.EVENT_OBSERVER])
    print("P_IDLE:", idle_t*1.0/counts[c.EVENT_OBSERVER])
