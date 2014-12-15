class DijkstraAlgorithm(object):
    """Find the shortest path between settlements"""

    def __init__(self):
        self.large_number = 1e4 # large number greater than any distance in the tree
        self.minimum = 0
        self.G = None
        self.source = None
        self.target = None

    def reset(self, G, source, target):
        """reset all dictionaries if there is a new source or graph"""
        self.G = G
        self.source = source
        self.target = target
        self.dist = {}
        self.dist[source] = self.minimum
        self.previous = {}

        # build distance and previous node dictionaries
        for v in self.G:
            if v != self.source:
                self.dist[v] = self.update_distance(self.large_number, self.source)
            self.previous[v] = None

    def dijkstra(self):
        unvisited_nodes = set(self.G)

        while len(unvisited_nodes):
            # pick the node closest to source that has not been picked
            min_dist = [None, self.large_number]

            for n in unvisited_nodes:
                if self.compare(self.dist[n], min_dist[1]):
                    min_dist = [n, self.dist[n]]
            u = min_dist[0]
            unvisited_nodes.remove(u) # remove the node you picked from unvisited_nodes

            v_refs = self.get_refs(u)
            for v in v_refs:
                if v:
                    alt = self.update_distance(self.dist[u], v)
                    # update dist of the neighbor if this is a closer route
                    if self.compare(alt, self.dist[v]):
                        self.dist[v] = alt
                        self.previous[v] = u

    def find_path(self, G, source, target, reset=False):
        """Return the path to target from the source node
        Inputs:
            G - a list containing all nodes in the graph
            source - start node for the path
            target - node to end at
        """
        if target != self.target:
            self.target = target
        if source != self.source or G != self.G or reset:
            self.reset(G, source, target)
            self.dijkstra()

        path = [self.target]
        u = self.target
        while self.previous[u]:
            u = self.previous[u]
            path.append(u)
        if path[-1] != self.source:
            raise ValueError('%s does not equal the expected start node, %s'
                             % (path[-1], self.source))
        return path[::-1], [self.source, self.target]

    @staticmethod
    def get_refs(v):
        """get the vertices one segment away from v"""
        return v.v_refs

    @staticmethod
    def update_distance(x, v):
        return x + v.weight

    @staticmethod
    def compare(x, y):
        return x <= y


class DijkstraResourceAlgorithm(DijkstraAlgorithm):
    """Find path based off of resource tuple"""

    def __init__(self):
        DijkstraAlgorithm.__init__(self)
        self.large_number = [1e4, 1e4, 1e4, 1e4, 1e4, 1e4] # large number greater than any distance in the tree
        self.minimum = [0, 0, 0, 0, 0, 0]

    @staticmethod
    def compare(x, y):
        return sum(x) <= sum(y)

    @staticmethod
    def update_distance(x, v):
        """Add the square of the resource value to the neighbor resource value

        The square makes it so our algorithm prefers a diverse set of resources
        instead of just a low number because (x+y)^2 > x^2 + y^2. so a vertex
        with two of the same resources will create a larger number than a vertex
        with all different resources even if their values sum to the same thing.
        """
        return [res_val + v.resources[i]**2 for i, res_val in enumerate(x)]


class DijkstraSettlementAlgorithm(DijkstraAlgorithm):
    """Find path based off of settlement placement"""

    @staticmethod
    def get_refs(v):
        """Get neighbor settlement refs for vertex v."""
        return v.s_refs

    def find_path(self, G, source, target, reset=False):
        """Return the path to target from the source node
        Inputs:
            G - a list containing all nodes in the graph
            source - start node for the path
            target - node to end at
        """
        if target != self.target:
            self.target = target
        if source != self.source or G != self.G or reset:
            self.reset(G, source, target)
            self.dijkstra()

        path = [self.target]
        u = self.target
        while self.previous[u]:
            u = self.previous[u]
            path.append(u)
        if path[-1] != self.source:
            raise ValueError('%s does not equal the expected start node, %s'
                             % (path[-1], self.source))
        return self.get_road_path(source, path)

    def get_road_path(self, source, path):
        """Connect settlements in path using connecting vertices
        Returns:
            The list of connecting roads,
             the list of vertices with a settlement"""
        path = path[::-1]
        newPath = reduce(lambda x, y: x + y, [v1.s_refs[v2] for v1,v2 in zip(path, path[1:])])
        return [source] + newPath, path


class DijkstraResourceSettlementAlgorithm(DijkstraSettlementAlgorithm,
                                          DijkstraResourceAlgorithm):
    """Find settlement path based off of resource tuple"""
    def __init__(self):
        DijkstraResourceAlgorithm.__init__(self)

class DijkstraPathAlgorithm(DijkstraSettlementAlgorithm,
                            DijkstraAlgorithm):
    """Find all paths less than or equal to some length from a source to a target"""

    @staticmethod
    def get_refs(v):
        """Get neighbor settlepython mment refs for vertex v."""
        return v.s_refs

    def reset(self, G, source, target):
        self.G = G
        self.source = source
        self.target = target
        self.dist = {}
        self.dist[source] = [[self.minimum, [self.source]]]
        self.previous = {}

        # build distance and previous node dictionaries
        for v in self.G:
            if v != self.source:
                self.dist[v] = [[self.large_number, []]]
            self.previous[v] = {}

    def find_min(self, paths):
        minimum = self.large_number
        for l, p in paths:
            if minimum >= l:
                minimum = l
        return minimum

    def dijkstra(self, length):
        unvisited_nodes = set(self.G)

        while len(unvisited_nodes):
            # pick the node closest to source that has not been picked
            min_dist = [None, self.large_number]

            for n in unvisited_nodes:
                x = self.find_min(self.dist[n])
                if x <= min_dist[1]:
                    min_dist = [n, self.find_min(self.dist[n])]
            u = min_dist[0]
            unvisited_nodes.remove(u) # remove the node you picked from unvisited_nodes

            v_refs = self.get_refs(u)
            for v in v_refs:
                if v:
                    alt = self.update_distance(self.dist[u], v)
                    # add path option if it is less than the max length
                    for val in alt:
                        if val[0] <= length:
                            if self.dist[v] == [[self.large_number, []]]:
                                self.dist[v] = []
                            self.dist[v].append(val)
                            if u not in self.previous[v]:
                                self.previous[v][u] = [val]
                            else:
                                self.previous[v][u].append(val)

    def find_all_paths(self, G, source, target, length, reset=False):
        """Return all paths to target from the source node with a distance <= length
        Inputs:
            G - a list containing all nodes in the graph
            source - start node for the path
            target - node to end at
            length - max length of paths
        """
        if target != self.target:
            self.target = target
        if source != self.source or G != self.G or reset:
            self.reset(G, source, target)
            self.dijkstra(length)
        # return [p for l, p in self.dist[target]]
        return [self.get_road_path(source, p[::-1]) for l, p in self.dist[target]]

    @staticmethod
    def update_distance(x, v):
        return [[i + 1, p + [v]] for i, p in x if v not in p]
