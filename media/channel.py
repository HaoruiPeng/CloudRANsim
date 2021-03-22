import simpy
import numpy as np
import sys
from collections import namedtuple
from strategy.data_struct import PacketHeader, Packet
from user.ue import Packet

class Channel(object):
    """This class represents the queue in the air."""
    def __init__(self, env, monitor=None):
        self.env = env
        self.queue = []
        self.arrivals = []
        self.monitor = monitor

    def submit(self, packet):
        self.queue.append(packet)
        self.arrivals.append(packet.arrival)

    def handle_expir(self, time):
        removes = 0
        queue = self.queue.copy()
        for p in queue:
            if p.deadline < time:
                self.queue.remove(p)
                removes += 1
                # print("[{}] Packet expired, node:{}, counter:{}, arriavl: {}, deadline: {}.".format(time, p.header.node_id, p.header.packet_counter, p.arrival, p.deadline))
        if self.monitor is not None:
            self.monitor.write_to_monitor((self.env.now, removes), 'loss')

    def get_queue_len(self):
        return len(self.queue)

    def get_arrivals(self):
        # print("get arrival")
        return self.arrivals.copy()

    def get_queue(self):
        return self.queue.copy()

    def serve(self, packet_headers):
        # for p in packet_headers:
            # print(p.node_id, p.packet_counter)
        removed_packet = [p for p in self.queue if p.header in packet_headers]
        # print("remove: {}".format([p.header.packet_counter for p in removed_packet]))
        for p in removed_packet:
            # print("before removal queue {}".format([p.header.packet_counter for p in self.queue]))
            # print(p.header.node_id, p.header.packet_counter)
            self.queue.remove(p)
            # print("[{}] updated queue {}".format(self.env.now, [p.header.packet_counter for p in self.queue]))
        try:
            assert len(removed_packet) == len(packet_headers)
        except AssertionError as e:
            print("wrong scheduler")
            sys.exit(1)
        # for p in removed_packet:
