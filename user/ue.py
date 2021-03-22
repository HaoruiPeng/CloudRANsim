import simpy
import numpy as np
from strategy.data_struct import PacketHeader, Packet

class UE(object):

    def __init__(self, env, id, channel, init_sleep, deadline, traffic_generator):
        self.id = id
        self.counter = 0

        self.env = env
        # self.rbs = rbs
        self.channel = channel

        self.init_sleep = init_sleep
        self.deadline = deadline
        self.traffic_generator = traffic_generator

        # self.d_on = d_on
        # self.d_off = d_off
        # self.lambda_in = lambda_in
        # self.action_mapping = {
        #     'continuous': self.__continuous_action,
        #     'on_off': self.__on_off_action}
        self.action = env.process(self.run())
    #
    # def get_t_on(self):
    #     alpha = 1.5
    #     d, distribution = self.d_on
    #     if distribution == "pareto":
    #         s = (np.random.pareto(alpha, 1) + 1) * d
    #         t_on = s[0]
    #     if distribution == "constant":
    #         t_on = d + np.random.normal(0, alpha)
    #     return t_on
    #
    # def get_t_off(self):
    #     alpha = 1.5
    #     d, distribution = self.d_off
    #     if distribution == "pareto":
    #         s = (np.random.pareto(alpha, 1) + 1) * d
    #         t_off = s[0]
    #     if distribution == "constant":
    #         t_off = d + np.random.normal(0, alpha)
    #     return t_off
    #
    # def get_t_start(self):
    #     alpha = 1.1
    #     # d = self.d_off[0]
    #     d = 200
    #     # s = abs(np.random.normal(d,  np.sqrt(alpha)))
    #     s = (np.random.pareto(alpha, 1) + 1) * d
    #     return s[0]
    #
    # def get_interval(self):
    #     lam, distribution = self.lambda_in
    #     var = 0.02
    #     if distribution == "exponential":
    #         interval = np.random.exponential(lam)
    #     if distribution == "constant":
    #         interval = lam + np.random.normal(0,  np.sqrt(var))
    #     return interval

    def submit_packet(self, packet):
        self.channel.submit(packet)
        # self.channel = np.append(self.channel, packet)
        # print("submit {}, total {}".format(packet, self.channel.get_queue_len()))

    def continuous_action(self):
        arrival = self.env.now
        self.counter += 1
        self.submit_packet(Packet(self.id, self.counter, arrival, arrival + self.deadline))
        yield self.env.timeout(self.traffic_generator.get_interval())

    def on_off_action(self, t_on, t_off):
        t_start = self.env.now
        while self.env.now < t_start + t_on:
            arrival = self.env.now
            self.counter += 1
            self.submit_packet(Packet(self.id, self.counter, arrival, arrival + self.deadline))
            yield self.env.timeout(self.traffic_generator.get_interval())
        yield self.env.timeout(t_off)


    def run(self):
        # print("start")
        yield self.env.timeout(self.init_sleep + self.traffic_generator.get_t_start())
        while True:
            t_on, t_off = self.traffic_generator.get_period()
            # print(t_on, t_off)
            if t_off != 0:
                t_start = self.env.now
                # print(t_start)
                while self.env.now < t_start + t_on:
                    arrival = self.env.now
                    self.counter += 1
                    # print("[{}] new arrival: {}".format(self.env.now, (self.id, self.counter, arrival, arrival + self.deadline)))
                    self.submit_packet(Packet(self.id, self.counter, arrival, arrival + self.deadline))
                    yield self.env.timeout(self.traffic_generator.get_interval())
                yield self.env.timeout(t_off)
            else:
                arrival = self.env.now
                self.counter += 1
                # print("[{}] new arrival: {}".format(self.env.now, (self.id, self.counter, arrival, arrival + self.deadline)))
                self.submit_packet(Packet(self.id, self.counter, arrival, arrival + self.deadline))
                yield self.env.timeout(self.traffic_generator.get_interval())
