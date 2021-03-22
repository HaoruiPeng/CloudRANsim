import simpy
from rbs.rbs import Report
from rbs.rbs import Decision
from strategy.data_struct import Report, Decision

class Cloud(object):

    def __init__(self, env, cable, scheduler):
        self.env = env
        self.uplink = cable[0]
        self.downlink = cable[1]
        self.scheduler = scheduler
        self.report_listener = self.env.process(self.listener_process())

    def listener_process(self):
        while True:
            report = yield self.uplink.get()
            # print("[Cloud] [{}] Get report {}".format(self.env.now, report.id))
            decision = self.scheduler.make_decision(report.report, report.id)
            self.downlink.put(decision)
