import numpy as np
import simpy

class TrafficGenerator(object):
    """Parent class for all traffic generators"""

    def __init__(self, env, id, arrival_rate, arrival_dist=None):
        self.env = env
        self.id = id
        self.arrival_dist = arrival_dist
        self.lambda_in =  arrival_rate
        self.noise_par = 0.001
        self.t_start = 200

    def get_t_start(self):
        start_std = 100
        s = abs(np.random.normal(self.t_start,  start_std))
        return s

    def get_interval(self):
        interval = abs(self.lambda_in + np.random.normal(0,  np.sqrt(self.noise_par)))
        return interval

    def get_period(self):
        return 100, 0
