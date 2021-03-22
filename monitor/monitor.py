import simpy
import numpy as np
from collections import namedtuple
import pandas as pd
import pickle

class Monitor(object):
    """ Monitor for the channel status and arrivals"""

    def __init__(self, env, dir):
        self.env = env
        self.dir = dir
        self.queue_monitor = []
        self.decision_monitor = []
        self.service_monitor = []
        self.loss_monitor = []
        self.waste_monitor = []
        # self.monitor = self.end.process(self.monitor_process())

    def write_to_monitor(self, value, value_type):
        if value_type == 'queue':
            self.queue_monitor.append(value)
            # print(self.queue_monitor)
        if value_type == 'decision':
            self.decision_monitor.append(value)
        if value_type == 'service':
            self.service_monitor.append(value)
        if value_type == 'loss':
            self.loss_monitor.append(value)
        if value_type == 'waste':
            self.waste_monitor.append(value)

    def dump_to_file(self):
        pd.DataFrame(np.array(self.queue_monitor), columns=["time", "queue_length"]).to_pickle(self.dir + "/queue.pkl")
        pd.DataFrame(np.array(self.decision_monitor), columns=["time", "decision", "id"]).to_pickle(self.dir + "/decision.pkl")
        pd.DataFrame(np.array(self.service_monitor), columns=["time", "service"]).to_pickle(self.dir + "/service.pkl")
        pd.DataFrame(np.array(self.loss_monitor), columns=["time", "loss"]).to_pickle(self.dir + "/loss.pkl")
        pd.DataFrame(np.array(self.waste_monitor), columns=["time", "waste"]).to_pickle(self.dir + "/waste.pkl")

    def get_loss(self):
        return self.loss_monitor.copy()

    def get_waste(self):
        return self.waste_monitor.copy()
