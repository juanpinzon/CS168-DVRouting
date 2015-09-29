from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        """ Add your code here! """
        self.f_table = {}
        self.port_table = {}
        self.r_packet = RoutingUpdate()
        self.least_cost_path = []
        self.neighbors = {}

    def handle_rx (self, packet, port):
        """ Add your code here! """

        if (isinstance(packet, DiscoveryPacket)):
            self.handle_discovery(packet, port, self.r_packet)
        elif (isinstance(packet, RoutingUpdate)):
            self.handle_RoutingUpdate(packet)
        else:
            self.send(packet, port, flood = True)

    def handle_discovery(self, packet, port, r_packet):

        if (self.name not in self.f_table.keys()):
            self.f_table[self.name] = {}
            self.f_table[self.name][self.name] = (0, self.name)
            self.neighbors[self.name] = []

        # if a link is down, update the router's forwarding table and drop packet.
        if not (packet.is_link_up):
            packet.latency = float("inf") # fix this!

        self.f_table[self.name][packet.src.name] = (packet.latency, self.name)
        # Add neighbor to the Routing Update packet.
        self.neighbors[self.name].append(packet.src.name)
        r_packet.add_destination(packet.src.name, packet.latency)
        self.port_table[packet.src.name] = port
        # send routing update packet from DV Router to neighbors.
        for port in self.port_table:
            self.send(r_packet, port, flood = False)

    def handle_RoutingUpdate(self, r_packet):
        for name in r_packet.all_dests():
            src = r_packet.src.name # src of packet.
            distance = r_packet.get_distance(name) # distance of neighbor.
            if (src not in self.f_table.keys()):
                self.f_table[src] = {}
                self.f_table[src][src] = (0, src)
            self.f_table[src][name] = (distance, src)
            if (name not in self.f_table[self.name]):
                self.f_table[self.name][name] = (999, src)
        
        for name in r_packet.all_dests():
            src = r_packet.src.name 
            for key in self.f_table[self.name]:
                if (key not in self.f_table[src]):
                    if (key == self.name):
                        self.f_table[src][key] = (self.f_table[self.name][src][0], src)
                    else:
                        self.f_table[src][key] = (999, self.name)
        
        for r_pckt in r_packet.all_dests():
            src = r_packet.src.name
            if (r_pckt in self.f_table[self.name]):
                cost = self.f_table[self.name][src][0]
                d_cost = self.f_table[src][r_pckt][0]
                total = cost + d_cost
                if (total < self.f_table[self.name][r_pckt][0]):
                    self.f_table[self.name][r_pckt] = (total, src)
                    r_packet.add_destination(r_pckt, total)