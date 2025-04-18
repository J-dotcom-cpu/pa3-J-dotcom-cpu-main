
"""
LSrouter: Implementation of the Link State Routing Protocol.

This module defines the `LSrouter` class, which inherits from the `Router` class.
The `LSrouter` class is responsible for handling link state updates, packet processing,
and routing decisions in a network simulation. It uses periodic broadcasts to 
propagate the link state to all neighbors.

Class:
    LSrouter: Implements link state routing protocol methods for:
        - Handling packets
        - Managing link changes
        - Periodic updates based on time
        - Debugging
"""

from json import dumps, loads
from router import Router
from packet import Packet

class LSrouter(Router):
    """Link state routing protocol implementation."""

    def __init__(self, addr, heartbeat_time):
        """
        Initialize the LSrouter instance.

        Args:
            addr: The address of the router.
            heartbeat_time: Time interval for broadcasting link states.
        """
        Router.__init__(self, addr)  # initialize superclass - don't remove
        self.heartbeat_time = heartbeat_time
        self.last_time = 0
        self.ls_database = {}  
        # My own link state info
        self.sequence_number = 0
        self.neighbors = {} 
        self.forwarding_table = {}

    def handle_packet(self, port, packet):
        """
        Process an incoming packet.

        Args:
            port: The port on which the packet was received.
            packet: The packet to process.

        If the packet is a normal data packet:
            - Check if the forwarding table contains the packet's destination address.
            - Send the packet based on the forwarding table.
        If the packet is a routing packet:
            - Check the sequence number.
            - If the sequence number is higher and the received link state is different:
                - Update the local copy of the link state.
                - Update the forwarding table.
                - Broadcast the packet to other neighbors.
        """
        if packet.is_traceroute():
            if packet.dstAddr in self.forwarding_table:
                next_hop = self.forwarding_table[packet.dstAddr]
                self.send(next_hop, packet)
            return

        if packet.kind == Packet.ROUTING:
            ls_info = loads(packet.content)
            sender = ls_info['sender']
            seq_num = ls_info['seq']
            neighbors = ls_info['neighbors']
            
            is_new = False
            if sender not in self.ls_database or seq_num > self.ls_database[sender][0]:
                self.ls_database[sender] = (seq_num, neighbors)
                is_new = True
                
                self._compute_routes()
                
                if is_new:
                    for p in self.neighbors:
                        if p != port:  # Don't send back
                            self.send(p, packet)

    def handle_new_link(self, port, endpoint, cost):
        """
        Handle the establishment of a new link.

        Args:
            port: The port number of the new link.
            endpoint: The endpoint address of the new link.
            cost: The cost of the new link.

        This method should:
            - Update the forwarding table.
            - Broadcast the new link state of this router to all neighbors.
        """
        self.neighbors[port] = (endpoint, cost)
        self._update_and_broadcast_ls()
        self._compute_routes()

    def handle_remove_link(self, port):
        """
        Handle the removal of a link.

        Args:
            port: The port number of the removed link.

        This method should:
            - Update the forwarding table.
            - Broadcast the new link state of this router to all neighbors.
        """
        if port in self.neighbors:
            del self.neighbors[port]
            self._update_and_broadcast_ls()
            self._compute_routes()

    def handle_time(self, time_milli_secs):
        """
        Handle periodic tasks based on the current time.

        Args:
            time_milli_secs: The current time in milliseconds.

        If the time since the last broadcast exceeds the heartbeat interval:
            - Broadcast the link state of this router to all neighbors.
        """
        if time_milli_secs - self.last_time >= self.heartbeat_time:
            self.last_time = time_milli_secs
            self._update_and_broadcast_ls()

    def _update_and_broadcast_ls(self):
        """
        Update our link state info and broadcast it to all neighbors.
        """
        self.sequence_number += 1
        neighbor_info = {}
        for port, (addr, cost) in self.neighbors.items():
            neighbor_info[addr] = cost

        ls_info = {
            'sender': self.addr,
            'seq': self.sequence_number,
            'neighbors': neighbor_info
        }

        self.ls_database[self.addr] = (self.sequence_number, neighbor_info)
        packet_content = dumps(ls_info)
        packet = Packet(Packet.ROUTING, self.addr, None, packet_content)
        for port in self.neighbors:
            self.send(port, packet)

    def _compute_routes(self):
        """
        Compute routes using Dijkstra's algorithm.
        """
        graph = {}
        for router, (_, neighbors) in self.ls_database.items():
            if router not in graph:
                graph[router] = {}
            for neighbor, cost in neighbors.items():
                graph[router][neighbor] = cost
                if neighbor not in graph:
                    graph[neighbor] = {}
        # Run Dijkstra's algorithm
        distances = {self.addr: 0}
        predecessors = {}
        unvisited = list(graph.keys())
        
        while unvisited:
            current = None
            min_dist = float('inf')
            for node in unvisited:
                if node in distances and distances[node] < min_dist:
                    current = node
                    min_dist = distances[node]
            if current is None:
                break    
            unvisited.remove(current)
            if current in graph:
                for neighbor, cost in graph[current].items():
                    distance = distances[current] + cost
                    if neighbor not in distances or distance < distances[neighbor]:
                        distances[neighbor] = distance
                        predecessors[neighbor] = current
        self.forwarding_table = {}
        for dest in distances:
            if dest != self.addr:
                next_hop = dest
                while next_hop in predecessors and predecessors[next_hop] != self.addr:
                    next_hop = predecessors[next_hop]
                for port, (addr, _) in self.neighbors.items():
                    if addr == next_hop:
                        self.forwarding_table[dest] = port
                        break

    def debug_string(self):
        #raise NotImplementedError
        return