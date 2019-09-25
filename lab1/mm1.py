#!/usr/bin/env python3

# DES Simulator for an M/M/1 queue (i.e. infinite buffer)

from classes.event_queue import EventQueue
from utils.utils import write_to_csv

file = 'mm1.csv'
headers = ['rho', 'E[N]', 'P_IDLE']

print('Format: ' + ', '.join(headers))

mm1_des = EventQueue(0.25, 0.95, 0.1)
data = mm1_des.run_des()

write_to_csv(file, headers, data)
