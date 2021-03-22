import os
import numpy as np
from multiprocessing import Pool
import json
import time
from main_ue_edf import main_ue_edf
import matplotlib.pyplot as plt
import scipy.stats as st


mu = 2
deadline = 10
nodes = 1
beta = 3
seed =17833650
type = "homogeneous"
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
    'arrival_rate_min': 2.5,
    'arrival_rate_max': 7.5
}

traffic_properties = traffic_properties_default
traffic_properties['deadline'] = deadline
traffic_properties['traffic_type'] = type

args, loss, waste = main_ue_edf(mu, nodes, mode, beta, seed, 2000, traffic_properties)
print(args)
print(loss, waste)
