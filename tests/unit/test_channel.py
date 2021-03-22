import unittest
import pytest
import simpy
import numpy as np
import pandas as pd
from strategy.data_struct import PacketHeader, Packet


@pytest.mark.parametrize(
"time", [0.5, 1, 2, 10, 100])
def test_handle_expir(channel, time):
    channel.handle_expir(time)
    for p in channel.queue:
        assert p.deadline > time

@pytest.mark.parametrize(
"nodes", [1, 3, 5])
def test_serve(channel, nodes):
    ids = np.random.choice(range(0, 20), size=nodes, replace=False)
    headers = []
    queue = channel.get_queue()
    print(queue)
    for i in ids:
        nbr_pakets = len([p for p in queue if p.header.node_id == i])
        counts = np.random.choice(range(1, nbr_pakets+1))
        for c in range(1, counts+1):
            headers.append(PacketHeader(i, c))
    channel.serve(headers)
    for p in headers:
        assert p not in [packet.header for packet in channel.queue]


@pytest.mark.parametrize(
"nodes", [1, 3, 5])
def test_serve_reverse(channel, nodes):
    ids = np.random.choice(range(0, 20), size=nodes, replace=False)
    headers = []
    queue = channel.get_queue()
    for i in ids:
        nbr_pakets = len([p for p in queue if p.header.node_id == i])
        counts = np.random.choice(range(1, nbr_pakets+1))
        for c in range(1, counts+1):
            headers.append(PacketHeader(i, c))
    headers.append(PacketHeader(i, 100))
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        channel.serve(headers)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
