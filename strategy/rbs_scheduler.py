import simpy
import numpy as np
import random
from strategy.data_struct import Report, Decision, PacketHeader, Packet

class FCFS(object):

    def __init__(self, env, monitor):
        self.env = env
        self.monitor = monitor

    def create_report(self, report_counter, channel):
        queue_len = channel.get_queue_len()
        report = Report(report_counter, self.env.now, queue_len)
        return report

    def make_decision(self, queue_len, decision_counter):
        if queue_len <=12:
            decision = queue_len
        else:
            decision = 12
        return Decision(decision_counter, decision)

    def init_decision(self):
        decision_id = 0
        decision_packets = 12
        decision = Decision(decision_id, decision_packets)
        return decision

    def update_init_decision(self):
        return self.init_decision()
     # TODO: start from herr
    def assign_pilots(self, decision, channel):
        self.monitor.write_to_monitor((self.env.now, decision.decision, decision.id), 'decision')
        # print("[{}] Take decision No.{}, assign {} packets".format(self.env.now, decision.id, decision.decision))
        queue = [p.header for p in channel.get_queue()]
        self.monitor.write_to_monitor((self.env.now, channel.get_queue_len()), 'queue')
        # print("current queue {}".format(len(queue)))
        waste_count = 0
        served_count = 0
        if len(queue) <= decision.decision:
            channel.serve(queue)
            waste_count = decision.decision - len(queue)
            served_count = len(queue)
        if len(queue) > decision.decision:
            channel.serve(queue[0:decision.decision])
            served_count = decision.decision
        if decision.id >0:
            input("take decision No.{}, current queue {}, decision {}, served {}, waste {}".format(
                decision.id, len(queue), decision.decision, served_count, waste_count))
        self.monitor.write_to_monitor((self.env.now, waste_count), 'waste')
        self.monitor.write_to_monitor((self.env.now, served_count), 'service')

class EDF(object):

    def __init__(self, env, monitor):
        self.env = env
        self.monitor = monitor

    def create_report(self, report_counter, channel):
        queue_len = channel.get_queue_len()
        report = Report(report_counter, self.env.now, queue_len)
        return report

    def make_decision(self, queue_len, decision_counter):
        if queue_len <=12:
            decision = queue_len
        else:
            decision = 12
        print("Make decision No.{} for {} pilots".format(decision_counter, decision))
        return Decision(decision_counter, decision)

    def init_decision(self):
        decision_id = 0
        decision_packets = 12
        decision = Decision(decision_id, decision_packets)
        return decision

    def update_init_decision(self):
        return self.init_decision()

     # TODO: start from herr
    def assign_pilots(self, decision, channel):
        self.monitor.write_to_monitor((self.env.now, decision.decision, decision.id), 'decision')
        # print("[{}] Take decision No.{}, assign {} packets".format(self.env.now, decision.id, decision.decision))
        queue = channel.get_queue()
        queue.sort(key=lambda x: x.deadline)
        queue_to_consider = [p.header for p in queue]
        self.monitor.write_to_monitor((self.env.now, channel.get_queue_len()), 'queue')
        # print("current queue {}".format(len(queue_to_consider)))
        waste_count = 0
        served_count = 0
        if len(queue_to_consider) <= decision.decision:
            channel.serve(queue_to_consider)
            waste_count = decision.decision - len(queue_to_consider)
            served_count = len(queue_to_consider)
        if len(queue_to_consider) > decision.decision:
            channel.serve(queue_to_consider[0:decision.decision])
            served_count = decision.decision
        if decision.id >0:
            input("take decision No.{}, current queue {}, decision {}, served {}, waste {}".format(
                decision.id, len(queue), decision.decision, served_count, waste_count))
        self.monitor.write_to_monitor((self.env.now, waste_count), 'waste')
        self.monitor.write_to_monitor((self.env.now, served_count), 'service')
