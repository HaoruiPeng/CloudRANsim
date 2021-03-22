import pytest
import simpy
import numpy as np
import pandas as pd
import strategy.ue_scheduler as us
from media.channel import Channel
from media.cable import Cable
from strategy.data_struct import Report, Decision, PacketHeader, Packet

@pytest.fixture(scope="function")
def channel():
    env =  simpy.Environment()
    channel = Channel(env)
    packets = pd.read_pickle("datafiles/packets.pkl")
    for index, row in packets.iterrows():
        channel.queue.append(Packet(int(row['id']), int(row['counter']), row['arrival'], row['arrival']+row['deadline']))
    yield channel
    print("teardown channel")

@pytest.fixture(scope="function")
def scheduler():
    env =  simpy.Environment()
    beta = 1
    scheduler = us.scheduler(env, beta)
    return scheduler

@pytest.fixture(scope="function")
def scheduler_edf():
    env =  simpy.Environment()
    beta = 1
    scheduler_edf = us.edf(env, beta)
    return scheduler_edf


@pytest.fixture(scope="function")
def scheduler_fcfs():
    env =  simpy.Environment()
    beta = 1
    scheduler_fcfs = us.fcfs(env, beta)
    return scheduler_fcfs

@pytest.fixture(scope="function")
def scheduler_pd():
    env =  simpy.Environment()
    beta = 1
    scheduler_wfair = us.proportionaldivision(env, beta)
    return scheduler_wfair

@pytest.fixture(scope="function")
def cable():
    env = simpy.Environment()
    mu = 1.5
    cable = Cable(env, mu)
    return cable
