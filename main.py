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

strategy_mapping = {
    "ue": {
        "FCFS": us.fcfs,
        "EDF": us.edf,
        "WFAIR": us.proportionaldivision},
    "rbs": {
        "FCFS": rs.FCFS,
        "EDF": rs.EDF},
    "packet": {
        "FCFS": ps.FCFS,
        "EDF": ps.EDF}
}

traffic_mapping = {
    "continuous":{
        "constant": continuous.constant,
        "exponential": continuous.exponential},
    "on_off":{
        "constant": OnOff.constant,
        "exponential": OnOff.exponential}

}

def main(mu, target, strategy, nodes, mode, deadline, seed, sim_duration, distribution_on=None, distribution_off=None):
    SIM_DURATION = sim_duration
    env = simpy.Environment()
    deadline_max = deadline
    arrival_rate = 0.5
    arrival_dist = "exponential"
    d_on = 100
    d_off = 600
    dir = "traces/ue_scheduling/" + str(mu) + '-' + distribution_on + '_' + distribution_off +  '-' +  target + '-' +  strategy + '-' + str(nodes)+ '-' + str(deadline_max) + '-' + mode + '-' +str(seed)
    args = str(mu) + '-' + distribution_on + '_' +  distribution_off + '-' +  target + '-' +  strategy + '-' + str(nodes)+ '-' + str(deadline_max)

    try:
        os.makedirs(dir)
    except OSError:
        pass

    np.random.seed(seed)
    monitor = Monitor(env, dir)
    scheduler = strategy_mapping[target][strategy](env, monitor)

    def traff_gen(mode, id):
        if mode == "on_off":
            traffic_generator = traffic_mapping[mode][arrival_dist](env, id, arrival_rate, (distribution_on, d_on), (distribution_off, d_off))
        elif mode == "continuous":
            traffic_generator = traffic_mapping[mode][arrival_dist](env, id, arrival_rate)
        return traffic_generator

    channel = Channel(env, monitor)
    cable = [Cable(env, mu), Cable(env, mu)]
    cloud = Cloud(env, cable, scheduler)
    rbs = RBS(env, channel, cable, scheduler, mu)
    # traffic_generator = traff_gen(mode)
    deadlines = np.random.uniform(1,deadline_max, nodes)

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
    load = total_arrivals / (end-start) / 24

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

    loss_rate = loss / total_arrivals

    waste = 0
    pilots = 0
    for w in waste_array:
        if w[0] >= start:
            waste += w[1]
            pilots += 12

    waste = waste/pilots

    return args, loss_rate, waste
