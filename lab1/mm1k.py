#!/usr/bin/env python3

# DES Simulator for an M/M/1 queue (i.e. infinite buffer)

from classes.event_queue import EventQueue

for K in [10, 25, 50]:
    mm1k_des = EventQueue(0.25, 0.95, K)
    mm1k_des.run_des()
