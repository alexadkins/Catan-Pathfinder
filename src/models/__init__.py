import unittest
from random import shuffle
from Vertex import Vertex
from Hexagon import Hexagon

"""
Constants for Board Building
"""
ROOT3 = round(3**.5, 3)
ROOT3_2 = round(ROOT3/2.0, 3)

HEXAGONS = [
    (0, ROOT3),
    (1.5, ROOT3_2),
    (1.5, -ROOT3_2),
    (0, -ROOT3),
    (-1.5, -ROOT3_2),
    (-1.5, ROOT3_2)
]

VERTICES = [
    (.5, ROOT3_2),
    (1, 0),
    (.5, -ROOT3_2),
    (-.5, -ROOT3_2),
    (-1, 0),
    (-.5, ROOT3_2)
]

# Relations for vertices across hexagons
RELATIONS = [
    (0,2,5,3),
    (0,4,1,3),
    (1,5,2,4),
    (3,5,2,0),
    (4,0,3,1),
    (4,2,5,1)
]

RESOURCES = {
    "wood": .2222,
    "sheep": .2222,
    "wheat": .2222,
    "brick": .166666,
    "stone": .166666
}

RESOURCE_ORDER = {"wood": 0, "wheat": 1, "sheep": 2, "brick": 3, "stone": 4, "desert": 5}


LOW_PROBABILITY = 0.05555555555
HIGH_PROBABILITY = 2 * LOW_PROBABILITY

