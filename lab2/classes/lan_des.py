from classes.arrival_event import ArrivalEvent
from classes.lan_node import LanNode
from utils import constants as c, utils

class LAN_DES:
    def __init__(self, N, A, T):
        self.N = N
        self.A = A
        self.T = T

        self.lan = []
        self.timer = 0
        self.t_prop = c.D / c.S
        self.t_trans = c.R / c.L

    def populate_lan(self):
        for i in range(self.N):
            curr_time = 0
            curr_node_events = []

            while curr_time < self.T:
                inter_arrival_time = utils.get_random_variable(1.0 / self.A)
                curr_time += inter_arrival_time

                curr_node_events.append(ArrivalEvent(curr_time))

            self.lan.append(LanNode(curr_node_events))

    def next_sender(self):
        next_node_index = -1
        next_packet_time = self.T

        for i in range(self.N):
            if self.lan[i].events[0].event_time < next_packet_time:
                next_packet_time = self.lan[i].events[0].event_time
                next_node_index = i

        return next_node_index

    def run_des(self):
        self.populate_lan()

        collision_occurred = False
        while self.timer < self.T:
            next_node = self.next_sender()
            self.timer = self.lan[next_node].events[0].event_time

            for i in range(self.N):
                if i == next_node:
                    continue
                t_first_bit = self.timer + abs(i - next_node) * self.t_prop
                t_last_bit = t_first_bit + self.t_trans

                if t_first_bit < self.lan[i].events[0].event_time < t_last_bit:
                    for event in self.lan[i].events:
                        if event.event_time > t_last_bit:
                            break
                        event.event_time = t_last_bit

                elif self.lan[i].events[0].event_time < t_first_bit:
                    collision_occurred = True
                    self.lan[i].collisions += 1

                    i_backoff = utils.get_exponential_backoff()

                    for event in self.lan[i].events:
                        if event.event_time > t_last_bit + i_backoff:
                            break
                        event.event_time = t_last_bit + i_backoff

            if collision_occurred:
                self.lan[next_node].collisions += 1
                curr_backoff = utils.get_exponential_backoff()

                for event in self.lan[i].events:
                    if event.event_time > t_last_bit + curr_backoff:
                        break
                    event.event_time = t_last_bit + curr_backoff
                

