import sys
import threading
import json
import pickle
import signal
import time
import os.path
import queue
from collections import defaultdict
from client import Client
from link import Link
from router import Router
from tabulate import tabulate

# Define ANSI escape codes for colors
RED = "\033[91m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"  

class Network:
    """Network class maintains all clients, routers, links, and configuration"""

    def __init__(self, netJsonFilepath, routerClass, visualize=False):
        """Create a new network from the parameters in the file at
           netJsonFilepath. routerClass determines whether to use DVrouter,
           LSrouter, or the default Router"""

        with open(netJsonFilepath, 'r') as netJsonFile:
            netJson = json.load(netJsonFile)  

        self.latencyMultiplier = 100
        self.endTime = netJson["endTime"] * self.latencyMultiplier
        self.visualize = visualize
        if visualize:
            self.latencyMultiplier *= netJson["visualize"]["timeMultiplier"]
        self.clientSendRate = netJson["clientSendRate"] * self.latencyMultiplier

        self.printJsonInTable(netJson)

        self.routers = self.parseRouters(netJson["routers"], routerClass)
        self.clients = self.parseClients(netJson["clients"], self.clientSendRate)
        self.links = self.parseLinks(netJson["links"])

        if "changes" in netJson:
            self.changes = self.parseChanges(netJson["changes"])
        else:
            self.changes = None

        self.correctRoutes = self.parseCorrectRoutes(netJson["correctRoutes"])
        self.threads = []
        self.routes = {}
        self.routesLock = threading.Lock()
        
        
    def printJsonInTable(self, netJson):
        """Print the network JSON data in a tabular format with colors"""

        print(f"\n{CYAN}--- Routers and Clients ---{RESET}")
        devices_table = [
            [f"{RED}Routers{RESET}", f"{BLUE}{', '.join(netJson['routers'])}{RESET}"],
            [f"{YELLOW}Clients{RESET}", f"{GREEN}{', '.join(netJson['clients'])}{RESET}"],
        ]
        print(tabulate(devices_table, headers=["Device Type", "IDs"], tablefmt="grid"))

        print(f"\n{CYAN}--- Links ---{RESET}")
        colored_links = [
            [f"{GREEN}{r1}{RESET}", f"{BLUE}{r2}{RESET}", f"{YELLOW}{c1}{RESET}", f"{YELLOW}{c2}{RESET}", f"{CYAN}{l1}{RESET}", f"{CYAN}{l2}{RESET}"]
            for r1, r2, c1, c2, l1, l2 in netJson["links"]
        ]
        print(tabulate(colored_links, headers=["Router1", "Router2", "Cost1", "Cost2", "Latency1", "Latency2"], tablefmt="grid"))

        print(f"\n{CYAN}--- Correct Routes ---{RESET}")
        colored_routes = [
            [f"{RED}{route[0]}{RESET}", f"{YELLOW}{' -> '.join(route[1:-1])}{RESET}", f"{GREEN}{route[-1]}{RESET}"]
            for route in netJson["correctRoutes"]
        ]
        print(tabulate(colored_routes, headers=["Source", "Path", "Destination"], tablefmt="grid"))

        print(f"\n{CYAN}--- Changes ---{RESET}")
        if netJson.get("changes"):
            colored_changes = [
                [f"{BLUE}{time}{RESET}", f"{RED}{ctype}{RESET}", f"{GREEN}{details}{RESET}"]
                for time, ctype, details in netJson["changes"]
            ]
            print(tabulate(colored_changes, headers=["Time", "Change Type", "Details"], tablefmt="grid"))
        else:
            print(f"{RED}No changes defined in the configuration.{RESET}")


    def parseRouters(self, routerParams, routerClass):
        """Parse routers from routerParams list"""
        routers = {}
        for addr in routerParams:
            routers[addr] = routerClass(addr, heartbeat_time=self.latencyMultiplier * 10)
        return routers

    def parseClients(self, clientParams, clientSendRate):
        """Parse clients from clientParams list"""
        clients = {}
        for addr in clientParams:
            clients[addr] = Client(addr, clientParams, clientSendRate, self.updateRoute)
        return clients

    def parseLinks(self, linkParams):
        """Parse links from linkParams list"""
        links = {}
        for addr1, addr2, p1, p2, c12, c21 in linkParams:
            link = Link(addr1, addr2, c12, c21, self.latencyMultiplier)
            links[(addr1, addr2)] = (p1, p2, c12, c21, link)
        return links

    def parseChanges(self, changesParams):
        """Parse link changes from changesParams list"""
        changes = queue.PriorityQueue()
        for change in changesParams:
            changes.put(change)
        return changes

    def parseCorrectRoutes(self, routesParams):
        """Parse correct routes from routesParams list"""
        correctRoutes = defaultdict(list)
        for route in routesParams:
            src, dst = route[0], route[-1]
            correctRoutes[(src, dst)].append(route)
        return correctRoutes

    def run(self):
        """Run the network."""
        for router in self.routers.values():
            thread = router_thread(router)
            thread.start()
            self.threads.append(thread)
        for client in self.clients.values():
            thread = client_thread(client)
            thread.start()
            self.threads.append(thread)
        self.addLinks()
        if self.changes:
            self.handleChangesThread = handle_changes_thread(self)
            self.handleChangesThread.start()

        if not self.visualize:
            signal.signal(signal.SIGINT, self.handleInterrupt)
            time.sleep(self.endTime / float(1000))
            self.finalRoutes()
            sys.stdout.write("\n" + self.getRouteString() + "\n")
            self.joinAll()

    def addLinks(self):
        """Add links to clients and routers"""
        for addr1, addr2 in self.links:
            p1, p2, c12, c21, link = self.links[(addr1, addr2)]
            if addr1 in self.clients:
                self.clients[addr1].changeLink(("add", link))
            if addr2 in self.clients:
                self.clients[addr2].changeLink(("add", link))
            if addr1 in self.routers:
                self.routers[addr1].changeLink(("add", p1, addr2, link, c12))
            if addr2 in self.routers:
                self.routers[addr2].changeLink(("add", p2, addr1, link, c21))

    def handleChanges(self):
        """Handle changes to links."""
        startTime = time.time() * 1000
        while not self.changes.empty():
            changeTime, target, change = self.changes.get()
            currentTime = time.time() * 1000
            waitTime = (changeTime * self.latencyMultiplier + startTime) - currentTime
            if waitTime > 0:
                time.sleep(waitTime / float(1000))
            if change == "up":
                addr1, addr2, p1, p2, c12, c21 = target
                link = Link(addr1, addr2, c12, c21, self.latencyMultiplier)
                self.links[(addr1, addr2)] = (p1, p2, c12, c21, link)
                self.routers[addr1].changeLink(("add", p1, addr2, link, c12))
                self.routers[addr2].changeLink(("add", p2, addr1, link, c21))
            elif change == "down":
                addr1, addr2 = target
                p1, p2, _, _, link = self.links[(addr1, addr2)]
                self.routers[addr1].changeLink(("remove", p1))
                self.routers[addr2].changeLink(("remove", p2))
            if hasattr(Network, "visualizeChangesCallback"):
                Network.visualizeChangesCallback(change, target)

    def updateRoute(self, src, dst, route):
        """Callback function for route updates."""
        with self.routesLock:
            timeMillisecs = int(round(time.time() * 1000))
            isGood = route in self.correctRoutes[(src, dst)]
            try:
                _, _, currentTime = self.routes[(src, dst)]
                if timeMillisecs > currentTime:
                    self.routes[(src, dst)] = (route, isGood, timeMillisecs)
            except KeyError:
                self.routes[(src, dst)] = (route, isGood, timeMillisecs)

    def getRouteString(self, labelIncorrect=True):
        """Create a string with all the current routes."""
        with self.routesLock:
            routeStrings = []
            allCorrect = True
            incorrect_count = 0
            for src, dst in self.routes:
                route, isGood, _ = self.routes[(src, dst)]
                if isGood or not labelIncorrect:
                    routeStrings.append(
                        f"{GREEN}{src} -> {dst}: {route}{RESET}"
                    )
                else:
                    routeStrings.append(
                        f"{RED}{src} -> {dst}: {route} (Incorrect Route){RESET}"
                    )
                    incorrect_count += 1
                    allCorrect = False
            routeStrings.sort()
            if allCorrect and len(self.routes) > 0:
                routeStrings.append(f"\n{GREEN}SUCCESS: All Routes correct!{RESET}")
            else:
                routeStrings.append(f"\n{RED}FAILURE: {incorrect_count} routes are incorrect. {RESET}")
            return "\n".join(routeStrings)

    def finalRoutes(self):
        """Send one final batch of traceroute packets."""
        self.resetRoutes()
        for client in self.clients.values():
            client.lastSend()
        time.sleep(4 * self.clientSendRate / float(1000))

    def resetRoutes(self):
        """Reset the routes found by traceroute packets."""
        with self.routesLock:
            self.routes = {}

    def joinAll(self):
        if self.changes:
            self.handleChangesThread.join()
        for thread in self.threads:
            thread.join()

    def handleInterrupt(self, signum, _):
        self.joinAll()
        print('')
        quit()


