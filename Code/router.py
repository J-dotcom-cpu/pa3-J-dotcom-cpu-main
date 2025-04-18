import time
import sys
import _thread
import queue


class Router:
    """Router superclass that handles the details of
       packet send/receive and link changes.
       Subclass this class and override the "handle..." methods
       to implement routing algorithm functionality"""


    def __init__(self, addr, heartbeat_time=None):
        """Initialize Router address and threadsafe queue for link changes"""
        self.addr = addr       # address of router
        self.links = {}        # links indexed by port
        self.linkChanges = queue.Queue()
        self.keepRunning = True


    def changeLink(self, change):
        """Add, remove, or change the cost of a link.
           The change argument is a tuple with first element
           'add', or 'remove' """
        self.linkChanges.put(change)


    def addLink(self, port, endpointAddr, link, cost):
        """Add new link to router"""
        if port in self.links:
            self.removeLink(port)
        self.links[port] = link
        self.handle_new_link(port, endpointAddr, cost)


    def removeLink(self, port):
        """Remove link from router"""
        self.links = {p:link for p,link in self.links.items() if p != port}
        self.handle_remove_link(port)


    def runRouter(self):
        """Main loop of router"""
        while self.keepRunning:
            time.sleep(0.1)
            timeMillisecs = int(round(time.time() * 1000))
            try:
                change = self.linkChanges.get_nowait()
                if change[0] == "add":
                    self.addLink(*change[1:])
                elif change[0] == "remove":
                    self.removeLink(*change[1:])
            except queue.Empty:
                pass
            for port in list(self.links.keys()):
                packet = self.links[port].recv(self.addr)
                if packet:
                    self.handle_packet(port, packet)
            self.handle_time(timeMillisecs)


    def send(self, port, packet):
        """Send a packet out given port"""
        try:
            self.links[port].send(packet, self.addr)
        except KeyError:
            pass


    def handle_packet(self, port, packet):
        """process incoming packet"""
        # default implementation sends packet back out the port it arrived
        self.send(port, packet)


    def handle_new_link(self, port, endpoint, cost):
        """handle new link"""
        pass


    def handle_remove_link(self, port):
        """handle removed link"""
        pass


    def handle_time(self, time_milli_secs):
        """handle current time"""
        pass


    def debug_string(self):
        """generate a string for debugging in network visualizer"""
        return "Mirror router: address {}".format(self.addr)
