import time

from classes.arrival_event import ArrivalEvent
from classes.lan_node import LanNode
from utils import constants as c, utils

class LAN_DES:
    def __init__(self, N, A, T, non_persistent = False):
        self.N = N
        self.A = A
        self.T = T
        self.non_persistent = non_persistent

        self.lan = []
        self.timer = 0
        self.t_prop = c.D / c.S # move these constants
        self.t_trans = c.L / c.R
        self.dropped_packets = 0

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
        sender_index = -1
        next_packet_time = self.T

        for i in range(self.N):
            if self.lan[i].events[0].event_time < next_packet_time:
                next_packet_time = self.lan[i].events[0].event_time
                sender_index = i

        return sender_index

    def update_node_event_times(self, node, new_time, collision_logic=False):
        if not collision_logic and self.non_persistent:
            node.busy_count += 1
            backoff_time = utils.get_exponential_backoff(node.busy_count)

            if node.collisions > c.K_max:
                # print('Packet dropped!')
                node.busy_count = 0
                node.events.popleft()
                self.dropped_packets += 1
        else:
            backoff_time = 0

        for event in node.events:
            if event.event_time > new_time + backoff_time:
                break
            event.event_time = new_time + backoff_time

    def handle_collision(self, node):
        node.collisions += 1
        node.busy_count = 0

        backoff_time = utils.get_exponential_backoff(node.collisions)

        waiting_start = node.events[0].event_time
        self.update_node_event_times(node, waiting_start + backoff_time + c.jamming_time, collision_logic=True)

        if node.collisions > c.K_max:
            # print('Packet dropped!')
            node.collisions = 0
            node.events.popleft()
            self.dropped_packets += 1

    # helper function for printing first packet
    def first_packet(self, sender, overlaps):
        first_packet = []
        for i in range(self.N):
            t_first_bit = self.timer + abs(i - sender) * self.t_prop

            if self.lan[i].events[0].event_time < t_first_bit:
                overlaps += 1

            first_packet.append(self.lan[i].events[0].event_time)
        return overlaps, first_packet

    def run_des(self):
        self.populate_lan()
        num_packets = 0
        for n in self.lan:
            num_packets += len(n.events)
        print(num_packets)

        total_overlaps = 0
        collision_occurred = False
        total_packets = 0
        successfully_transmitted = 0
        total_collisions = 0
        dropped_packets = 0
        while self.timer < self.T:
            sender = self.next_sender()
            # print('Next sender: node', sender)
            self.timer = self.lan[sender].events[0].event_time
            self.lan[sender].busy_count = 0

            curr_collisions = 0
            # total_overlaps, first_packet = self.first_packet(sender, total_overlaps)
            # print(total_overlaps, first_packet)

            for i in range(self.N):
                if i == sender:
                    continue
                t_first_bit = self.timer + abs(i - sender) * self.t_prop
                t_last_bit = t_first_bit + self.t_trans

                # If line is busy, node will wait to transmit
                if t_first_bit < self.lan[i].events[0].event_time < t_last_bit:
                    # print(t_first_bit, t_last_bit)
                    # print(i, self.lan[i].events[0].event_time)
                    self.update_node_event_times(self.lan[i], t_last_bit)

                # Cannot detect line is busy, collision occurs
                elif self.lan[i].events[0].event_time < t_first_bit:
                    collision_occurred = True
                    curr_collisions += 1
                    self.handle_collision(self.lan[i])

                    total_packets += 1

            if collision_occurred:
                # print(curr_collisions)
                collision_occurred = False
                curr_collisions += 1
                self.handle_collision(self.lan[sender])
                    
            else:
                self.lan[sender].collisions = 0
                self.lan[sender].events.popleft()
                successfully_transmitted += 1

            total_packets += 1
            total_collisions += curr_collisions
            # print(self.timer)

        print('N =', self.N)
        print('Successfully transmitted:', successfully_transmitted)
        print('Total packets:', total_packets)
        print('Efficiency:', successfully_transmitted * 1.0 / total_packets)
        print('Throughput:', total_packets * c.L / self.T)
        print('Total collisions:', total_collisions)
        print('Dropped packets:', self.dropped_packets)

                