def main():
    """Main function parses command line arguments and runs network"""
    try:
        if len(sys.argv) < 2:
            print("Usage: python network.py [networkSimulationFile.json] [DV|LS (router class, optional)]")
            return
        netCfgFilepath = sys.argv[1]
        routerClass = Router
        if len(sys.argv) >= 3:
            if sys.argv[2] == "DV":
                from DVrouter import DVrouter
                routerClass = DVrouter
            elif sys.argv[2] == "LS":
                from LSrouter import LSrouter
                routerClass = LSrouter
        net = Network(netCfgFilepath, routerClass, visualize=False)
        net.run()
    except:
        print("Error running network simulation.")
        raise


# Extensions of threading.Thread class
class router_thread(threading.Thread):
    def __init__(self, router):
        threading.Thread.__init__(self)
        self.router = router

    def run(self):
        self.router.runRouter()

    def join(self, timeout=None):
        self.router.keepRunning = False
        super(router_thread, self).join(timeout)


class client_thread(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client

    def run(self):
        self.client.runClient()

    def join(self, timeout=None):
        self.client.keepRunning = False
        super(client_thread, self).join(timeout)


class handle_changes_thread(threading.Thread):
    def __init__(self, network):
        threading.Thread.__init__(self)
        self.network = network

    def run(self):
        self.network.handleChanges()


if __name__ == "__main__":
    main()