"""
Board Builder Class
Generates a dictionary of Resources (Hexagons) and a dictionary of vertices
"""
class Board():
    def __init__(self, num_rings = 3, settlement_depth = 3):
        self.hexagons = dict()
        self.vertices = dict()

        self.settlement_depth = settlement_depth

        self.build(num_rings)

    """
    Building the Board
    """
    def build(self, num_rings):
        start = Hexagon(pos = (0,0))
        self.hexagons[(0,0)] = start
        self.buildRing(start, num_rings)

        self.num_hexagons = len(self.hexagons)
        self.num_vertices = len(self.vertices)

        self.buildVertexRelations()
        self.buildResources()

    def buildRing(self, r, depth):
        for i, vertex in enumerate(VERTICES):
            if r.vertices[i] == None:
                newPos = self.add(r.pos, vertex)
                newV = self.vertices.get(newPos, Vertex(pos = newPos, parity = (i % 2) == 0))
                r.vertices[i] = newV
                if newPos not in self.vertices:
                    self.vertices[newPos] = newV

        if depth == 0:
            return

        for i, hexagon in enumerate(HEXAGONS):
            newPos = self.add(r.pos, hexagon)
            newR = self.hexagons.get(newPos, Hexagon(pos = newPos))
            rel = RELATIONS[i]
            newR.vertices[rel[1]], newR.vertices[rel[3]] = r.vertices[rel[0]], r.vertices[rel[2]]
            self.buildRing(newR, depth - 1)
            if newPos not in self.hexagons:
                self.hexagons[newPos] = newR

    def buildVertexRelations(self):
        map(self.get_vertex_ref, self.vertices.values())
        map(self.get_settlement_set, self.vertices.values())

    def buildResources(self):
        materials, values = self.get_resources()

        for hexagon in self.hexagons.values():
            hexagon.resource = materials.pop()
            hexagon.value = 7 if hexagon.resource == "desert" else values.pop()

        for vertex in self.vertices.values():
            for hexagon in vertex.h_refs:
                if hexagon != None and hexagon.resource != "desert":
                    vertex.roll[hexagon.value] = vertex.roll.get(hexagon.value, []) + [hexagon.resource]
                    vertex.resources[RESOURCE_ORDER[hexagon.resource]] += abs(7 - hexagon.value)
                else:
                    vertex.resources[5] += 14

    """
    Helpers
    """
    def get_vertex_ref(self, vertex):
        for i,j in enumerate(xrange(0, 6, 2)):
            pos = self.add(vertex.pos, VERTICES[j]), self.add(vertex.pos, VERTICES[j + 1])

            if vertex.v_refs[i] == None:
                vertex.v_refs[i] = self.vertices.get(pos[1 - vertex.parity], None)

            if vertex.h_refs[i] == None:
                vertex.h_refs[i] = self.hexagons.get(pos[vertex.parity], None)

    def get_settlement_set(self, vertex):
        vertex.s_refs = dict()
        for x in xrange(1 - vertex.parity, 6, 2):
            v = self.vertices.get(self.add(vertex.pos, VERTICES[x]), None)
            if not v:
                continue
            self._settlement_recursion(x, 1 - vertex.parity,
                                         vertex.s_refs, [v],
                                         self.settlement_depth - 1)


    def _settlement_recursion(self, curIndex, curParity, settle, path, depth):
        _not = (curIndex + 3) % 6
        for x in xrange(1 - curParity, 6, 2):
            if x != _not:
                newPos = self.add(path[-1].pos, VERTICES[x])
                refV = self.vertices.get(newPos, None)
                if refV:
                    settle[refV] = path + [refV]
                    if depth > 1:
                        self._settlement_recursion(x, 1 - curParity, settle, path + [refV], depth - 1)



    def get_resources(self):
        # Get resources based on probability distribution specified in RESOURCES
        resources = [key for key, value in RESOURCES.items() for _ in xrange(int(value * self.num_hexagons))]

        # Count how many deserts necessary to fill in the hexagons
        diff =  self.num_hexagons - len(resources)
        if diff > 2: # JenkNote - we shouldn't have too many deserts. this limits it to 3 (diff is mod 5)
            resources.extend(["brick", "stone"])
            diff -= 2

        # Add the deserts needed
        resources.extend(["desert"] * diff)

        # Fill in resources based on probabilities of high / low resource probabilities. Default is 2 ring board distribution
        avail = (self.num_hexagons - diff)
        resourceValues = [3, 4, 5, 6, 8, 9, 10, 11] * int(avail * HIGH_PROBABILITY) + [2, 12] * int(avail * LOW_PROBABILITY)
        resourceValues.extend([2, 12, 3, 4, 5, 6, 8, 9, 10, 11][:self.num_hexagons - len(resourceValues) + 1])

        shuffle(resources)
        shuffle(resourceValues)

        return resources, resourceValues

    def get_vertex_from_position(self, pos):
        diffx = (pos[0] / .5)
        diffy = (pos[1] / ROOT3_2)

        lowerX = int(diffx)
        lowerY = int(diffy)

        x = lowerX if abs(diffx - lowerX) <= .5 else lowerX + 2 * (lowerX >= 0) - 1
        y = lowerY if abs(diffy - lowerY) <= .5 else lowerY + 2 * (lowerY >= 0) - 1
        # x = round(lowerX , 0)
        # y = round(lowerY , 0)

        return self.vertices.get((round(x * .5, 3), round(y * ROOT3_2, 3)))

    """
    Helpers for helping
    """
    def print_vertices(self):
        print sorted([vertex.pos for vertex in self.vertices.values()])

    def add(self, a, b):
        return round(a[0] + b[0], 3), round(a[1] + b[1], 3)

