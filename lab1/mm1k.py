#!/usr/bin/env python3

# DES Simulator for an M/M/1 queue (i.e. infinite buffer)

from classes.event_queue import EventQueue

file = 'mm1k.csv'
headers = ['K', 'rho', 'E[N]', 'P_LOSS']

print('Format: ' + ', '.join(headers))

data = []
for K in [10, 25, 50]:
    mm1k_des = EventQueue(0.5, 1.5, 0.1, K)
    data += mm1k_des.run_des()

write_to_csv(file, headers, data)
