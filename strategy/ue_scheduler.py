import simpy
import numpy as np
import random
import math
from strategy.data_struct import Report, Decision, PacketHeader, Packet

class scheduler(object):
    def __init__(self, env, beta, monitor=None):
        self.env = env
        self.monitor = monitor
        self.ue_max_index = 11
        self.nbr_pilots = 12 * beta
        self.beta = beta
        self.decision_list = []
        self.ue_register = list(range(0, self.ue_max_index+1))

    def create_report(self, report_counter, channel):
        queue = channel.get_queue()
        report = Report(report_counter, self.env.now, queue)
        return report

    def update_ue_register(self, max):
        new_index = list(range(self.ue_max_index + 1, max + 1))
        self.ue_max_index = max
        self.ue_register = self.ue_register + new_index

    def init_decision(self):
        decision_id = 0
        decision_list = self.ue_register
        decision = Decision(decision_id, decision_list)
        return decision

    def update_init_decision(self):
        return self.init_decision()

    def create_active_ue_list(self, queue):
        active_ue = []
        for p in queue:
            node_id = p.header.node_id
            if node_id not in active_ue:
                active_ue.append(node_id)
        return active_ue

    def make_decision(self, queue, decision_counter):
        # self.decision_dict = dict.fromkeys(range(self.ue_max_index + 1),0)
        self.decision_list = self.create_active_ue_list(queue)
        # for k in self.decision_dict.keys():
        #     if self.decision_dict[k] > 0:
                # print("Node: {}, Pilots {}".format(k, self.decision_dict[k]))
        # input("Decision Made")
        decision = Decision(decision_counter, self.decision_list)
        return decision

    def assign_pilots(self, decision, channel):
        # print("[{}] Assigne pilots to UEs {}".format(self.env.now, decision.decision))
        # print("Serve {} packets each".format(self.beta))
        queue = channel.get_queue()
        queue_length = len(queue)
        waste_count = 0
        served_count = 0
        for node in decision.decision:
            nbr_packets_to_assign = self.beta
            packets_in_queue = self.get_packets_from_ue(queue, node)
            # print("[{}] get current queue for node {}: {}".format(self.env.now, node, [p.packet_counter for p in packets_in_queue]))
            if len(packets_in_queue) >= nbr_packets_to_assign:
                channel.serve(packets_in_queue[0:nbr_packets_to_assign])
                served_count += nbr_packets_to_assign
                # print("[RBS][{}] Assign Node {} pilot, {} requests waiting, {} requests served, no waste".format(self.env.now, node, len(packets_in_queue), nbr_packets_to_assign))
            else:
                channel.serve(packets_in_queue)
                served_count += len(packets_in_queue)
                # print("[RBS][{}] Assign Node {} pilot, want to serve {} requests, only {} requests waiting.".format(
                #                             self.env.now, node,
                #                             nbr_packets_to_assign, len(packets_in_queue)))
            waste = max((nbr_packets_to_assign - len(packets_in_queue))/nbr_packets_to_assign, 0)
            # input("[RBS][{}] On Node {}, waste {} pilots".format(self.env.now, node, waste))
            waste_count += waste
        # print(waste_count)
        if self.env.now > 998:
            print(self.env.now)
            print(queue_length)
        self.monitor_record(decision, waste_count, served_count, queue_length)
        return waste_count, served_count

    def monitor_record(self, decision=None, waste=None, served=None, queue_length=None):
        if self.monitor is not None:
            if decision is not None:
                self.monitor.write_to_monitor((self.env.now, len(decision.decision) * self.beta, decision.id), 'decision')
                # print("[RBS][{}] Take decision No.{}, assign {} packets".format(self.env.now, decision.id, sum(decision.decision.values())))
            if waste is not None:
                self.monitor.write_to_monitor((self.env.now, waste), 'waste')
            if served is not None:
                self.monitor.write_to_monitor((self.env.now, served), 'service')
            if queue_length is not None:
                self.monitor.write_to_monitor((self.env.now, queue_length), 'queue')
                # print("[RBS][{}] Current queue {}".format(self.env.now, len(queue)))

    def get_header_list(self, queue):
        header_list = [p.header for p in queue]
        return header_list, len(header_list)

    def get_packets_from_ue(self, queue, node_id):
        assert type(queue) == list
        if len(queue) > 0:
            assert type(queue[0]) == Packet
        packets_from_ue = [packet.header for packet in queue if packet.header.node_id == node_id]
        return packets_from_ue

    def queue_saturate(self, queue):
        ue_list = []
        for p in queue:
            if p.header.node_id not in ue_list:
                ue_list.append(p.header.node_id)
            if len(ue_list) >= self.nbr_pilots:
                break
        queue_sat = [p for p in queue if p.header.node_id in ue_list]
        return queue_sat

