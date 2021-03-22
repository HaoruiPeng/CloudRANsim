import os
import numpy as np
from multiprocessing import Pool
import json
import time
from main_ue_edf import main_ue_edf
import matplotlib.pyplot as plt
import scipy.stats as st

PROCESSES = 4
pool = Pool(processes=PROCESSES)

mu_list = [0, 0.5, 2, 4, 6, 8]
# mu_list = [0,]
distributions = ["pareto", "constant"]
# deadlines = [5, 10, 15]
deadlines = [10]
# deadlines = [5,10]
# types = ["homogeneous", "heterogeneous"]
types = ["homogeneous"]
# nodes = [12, 4, 9, 1]
nodes = [1]
# betas = [1]
betas = [1, 2, 3]
plt.style.use('ggplot')
Dict = {}
def collect_results(results):
    if results is None:
        pass
    else:
        args, loss, waste = results
        print(args)
        print("loss: {}".format(loss))
        print("waste: {}".format(waste))

seed=np.random.randint(1,200000)

mode = "continuous"
traffic_properties_default = {
    'traffic_type': None,
    'deadline': None,
    'arrival_dist': 'constant',
    'distribution_on': None,
    'distribution_off': 'constant',
    'd_on': 100,
    'd_off': 600,
    'arrival_rate': 10,
    'arrival_rate_min': 0.2,
    'arrival_rate_max': 0.8
}
for deadline in deadlines:
    for type in types:
        traffic_properties = traffic_properties_default.copy()
        traffic_properties['traffic_type'] = type
        traffic_properties['deadline'] = deadline
        for beta in betas:
            for node in nodes:
                for mu in mu_list:
                    for run in range(0, 1):
                        seed += np.random.randint(1, 100000)
                        print(mu, beta, node, deadline, traffic_properties['traffic_type'], seed)
                        pool.apply_async(main_ue_edf, (mu, node, mode, beta, seed, 2000, traffic_properties), callback=collect_results)


# mode = "on_off"
# traffic_properties_default = {
#     'traffic_type': 'heterogeneous',
#     'deadline': None,
#     'arrival_dist': 'constant',
#     'distribution_on': None,
#     'distribution_off': 'constant',
#     'd_on': 100
#     'd_off': 600,
#     'arrival_rate': 0.5,
#     'arrival_rate_min': 0.2,
#     'arrival_rate_max': 0.8
# }
#
# for deadline in deadlines:
#     for distribution in distributions:
#         traffic_properties = traffic_properties_default.copy()
#         traffic_properties['deadline'] = deadline
#         traffic_properties['distribution_on'] = distribution
#         for beta in betas:
#             for node in nodes:
#                 for mu in mu_list:
#                     for run in range(0, 5):
#                         seed += np.random.randint(1, 100000)
#                         pool.apply_async(main_ue_edf, (mu, node, mode, beta, seed, 200000, traffic_properties), callback=collect_results)

pool.close()
pool.join()
print("All simulations completed!")
