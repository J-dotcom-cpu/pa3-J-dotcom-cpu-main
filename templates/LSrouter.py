
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

# from json import dumps, loads
# from collections import defaultdict
from router import Router
from packet import Packet
# import dijkstar
# import networkx
# from copy import deepcopy


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
        """Hints: initialize local state."""
        raise NotImplementedError

    def handle_packet(self, port, packet: Packet):
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
            pass
        else:
            pass
        raise NotImplementedError

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
        raise NotImplementedError

    def handle_remove_link(self, port):
        """
        Handle the removal of a link.

        Args:
            port: The port number of the removed link.

        This method should:
            - Update the forwarding table.
            - Broadcast the new link state of this router to all neighbors.
        """
        raise NotImplementedError

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
            raise NotImplementedError

    def debug_string(self):
        """
        Generate a string for debugging in the network visualizer.

        Returns:
            str: A debug string representing the router's state.
        """
        return ""
