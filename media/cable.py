import simpy
import numpy as np
import scipy.stats as st

SIM_DURATION = 100


class Cable(object):
    """This class represents the propagation through a cable."""
    def __init__(self, env, delay_mu):
        self.env = env
        self.store = simpy.Store(env)
        self.mu = delay_mu
        self.loglaplace_param = (3.5586173859556576, 1.9121040460127234, 0.43012023108193775)

    def latency(self, value):
        d  = self.get_delay()
        # print("delay for {}ms".format(d))
        yield self.env.timeout(d)
        yield self.store.put(value)

    def get_delay(self):
        if self.mu == 0:
            return 0
        else:
            s = st.loglaplace.rvs(c=self.loglaplace_param[0],
                                loc=self.mu,
                                scale=self.loglaplace_param[2],
                                size=1)
            # return np.random.lognormal(self.mu, 0.2, 1)[0]/2
            # return abs(np.random.normal(self.mu, 0.3))
            # print(s[0])
            return s[0]/2

    def put(self, value):
        self.env.process(self.latency(value))

    def get(self):
        return self.store.get()