"""
Testing
"""
class TestGame(unittest.TestCase):
    def setUp(self):
        self.ring0 = Board(0)
        self.ring1 = Board(1)
        self.ring2 = Board(2)
        self.ring3 = Board(3)
        self.ring4 = Board(4)

        self.rings = [self.ring0, self.ring1, self.ring2, self.ring3, self.ring4]


    def test_building_function(self):
        """
        Test number of vertices and hexagons as a result of board building
        """
        self.assertEqual(len(self.ring0.hexagons), 1)
        self.assertEqual(len(self.ring1.hexagons), 7)
        self.assertEqual(len(self.ring2.hexagons), 19)
        self.assertEqual(len(self.ring3.hexagons), 37)
        self.assertEqual(len(self.ring4.hexagons), 61)

        self.assertEqual(len(self.ring0.vertices), 6)
        self.assertEqual(len(self.ring1.vertices), 24)
        self.assertEqual(len(self.ring2.vertices), 54)
        self.assertEqual(len(self.ring3.vertices), 96)
        self.assertEqual(len(self.ring4.vertices), 150)

    def test_vertex_refs(self):
        """
        Tests for all rings if there are the right number of vertices with only 2 references
        """
        self.assertEqual(len([1 for x in self.ring0.vertices.values() if len([z for z in x.v_refs if z]) == 2]), self.ring0.num_vertices)
        for i in xrange(len(self.rings) - 1):
            calculated = self.rings[i + 1].num_vertices - self.rings[i].num_vertices - self.rings[i + 1].num_hexagons + self.rings[i].num_hexagons
            only_two = [x for x in self.rings[i + 1].vertices.values() if len([z for z in x.v_refs if z]) == 2]
            self.assertEqual(len(only_two), calculated)

            # v_refs = [*x.v_refs for x in only_two]
            # first = v_refs.pop()
            # curr = first
            # while True:
            #     for v in curr.v_refs:
            #         if v in v_refs:
            #             curr = v
            #             v_refs.remove(v)


            #     if len(v_refs) == 0:
            #         break





    def test_vertex_ref_builder(self):
        """
        All cases
        Tests vertex references in vertices.
        List Indices always start from positive y-axis (north) and clockwise by center point
        """
        # Even Vertices
        testVertex = self.ring3.vertices[VERTICES[0]]

        self.assertEqual(testVertex.v_refs[0], self.ring3.vertices[2 * VERTICES[0][0], 2 * VERTICES[0][1]])
        self.assertEqual(testVertex.v_refs[1], self.ring3.vertices[VERTICES[1]])
        self.assertEqual(testVertex.v_refs[2], self.ring3.vertices[VERTICES[5]])

        # Odd Vertices
        testVertex = self.ring3.vertices[VERTICES[1]]

        self.assertEqual(testVertex.v_refs[0], self.ring3.vertices[2 * VERTICES[1][0], 2 * VERTICES[1][1]])
        self.assertEqual(testVertex.v_refs[1], self.ring3.vertices[VERTICES[2]])
        self.assertEqual(testVertex.v_refs[2], self.ring3.vertices[VERTICES[0]])

    def test_vertex_ref(self):
        """
        Single case
        Tests vertex references in vertices.
        List Indices always start from positive y-axis (north) and clockwise by center point
        """
        # For Even Vertices
        testVertex = self.ring3.vertices[VERTICES[0]]

        self.ring3.get_vertex_ref(testVertex)

        self.assertEqual(testVertex.v_refs[0], self.ring3.vertices[2 * VERTICES[0][0], 2 * VERTICES[0][1]])
        self.assertEqual(testVertex.v_refs[1], self.ring3.vertices[VERTICES[1]])
        self.assertEqual(testVertex.v_refs[2], self.ring3.vertices[VERTICES[5]])

        # For Odd Vertices
        testVertex = self.ring3.vertices[VERTICES[1]]

        self.ring3.get_vertex_ref(testVertex)

        self.assertEqual(testVertex.v_refs[0], self.ring3.vertices[2 * VERTICES[1][0], 2 * VERTICES[1][1]])
        self.assertEqual(testVertex.v_refs[1], self.ring3.vertices[VERTICES[2]])
        self.assertEqual(testVertex.v_refs[2], self.ring3.vertices[VERTICES[0]])

    def test_vertex_hexagon_ref_builder(self):
        """
        Tests hexagon references in vertices.
        List Indices always start from positive y-axis (north) and clockwise by center point
        """
        # For Even Vertices
        testVertex = self.ring3.vertices[VERTICES[0]]

        self.assertEqual(testVertex.h_refs[0], self.ring3.hexagons[VERTICES[0][0] + VERTICES[1][0], VERTICES[0][1] + VERTICES[1][1]])
        self.assertEqual(testVertex.h_refs[1], self.ring3.hexagons[(0,0)])
        self.assertEqual(testVertex.h_refs[2], self.ring3.hexagons[VERTICES[0][0] + VERTICES[5][0], VERTICES[0][1] + VERTICES[5][1]])

        # # For Odd Vertices
        testVertex = self.ring3.vertices[VERTICES[1]]

        self.assertEqual(testVertex.h_refs[0], self.ring3.hexagons[VERTICES[0][0] + VERTICES[1][0], VERTICES[0][1] + VERTICES[1][1]])
        self.assertEqual(testVertex.h_refs[1], self.ring3.hexagons[VERTICES[1][0] + VERTICES[2][0], VERTICES[1][1] + VERTICES[2][1]])
        self.assertEqual(testVertex.h_refs[2], self.ring3.hexagons[(0,0)])

    def test_resource_arrays(self):
        """
        The output of resource arrays - type and probabilities
        """
        resources, values = self.ring3.get_resources()

        # Make sure there enough resources for hexagons
        self.assertEqual(self.ring3.num_hexagons, len(resources))

        r_results = {}
        v_results = [0] * 11
        v_results[0] += 1
        v_results[-1] += 1

        # Calculate Freq
        for resource in resources:
            r_results[resource] = r_results.get(resource, 0) + 1
        for value in values:
            v_results[value - 2] += 1

        # Handle deserts
        deserts = r_results["desert"]
        del(r_results["desert"])
        del(v_results[5])

        # Make sure there are enough values for hexagons
        self.assertEqual(self.ring3.num_hexagons, len(values) + deserts)

    def test_hexagon_resources(self):
        """
        Make sure every hexagon has a resource and value
        """

        for hexagon in self.ring3.hexagons.values():
            self.assertTrue(hexagon.value is not None)
            self.assertTrue(hexagon.resource is not None)

    def test_vertex_from_clicked_position(self):
        testVertex = self.ring3.vertices.values()[0]
        x = testVertex.pos[0]
        y = testVertex.pos[1]

        vertex0 = self.ring3.get_vertex_from_position((x + .2, y - .25))
        vertex1 = self.ring3.get_vertex_from_position((x - .2, y - .25))
        vertex2 = self.ring3.get_vertex_from_position((x + .2, y + .25))
        vertex3 = self.ring3.get_vertex_from_position((x - .2, y + .25))

        self.assertEqual(testVertex, vertex0)
        self.assertEqual(testVertex, vertex1)
        self.assertEqual(testVertex, vertex2)
        self.assertEqual(testVertex, vertex3)

    def test_vertex_settlement_set(self):
        testVertex = self.ring3.vertices.values()[0]
        self.assertEqual(len(testVertex.s_refs), 9)

        # Check the paths to settlements are correct
        for v, path in testVertex.s_refs.items():
            self.assertEqual(v, path[-1])
            ref = testVertex
            for _v in path:
                self.assertTrue(_v in ref.v_refs)
                ref = _v


def TestGraphBoard(board):
    x = []
    y = []
    x1 = []
    y1 = []
    for key, item in board.hexagons.items():
        x.append(key[0])
        y.append(key[1])
        for vertex in item.vertices:
            x1.append(vertex.pos[0])
            y1.append(vertex.pos[1])

    plt.plot(x, y, 'ro')
    plt.plot(x1, y1, 'bo')
    plt.show()

if __name__ == "__main__":
    # Importing here to avoid importing when not testing
    # import matplotlib.pyplot as plt

    unittest.main()

    # board = Board(3)
    # TestGraphBoard(board)
