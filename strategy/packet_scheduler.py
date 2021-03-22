import simpy
import numpy as np
from strategy.data_struct import Report, Decision, PacketHeader, Packet

class FCFS(object):

    def __init__(self, env, monitor):
        self.env = env
        self.monitor = monitor
        self.init_counter = 1

    def create_report(self, report_counter, channel):
        queue = channel.get_queue()
        report = Report(report_counter, self.env.now, queue)
        return report

    def make_decision(self, queue, decision_counter):
        if len(queue)<=12:
            packets = [p.header for p in queue]
        else:
            packets = [p.header for p in queue[0:12]]
        decision = Decision(decision_counter, packets)
        return decision

    def init_decision(self):
        decision_id = 0
        decision = Decision(0, [PacketHeader(i, self.init_counter) for i in range(12)])
        return decision

    def update_init_decision(self):
        decision_id = 0
        self.init_counter += 1
        decision = Decision(0, [PacketHeader(i, self.init_counter) for i in range(12)])
        return decision

    def assign_pilots(self, decision, channel):
        self.monitor.write_to_monitor((self.env.now, len(decision.decision), decision.id), 'decision')
        # print("[{}] Take decision No.{}, assign {} packets".format(self.env.now, decision.id, len(decision.decision)))
        queue = np.array([p.header for p in channel.get_queue()])
        self.monitor.write_to_monitor((self.env.now, channel.get_queue_len()), 'queue')
        # print("current queue {}".format(len(queue)))
        selected_packets = np.array(decision.decision)
        # print("select {}".format(selected_packets))
        mask = np.isin(selected_packets, queue)
        active_packets = selected_packets[mask]
        # print("Active {}".format(len(active_packets)))
        expired_packets = [p for p in selected_packets if not p in active_packets]
        # print("Expired {}".format(len(expired_packets)))
        self.monitor.write_to_monitor((self.env.now, len(expired_packets)), 'waste')
        # for packet in active_packets:
            # # print(packet)
        channel.serve(active_packets)
        self.monitor.write_to_monitor((self.env.now, len(active_packets)), 'service')
        # if len(expired_packets) > 0:
        #     input()


class EDF(object):

    def __init__(self, env, monitor):
        self.env = env
        self.monitor = monitor
        self.init_counter = 1

    def create_report(self, report_counter, channel):
        queue = channel.get_queue()
        report = Report(report_counter, self.env.now, queue)
        return report

    def make_decision(self, queue, decision_counter):
        queue.sort(key=lambda x: x.deadline)
        if len(queue)<=12:
            packets = [p.header for p in queue]
        else:
            packets = [p.header for p in queue[0:12]]
        decision = Decision(decision_counter, packets)
        return decision

    def init_decision(self):
        decision_id = 0
        decision = Decision(0, [PacketHeader(i, self.init_counter) for i in range(12)])
        return decision

    def update_init_decision(self):
        decision_id = 0
        self.init_counter += 1
        decision = Decision(0, [PacketHeader(i, self.init_counter) for i in range(12)])
        return decision

    def assign_pilots(self, decision, channel):
        self.monitor.write_to_monitor((self.env.now, len(decision.decision), decision.id), 'decision')
        # # print("decision {}".format(decision))
        queue = np.array([p.header for p in channel.get_queue()])
        self.monitor.write_to_monitor((self.env.now, channel.get_queue_len()), 'queue')
        # # print("queue {}".format(queue))
        selected_packets = np.array(decision.decision)
        # # print("select {}".format(selected_packets))
        mask = np.isin(selected_packets, queue)
        active_packets = selected_packets[mask]
        # # print("active {}".format(active_packets))
        expired_packets = [p for p in selected_packets if not p in active_packets]
        # # print("expired {}".format(expired_packets))
        self.monitor.write_to_monitor((self.env.now, len(expired_packets)), 'waste')
        # for packet in active_packets:
            # print(packet)
        channel.serve(active_packets)
        self.monitor.write_to_monitor((self.env.now, len(active_packets)), 'service')
