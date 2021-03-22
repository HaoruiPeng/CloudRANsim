import os
import numpy as np
from multiprocessing import Pool
import json
import time
from main import main
import matplotlib.pyplot as plt
import scipy.stats as st

PROCESSES = 6
pool = Pool(processes=PROCESSES)

mu_list = [0, 4, 8, 12, 16, 20]
distribution = ("pareto", "constant")
deadlines = [20]
strategies = ['WFAIR', 'EDF', 'FCFS']
targets = ['ue']
mode = "on_off"
nodes = [18, 27, 9, 4, 32]
plt.style.use('ggplot')

target_plot_nbr = dict(zip(targets, [0, 1, 2]))
strategy_plot_label_nbr = dict(zip(strategies, [0, 1, 2]))
color_list = list(plt.rcParams['axes.prop_cycle'])[0:3]
Dict = {}


def collect_results(results):
    if results is None:
        pass
    else:
        args, loss, waste = results
        print(args)
        if args not in Dict.keys():
            new_entry = dict.fromkeys([args], [])
            Dict.update(new_entry)
        Dict[args].append((loss, waste))
        if len(Dict[args]) == 20:
            print("Done: {}".format(args))

seed=np.random.randint(1,200000)
for target in targets:
        for deadline in deadlines:
            for strategy in strategies:
                for node in nodes:
                    for mu in mu_list:
                        for run in range(0, 20):
                            seed += np.random.randint(1, 100000)
                            # print(mu, target, strategy, node, distribution, deadline, seed)
                            pool.apply_async(main, (mu, target, strategy, node, mode, deadline, seed, 300000, distribution[0], distribution[1]), callback=collect_results)

pool.close()
pool.join()
print("All simulations completed!")
