import numpy as np
import simpy
from .traffic_gen import TrafficGenerator

class on_off(TrafficGenerator):

    def __init__(self, env, id, arrival_rate, arrival_dist, args_on, args_off):
        super().__init__(env, id, arrival_rate, arrival_dist=arrival_dist)
        self.dist_on =  args_on[0]
        self.dist_off = args_off[0]
        self.d_on = args_on[1]
        self.d_off =  args_off[1]
        self.alpha_on = 1.5
        self.alpha_off = 1.5
        self.distribution_mapping = {
            'constant': self.__get_constant_duration,
            'pareto': self.__get_pareto_duration
        }


    def get_t_on(self):
        t_on = self.distribution_mapping[self.dist_on](self.d_on, self.alpha_on)
        return t_on

    def get_t_off(self):
        t_off = self.distribution_mapping[self.dist_off](self.d_off, self.alpha_off)
        return t_off

    def __get_constant_duration(self, d, alpha):
        # make sure that the load gerated are the same
        d_align = d * alpha / (alpha - 1)
        t = d_align + np.random.normal(0, alpha)
        return t

    def __get_pareto_duration(self, d, alpha):
        t =  (np.random.pareto(alpha, 1) + 1) * d
        return t[0]

    def get_period(self):
        return self.get_t_on(), self.get_t_off()

class constant(on_off):

    def __init__(self, env, id, arrival_rate, args_on, args_off):
        super().__init__(env, id, arrival_rate, "constant", args_on, args_off)


class exponential(on_off):

    def __init__(self, env, id, arrival_rate,  args_on, args_off):
        super().__init__(env, id, arrival_rate, "exponential", args_on, args_off)

    def get_interval(self):
        interval = np.random.exponential(self.lambda_in)
        return interval
