import simpy
from collections import namedtuple
from user.ue import Packet
from strategy.data_struct import Report, Decision, PacketHeader

class RBS(object):

    def __init__(self, env, channel, cable, scheduler, mu, beta):
        self.env = env
        self.channel = channel
        self.uplink = cable[0]
        self.downlink = cable[1]
        self.scheduler = scheduler
        self.delay = mu
        self.interval = 0.5 * beta

        self.init_decision = self.scheduler.init_decision()
        self.get_decision = self.env.event()

        self.decision = None
        self.reporter = self.env.process(self.reporter_process())
        self.listener = self.env.process(self.listener_process())
        self.action = self.env.process(self.scheduler_process())

    def listener_process(self):
        while True:
            self.decision = yield self.downlink.get()
            self.get_decision.succeed()
            # print("[RBS][{}] get decision: No.{}".format(self.env.now, self.decision.id))
            self.get_decision = self.env.event()

    def submit_report(self, report):
        # print("[RBS][{}] Submit report No.{}".format(self.env.now, report.id))
        self.uplink.put(report)

    def reporter_process(self):
        report_counter = 0
        while True:
            yield self.env.timeout(self.interval)
            self.channel.handle_expir(self.env.now)

            report_counter += 1
            self.submit_report(self.scheduler.create_report(report_counter, self.channel))

    def scheduler_process(self):
        while True:
            yield self.env.timeout(self.interval)
            if self.delay == 0:
                # print("need a decision!")
                yield self.get_decision
            else:
                pass
            # yield self.get_decision.succeed()
            # print(event for event in self.env._queue if event[0]==self.env.now)
            if self.decision is None:
                decision = self.init_decision
                self.init_decision = self.scheduler.update_init_decision()
            else:
                decision = self.decision
            self.scheduler.assign_pilots(decision, self.channel)
