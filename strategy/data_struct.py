import simpy


class Report(object):
    """docstring for Report."""
    def __init__(self, id, time, report):
        self.id = id
        self.time = time
        self.report = report


class Decision(object):
    def __init__(self, id, decision):
        self.id = id
        self.decision = decision

class PacketHeader(object):
    """docstring for PacketHeader."""
    def __init__(self, node_id, counter):
        self.node_id = node_id
        self.packet_counter = counter
    def __eq__(self, other):
        if not isinstance(other, PacketHeader):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.node_id == other.node_id and self.packet_counter == other.packet_counter

class Packet(object):
    """Packet = PacketHeader + arrival + departure"""
    def __init__(self, id, counter, arrival, deadline):
        self.header = PacketHeader(id, counter)
        self.arrival = arrival
        self.deadline = deadline
