#!/usr/bin/env python3

# DES Simulator for an M/M/1 queue (i.e. infinite buffer)

import math
import statistics
from numpy import arange
from random import random

L = 2000
C = 1000000.0
T = 1000

for rho in arange(0.25,1.0,0.1):

    events = []

    lam = rho*C/L
    a = lam*5

    N_a = 0
    N_d = 0
    N_o = 0
    idle_t = 0

    curr_time = 0
    while curr_time < T:
        interarrival_t = -(1/lam)*math.log(1-random())
        curr_time += interarrival_t
        events.append(('a', curr_time))

        length = -(L)*math.log(1-random())
        service_t = length/C
        departure_t = curr_time + service_t
        events.append(('d', departure_t))

    curr_time = 0
    while curr_time < T:
        curr_time += -(1/a)*math.log(1-random())
        events.append(('o', curr_time))

    events.sort(key=lambda x: x[1], reverse=True)

    event_count = len(events)
    queue = 0
    queue_sizes = []
    while len(events) > 0:
        curr_event = events.pop()
        if curr_event[0] == 'a':
            N_a += 1
            queue += 1
        elif curr_event[0] == 'd':
            N_d += 1
            queue -= 1
        else:
            N_o += 1
            queue_sizes.append(queue)
            if queue == 0:
                idle_t += 1

    print("\nrho: %.2f" % rho)
    print("lambda: %.0f" % lam)
    print("N_a:", N_a)
    print("N_d:", N_d)
    print("N_o:", N_o)
    print("idle_t:", idle_t)
    print("E[N]:", statistics.mean(queue_sizes))
    print("P_IDLE:", idle_t*1.0/N_o)
