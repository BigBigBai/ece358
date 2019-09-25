#!/usr/bin/env python3

# DES Simulator for an M/M/1 queue (i.e. infinite buffer)

from classes.event_queue import EventQueue

print("Format: K, rho, E[N], P_IDLE, P_LOSS")
for K in [10, 25, 50]:
    mm1k_des_1 = EventQueue(0.5, 2, 0.1, K)
    mm1k_des_1.run_des()

    mm1k_des_2 = EventQueue(2.2, 5, 0.2, K)
    mm1k_des_2.run_des()

    mm1k_des_3 = EventQueue(5.4, 9.8, 0.4, K)
    mm1k_des_3.run_des()
