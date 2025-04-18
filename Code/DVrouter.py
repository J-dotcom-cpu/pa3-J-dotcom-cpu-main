
"""
DVrouter: Implementation of the Distance Vector Routing Protocol.

This module defines the `DVrouter` class, which inherits from the `Router` class.
The `DVrouter` class is responsible for handling distance vector updates, packet
processing, and routing decisions in a network simulation. It uses periodic
broadcasts to propagate the distance vector to all neighbors.

Class:
    DVrouter: Implements distance vector routing protocol methods for:
        - Handling packets
        - Managing link changes
        - Periodic updates based on time
        - Debugging
"""
from router import Router
from packet import Packet
import json

INFINITY = float('inf')

class DVrouter(Router):
    """
    Distance Vector Routing Protocol Implementation.

    Handles distance vector updates, packet processing, and routing decisions.
    """

    def __init__(self, addr, heartbeat_time):
        """
        Initialize the DVrouter instance.

        Args:
            addr: The address of the router.
            heartbeat_time: Time interval for broadcasting distance vectors.
        """
        Router.__init__(self, addr)  # initialize superclass - don't remove
        self.heartbeat_time = heartbeat_time
        self.last_time = 0
        """Hints: initialize local state."""
        self.neighbor_costs = {}         
        self.distance_vector = {addr: 0} 
        self.next_hop = {addr: None}    

    def _broadcast_dv(self):
        """
        Broadcast this router's distance vector to all neighbors.
        """
        payload = json.dumps(self.distance_vector)
        pkt = Packet(Packet.ROUTING, self.addr, None, payload)
        for port in self.neighbor_costs:
            self.send(port, pkt)

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
            - Check if the received distance vector is different.
            - If the received distance vector is different:
                - Update the local copy of the distance vector.
                - Update the distance vector of this router.
                - Update the forwarding table.
                - Broadcast the distance vector of this router to neighbors.
        """
        if packet.is_traceroute():
            dst = packet.dstAddr
            if dst in self.next_hop and self.next_hop[dst] is not None:
                self.send(self.next_hop[dst], packet)
            return

        if packet.kind == Packet.ROUTING:
            received = json.loads(packet.content)
            updated = False
            cost_to_nbr = self.neighbor_costs.get(port, INFINITY)
            # Apply Bellman-Ford equation: D(x,y) = min(c(x,v) + D(v,y))
            for dest, nbr_cost in received.items():
                new_cost = cost_to_nbr + nbr_cost
                current_next_hop = self.next_hop.get(dest)
                current_cost = self.distance_vector.get(dest, INFINITY)
                if new_cost < current_cost or (port == current_next_hop and new_cost != current_cost):
                    self.distance_vector[dest] = new_cost
                    self.next_hop[dest] = port
                    updated = True
                
                # If route through current next hop is now infinity, we need to find alternative
                if port == current_next_hop and nbr_cost == INFINITY:
                    for p, p_cost in self.neighbor_costs.items():
                        if p != port:  
                            self._broadcast_dv()
                    self.distance_vector[dest] = INFINITY
                    self.next_hop[dest] = None
                    updated = True

            if updated:
                self._broadcast_dv()

    def handle_new_link(self, port, endpoint, cost):
        """
        Handle the establishment of a new link.

        Args:
            port: The port number of the new link.
            endpoint: The endpoint address of the new link.
            cost: The cost of the new link.

        This method should:
            - Update the distance vector of this router.
            - Update the forwarding table.
            - Broadcast the distance vector of this router to neighbors.
        """
        self.neighbor_costs[port] = cost
        self.distance_vector[endpoint] = cost
        self.next_hop[endpoint] = port
        self._broadcast_dv()

    def handle_remove_link(self, port):
        """
        Handle the removal of a link.

        Args:
            port: The port number of the removed link.

        This method should:
            - Update the distance vector of this router.
            - Update the forwarding table.
            - Broadcast the distance vector of this router to neighbors.
        """
        if port not in self.neighbor_costs:
            return
        lost_destinations = [dest for dest, next_port in self.next_hop.items() 
                           if next_port == port]
        del self.neighbor_costs[port]
        updated = False
        for dest in lost_destinations:
            self.distance_vector[dest] = INFINITY
            self.next_hop[dest] = None
            updated = True
        if updated:
            self._broadcast_dv()

    def handle_time(self, time_milli_secs):
        """
        Handle periodic tasks based on the current time.

        Args:
            time_milli_secs: The current time in milliseconds.

        If the time since the last broadcast exceeds the heartbeat interval:
            - Broadcast the distance vector of this router to neighbors.
        """
        if time_milli_secs - self.last_time >= self.heartbeat_time:
            self.last_time = time_milli_secs
            self._broadcast_dv()

    def debug_string(self):
        #raise NotImplementedError
        return