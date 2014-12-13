import unittest
from dijkstra import *
from dijkstra_paths import *

class node(object):
    def __init__(self, name=None, weight=1, neighbors=None, s_refs=None, resources=[1,1,1,1]):
        self.name = name
        self.weight = weight
        self.v_refs = neighbors if neighbors else []
        self.s_refs = s_refs if s_refs else dict()
        self.resources = resources
    def __repr__(self):
        return self.name

    def add_neighbors(self, s_refs):
        for s in s_refs:
            self.s_refs.append(s)

    def add_neighbors(self, neighbors):
        for neighbor in neighbors:
            self.v_refs.append(neighbor)

class TestDijkstra(unittest.TestCase):
    def setUp(self):
        self.e = node('e')
        self.c = node('c')
        self.b = node('b', neighbors=[self.e], s_refs={self.e: [self.e]})
        self.a = node('a', neighbors=[self.b, self.c], s_refs={self.b: [self.b], self.e:[self.b, self.e]})
        self.d = node('d', neighbors=[self.e])
        self.c.add_neighbors([self.d])
        self.G = [self.a, self.b, self.c, self.d, self.e]

    def test_basic(self):
        self.a.add_neighbors([self.e])
        algorithm = DijkstraAlgorithm()
        path = algorithm.find_path(self.G, self.a, self.e)
        self.assertEqual([self.a, self.e], path)

    def test_alternate(self):
        self.b.weight = 4
        algorithm = DijkstraAlgorithm()
        path = algorithm.find_path(self.G, self.a, self.e)
        self.assertEqual([self.a, self.c, self.d, self.e], path)

    def test_path(self):
        algorithm = DijkstraAlgorithm()
        path = algorithm.find_path(self.G, self.a, self.e)
        self.assertEqual([self.a, self.b, self.e], path)

   # def test_basic_resource(self):
   #     self.a.add_neighbors([self.e])

   #     self.algorithm = DijkstraResourceAlgorithm()
   #     path = self.algorithm.find_path(self.G, self.a, self.e)
   #     self.assertEqual([self.a, self.e], path)

   # def test_alternate_resource(self):
   #     self.b.resources = [3, 3, 3, 3]

   #     self.algorithm = DijkstraResourceAlgorithm()
   #     path = self.algorithm.find_path(self.G, self.a, self.e)
   #     self.assertEqual([self.a, self.c, self.d, self.e], path)

   # def test_path_resource(self):
   #     self.algorithm = DijkstraResourceAlgorithm()
   #     path = self.algorithm.find_path(self.G, self.a, self.e)
   #     self.assertEqual([self.a, self.b, self.e], path)
   # # TODO: make better resource tests

   # def test_path_resource(self):
   #     self.algorithm = DijkstraSettlementAlgorithm()
   #     path = self.algorithm.find_path(self.G, self.a, self.e)
   #     self.assertEqual([self.a, self.b, self.e], path)

   # def test_all_paths(self):
   #     self.a.add_neighbors([self.e])
   #     self.d.add_neighbors([self.b])
   #     self.a.add_neighbors([self.d])
   #     algorithm = DijkstraPathAlgorithm()
   #     path = algorithm.find_path(self.G, self.a, self.e, 4)
   #
   #     #self.assertEqual([self.a, self.e], path)

    def test_path_resource(self):
        self.algorithm = DijkstraResourceAlgorithm()
        path, s_path = self.algorithm.find_path(self.G, self.a, self.e)
        self.assertEqual([self.a, self.b, self.e], path)
    # TODO: make better resource tests

    def test_path_resource(self):
        self.algorithm = DijkstraSettlementAlgorithm()
        path, s_path = self.algorithm.find_path(self.G, self.a, self.e)
        self.assertEqual([self.a, self.b, self.e], path)
if __name__ == "__main__":
    unittest.main()
