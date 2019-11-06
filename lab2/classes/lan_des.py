from classes.arrival_event import ArrivalEvent
from classes.lan_node import LanNode
from utils import constants as c, utils


class LAN_DES:
    def __init__(self, N, A, T, non_persistent=False):
        self.N = N
        self.A = A
        self.T = T
        self.non_persistent = non_persistent

        self.lan = []
        self.timer = 0
        self.dropped_packets = 0
        self.total_packets = 0

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

            if node.busy_count > c.K_max:
                node.busy_count = 0
                node.events.popleft()
                self.dropped_packets += 1
                self.total_packets += 1
                return
        else:
            backoff_time = 0

        events_updated = 0
        for event in node.events:
            if event.event_time > new_time + backoff_time:
                # if events_updated > 9:
                #     print(events_updated, new_time + backoff_time)
                break
            event.event_time = new_time + backoff_time
            events_updated += 1

    def handle_collision(self, node, waiting_start):
        node.collisions += 1
        node.busy_count = 0

        if node.collisions > c.K_max:
            node.collisions = 0
            node.events.popleft()
            self.dropped_packets += 1
            return

        backoff_time = utils.get_exponential_backoff(node.collisions)

        self.update_node_event_times(node, waiting_start + backoff_time, collision_logic=True)

    def run_des(self):
        self.populate_lan()

        collision_occurred = False
        successfully_transmitted = 0
        total_collisions = 0
        last_successful = 0
        last_successful_node = -1

        while self.timer < self.T:
            sender = self.next_sender()
            if sender < 0:
                break
            # if self.lan[sender].events[0].event_time - self.timer < c.t_trans:
            #     print(self.lan[sender].events[0].event_time - self.timer)
            self.timer = self.lan[sender].events[0].event_time
            # print(self.timer)
            self.lan[sender].busy_count = 0

            curr_collisions = 0

            for i in range(self.N):
                if i == sender or len(self.lan[i].events) == 0:
                    continue
                t_first_bit = self.timer + abs(i - sender) * c.t_prop
                t_last_bit = t_first_bit + c.t_trans

                # Cannot detect line is busy, collision occurs
                if self.lan[i].events[0].event_time <= t_first_bit:
                    collision_occurred = True
                    curr_collisions += 1
                    self.handle_collision(self.lan[i], t_last_bit)

                    self.total_packets += 1

            if collision_occurred:
                collision_occurred = False
                curr_collisions += 1
                self.handle_collision(self.lan[sender], self.timer + c.t_trans)
                    
            else:
                for i in range(self.N):
                    t_first_bit = self.timer + abs(i - sender) * c.t_prop
                    t_last_bit = t_first_bit + c.t_trans

                    # if i == sender:
                    #     print('uh-oh')

                    # If line is busy, node will wait to transmit
                    if t_first_bit <= self.lan[i].events[0].event_time < t_last_bit:
                        self.update_node_event_times(self.lan[i], t_last_bit)

                # if self.timer - last_successful < c.t_trans:
                #     print(self.timer - last_successful)
                self.lan[sender].collisions = 0
                self.lan[sender].events.popleft()
                successfully_transmitted += 1
                last_successful = self.timer
                last_successful_node = sender

            self.total_packets += 1
            total_collisions += curr_collisions

        leftovers = 0
        for n in self.lan:
            leftovers += len(n.events)
        print(leftovers)

        print('N =', self.N)
        print('Successfully transmitted:', successfully_transmitted)
        print('Total packets:', self.total_packets)
        print('Efficiency:', successfully_transmitted * 1.0 / self.total_packets)
        print('Throughput:', successfully_transmitted * c.L / self.T)
        print('Total collisions:', total_collisions)
        print('Dropped packets:', self.dropped_packets)
