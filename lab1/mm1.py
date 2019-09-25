#!/usr/bin/env python3

# DES Simulator for an M/M/1 queue (i.e. infinite buffer)

from classes.event_queue import EventQueue


mm1_des = EventQueue(0.25, 0.95, 0.1)
mm1_des.run_des()