class proportionaldivision(scheduler):

    def __init__(self, env, beta, monitor=None):
        super().__init__(env, beta, monitor)

    def make_decision(self, queue, decision_counter):
        queue_to_consider = self.queue_saturate(queue)
        self.decision_list = self.create_active_ue_list(queue_to_consider)
        # for k in self.decision_dict.keys():
        #     if self.decision_dict[k] > 0:
                # print("Node: {}, Pilots {}".format(k, self.decision_dict[k]))
        # input("Decision Made")
        decision = Decision(decision_counter, self.decision_list)
        return decision

    def queue_saturate(self, queue):
        ue_list = self.create_active_ue_list(queue)
        if len(ue_list) <= self.nbr_pilots:
            queue_sat = queue
        else:
            packets_dict = dict.fromkeys(ue_list)
            for p in queue:
                packets_dict[p.header.node_id] += 1
            ue_sorted = sorted(packets_dict, key=packets_dict.get, reverse=True)[0:self.nbr_pilots]
            queue_sat = [p for p in queue if p.header.node_id in ue_sorted]
        return queue_sat

class fcfs(scheduler):

    def __init__(self, env, beta, monitor=None):
        super().__init__(env, beta, monitor)

    def make_decision(self, queue, decision_counter):
        queue.sort(key=lambda x: x.arrival)
        queue_to_consider = self.queue_saturate(queue)
        self.decision_list = self.create_active_ue_list(queue_to_consider)
        # for k in self.decision_dict.keys():
        #     if self.decision_dict[k] > 0:
                # print("Node: {}, Pilots {}".format(k, self.decision_dict[k]))
        # input("Decision Made")
        decision = Decision(decision_counter, self.decision_list)
        return decision

    def get_packets_from_ue(self, queue, node_id):
        assert type(queue) == list
        if len(queue) > 0:
            assert type(queue[0]) == PacketHeader
        packets_from_ue = [packet for packet in queue if packet.node_id == node_id]
        packets_from_ue.sort(key=lambda x: x.arrival)
        return packets_from_ue

class edf(scheduler):

    def __init__(self, env, beta, monitor=None):
        super().__init__(env, beta, monitor)

    def make_decision(self, queue, decision_counter):
        queue.sort(key=lambda x: x.deadline)
        queue_to_consider = self.queue_saturate(queue)
        self.decision_list = self.create_active_ue_list(queue_to_consider)
        # for k in self.decision_dict.keys():
        #     if self.decision_dict[k] > 0:
                # print("Node: {}, Pilots {}".format(k, self.decision_dict[k]))
        # input("Decision Made")
        decision = Decision(decision_counter, self.decision_list)
        return decision

    def get_packets_from_ue(self, queue, node_id):
        assert type(queue) == list
        if len(queue) > 0:
            assert type(queue[0]) == Packet
        packets_from_ue = [packet for packet in queue if packet.header.node_id == node_id]
        packets_from_ue.sort(key=lambda x: x.deadline)
        packets_headers = [p.header for p in packets_from_ue]
        return packets_headers
