import simpy
from user.ue import UE
from user.ue import Packet
from rbs.rbs import RBS
from cloud.cloud import Cloud
from monitor.monitor import Monitor
from media.channel import Channel
from media.cable import Cable
import strategy.packet_scheduler as ps
import strategy.ue_scheduler as us
import strategy.rbs_scheduler as rs
import traffic_generator.continuous as continuous
import traffic_generator.on_off as OnOff
import numpy as np
from collections import namedtuple
import matplotlib.pyplot as plt
import pandas as pd
import pickle
import os
import sys

traffic_mapping = {
    "continuous":{
        "constant": continuous.constant,
        "exponential": continuous.exponential},
    "on_off":{
        "constant": OnOff.constant,
        "exponential": OnOff.exponential}
}

traffic_properties_default = {
    'traffic_type': None,
    'deadline': None,
    'arrival_dist': None,
    'distribution_on': None,
    'distribution_off': None,
    'd_on': None,
    'd_off': None,
    'arrival_rate': None,
    'arrival_rate_min': None,
    'arrival_rate_max': None
}

# def main(mu, target, strategy, nodes, mode, deadline, seed, sim_duration, distribution_on=None, distribution_off=None):
def main_ue_edf(mu, nodes, mode, beta, seed, sim_duration, traffic_props):
    SIM_DURATION = sim_duration
    env = simpy.Environment()

    deadline_max = traffic_props['deadline']
    traffic_type = traffic_props['traffic_type']
    arrival_dist = traffic_props['arrival_dist']
    print(traffic_props)
    np.random.seed(seed)

    if traffic_type == 'homogeneous':
        arrival_rates = np.ones(nodes) * traffic_props['arrival_rate']
        deadline_min = traffic_props['arrival_rate']
        arrival_mean = traffic_props['arrival_rate']
    elif traffic_type == 'heterogeneous':
        arrival_rates = np.random.uniform(traffic_props['arrival_rate_min'], traffic_props['arrival_rate_max'], size=nodes)
        arrival_mean = 0.5 * (traffic_props['arrival_rate_min'] + traffic_props['arrival_rate_max'])
        deadline_min = traffic_props['arrival_rate_min']
        # print('heterogeneous')

    # print(arrival_rates)
    print(np.mean(arrival_rates))

    if mode == "on_off":
        distribution_on = traffic_props['distribution_on']
        distribution_off = traffic_props['distribution_off']
        d_on = traffic_props['d_on']
        d_off = traffic_props['d_off']
        traffic_profile = mode + '_' + distribution_on + '-' + traffic_type
    else:
        traffic_profile = mode + '-' + traffic_type

    trace_dir = "traces/softcom_lowrate"
    dir = os.path.join(trace_dir, str(mu) + '-' + str(beta) + '-' + str(nodes)+ '-' + str(arrival_mean) + '-'  + str(deadline_max) + '-' + traffic_profile + '-' +str(seed))
    args = str(mu) + '-' + str(beta) + '-' + str(nodes)+ '-' + str(arrival_mean) + '-' + str(deadline_max) + '-' + traffic_profile
    try:
        os.makedirs(dir)
    except OSError:
        pass

    monitor = Monitor(env, dir)
    scheduler = us.edf(env, beta, monitor)

    def traff_gen(mode, id):
        if mode == "on_off":
            traffic_generator = traffic_mapping[mode][arrival_dist](env, id, arrival_rates[i], (distribution_on, d_on), (distribution_off, d_off))
        elif mode == "continuous":
            traffic_generator = traffic_mapping[mode][arrival_dist](env, id, arrival_rates[i])
        return traffic_generator

    channel = Channel(env, monitor)
    loglaplace_base = 0.46699687428378805
    if mu == 0:
        mu_loc = 0
    else:
        mu_loc = mu - loglaplace_base
    cable = [Cable(env, mu_loc), Cable(env, mu_loc)]
    cloud = Cloud(env, cable, scheduler)
    rbs = RBS(env, channel, cable, scheduler, mu, beta)
    # traffic_generator = traff_gen(mode)
    deadlines = np.random.uniform(deadline_min,deadline_max, nodes)

    ue = []
    for i in range(nodes):
        ue.append(UE(env, i, channel, 0, deadlines[i], traff_gen(mode, i)))

    env.run(until = SIM_DURATION)

    # rho = (1/0.5 * 50 /250) * 10 * 10000
    # print("estimate nbr. packet: {}".format(rho))
    # print(channel.get_queue_len())

    arrival_array = np.array(channel.get_arrivals())
    print(len(arrival_array))
    end = arrival_array[-1]
    # print(end)
    start = 500
    index = 0
    for i in range(len(arrival_array)):
        if arrival_array[i] >= start:
            break

    total_arrivals = len(arrival_array[i:-1])
    print(total_arrivals)
    # load = total_arrivals / (end-start) / 24

    pd.DataFrame(arrival_array, columns=["arrival_time"]).to_pickle(dir+"/arrivals.pkl")
    monitor.dump_to_file()

    loss_array = monitor.get_loss()
    # print(loss_array)

    waste_array = monitor.get_waste()
    # print(waste_array)
    loss = 0
    for l in loss_array:
        if l[0] >= start:
            loss += l[1]

    loss_probability = loss / total_arrivals

    waste = 0
    pilots = 0
    for w in waste_array:
        if w[0] >= start:
            waste += w[1]
            pilots += 12*beta

    waste = waste/pilots

    return args, loss_probability, waste
