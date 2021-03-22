import unittest
import pytest
import simpy
import numpy as np
import pandas as pd
from strategy.data_struct import Report, Decision, PacketHeader, Packet

def test_create_report(scheduler_edf, channel):
    report_counter = 1
    report = scheduler_edf.create_report(report_counter, channel)
    assert report.id == report_counter
    assert type(report.report) is list
    assert len(report.report) == len(channel.get_queue())

def test_update_ue_register(scheduler_edf, channel):
    queue = channel.get_queue()
    test_list = []
    for p in queue:
        if p.header.node_id not in test_list:
            test_list.append(p.header.node_id)
        if p.header.node_id not in scheduler_edf.ue_register:
            scheduler_edf.update_ue_register(p.header.node_id)
    assert sorted(scheduler_edf.ue_register) == sorted(test_list)

# @pytest.mark.skip(reason="need rewrite")
@pytest.mark.parametrize("nbr_nodes", [1, 5, 10, 12])
def test_assign_pilots_no_waste(scheduler_edf, channel, nbr_nodes):
    queue = channel.get_queue()
    queue_length = len(queue)
    nbr_packets = 2
    nodes = scheduler_edf.create_active_ue_list(queue)
    selected_nodes = np.random.choice(nodes, size=nbr_nodes, replace=False)
    for node in selected_nodes:
        packets_from_ue = [p for p in queue if p.header.node_id == node]
        if len(packets_from_ue) < nbr_packets:
            for p in packets_from_ue:
                queue.remove(p)
                selected_nodes.remove(node)

    decision = Decision(1, selected_nodes)
    waste, served = scheduler_edf.assign_pilots(decision, channel)
    assert len(channel.get_queue()) ==  queue_length - served
    assert waste == 0

# @pytest.mark.skip(reason="need rewrite")
@pytest.mark.parametrize("nbr_nodes", [1, 5, 10, 12])
def test_assign_pilots_has_waste(scheduler_edf, channel, nbr_nodes):
    queue = channel.get_queue()
    new_queue = []
    queue_length = len(queue)
    nbr_packets = 1
    nodes = scheduler_edf.create_active_ue_list(queue)
    selected_nodes = np.random.choice(nodes, size=nbr_nodes, replace=False)
    for node in selected_nodes:
         new_queue += list(np.random.choice([p for p in queue if p.header.node_id == node], size=nbr_packets))
    channel.queue = new_queue
    decision = Decision(1, selected_nodes)
    waste, served = scheduler_edf.assign_pilots(decision, channel)
    assert waste == (scheduler_edf.beta - 1)/scheduler_edf.beta * nbr_nodes
    assert served == nbr_nodes
    assert len(channel.get_queue()) == 0

@pytest.mark.parametrize("nbr_nodes", [1, 5, 10, 12])
def test_assign_pilots_empty_queue(scheduler_edf, channel, nbr_nodes):
    queue = channel.get_queue()
    new_queue = []
    queue_length = len(queue)
    nbr_packets = 0
    nodes = scheduler_edf.create_active_ue_list(queue)
    selected_nodes = np.random.choice(nodes, size=nbr_nodes, replace=False)
    channel.queue = []
    decision = Decision(1, selected_nodes)
    waste, served = scheduler_edf.assign_pilots(decision, channel)
    assert waste == nbr_nodes
    assert served == 0

# @pytest.mark.skip(reason="need rewrite")
def test_init_decision(scheduler_edf):
    decision = scheduler_edf.init_decision()
    assert decision.id == 0
    assert type(decision.decision) is list
    assert decision.decision == list(range(0, scheduler_edf.ue_max_index+1))

# @pytest.mark.skip(reason="need rewrite")
def test_update_init_decision(scheduler_edf):
    decision = scheduler_edf.update_init_decision()
    assert decision.id == 0
    assert type(decision.decision) is list
    assert decision.decision == list(range(0, scheduler_edf.ue_max_index+1))

# @pytest.mark.skip(reason="need rewrite")
def test_make_decision_full_queue(scheduler_edf, channel):
    queue = channel.get_queue()
    decision = scheduler_edf.make_decision(queue, 1)
    assert decision.id == 1
    assert len(decision.decision) == 12
    queue_sorted = sorted(queue, key=lambda x: x.deadline)
    considered_nodes = []
    for p in queue_sorted:
        if p.header.node_id not in considered_nodes:
            considered_nodes.append(p.header.node_id)
            if len(considered_nodes) == 12:
                break
    assert sorted(decision.decision) == sorted(considered_nodes)

# @pytest.mark.skip(reason="need rewrite")
@pytest.mark.parametrize("nbr_nodes", [2, 5, 10, 11])
def test_make_decision_half_queue(scheduler_edf, channel, nbr_nodes):
    queue = channel.get_queue()
    nodes = scheduler_edf.create_active_ue_list(queue)
    selected_nodes = np.random.choice(nodes, size=nbr_nodes, replace=False)
    new_queue = [p for p in channel.get_queue() if p.header.node_id in selected_nodes]
    decision = scheduler_edf.make_decision(new_queue, 1)
    assert decision.id == 1
    assert len(decision.decision) == nbr_nodes
    assert sorted(decision.decision) == sorted(selected_nodes)


# @pytest.mark.skip(reason="need rewrite")
def test_make_decision_empty_queue(scheduler_edf, channel):
    queue = []
    decision = scheduler_edf.make_decision(queue, 1)
    assert decision.id == 1
    assert len(decision.decision) == 0
