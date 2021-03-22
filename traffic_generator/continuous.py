import numpy as np
import simpy
from .traffic_gen import TrafficGenerator

class continuous(TrafficGenerator):

    def __init__(self, env, id, arrival_rate, arrival_dist):
        super().__init__(env, id, arrival_rate, arrival_dist=arrival_dist)


class constant(continuous):

    def __init__(self, env, id, arrival_rate):
        super().__init__(env, id, arrival_rate, arrival_dist="constant")


class exponential(continuous):

    def __init__(self, env, id, arrival_rate):
        super().__init__(env, id, arrival_rate, arrival_dist="exponential")


    def get_interval(self):
        interval = np.random.exponential(self.lambda_in)
        return interval
