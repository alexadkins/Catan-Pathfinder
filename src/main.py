from models import Board, Hexagon, Vertex, RESOURCE_ORDER
from views import Display
from evaluators import EvaluatorA as EV
from algorithms import dijkstra
from random import randint
from copy import deepcopy
import sys


class Controller:
    def __init__(self, display, board, algorithm, verification):
        self.display = display
        self.board = board
        self.algorithm = algorithm()
        self.verification = verification()

        self.initMembers()

        self.display.drawBoard(self.board)

    def initMembers(self):
        # Click action
        self.action = None

        # Start / End vertices / circles
        self.start_circle = None
        self.end_circle = None
        self.start = None
        self.end = None

        # Whether or not to recalculate the path
        self.changed = False
        self.pathLines = []
        self.settleCircles = []
        self.verifyPaths = []

    def drawButtons(self, *args):
        self.buttons = []
        for arg in args:
            self.buttons.append(arg)
            self.display.drawButton(arg[-1], arg[0:2], arg[2:4], scale = True)

    def handleClick(self):
        clicked = self.display.input()
        if clicked == None:
            return
        # Check if clicked buttons
        if self.clickedInBounds(clicked, self.buttons[0]):
            self.action = "start"
            if self.start_circle != None:
                self.start_circle.undraw()
        elif self.clickedInBounds(clicked, self.buttons[1]):
            self.action = "end"
            if self.end_circle != None:
                self.end_circle.undraw()
        elif self.clickedInBounds(clicked, self.buttons[2]):
            if self.start and self.end:
                self.verifyPath()
        else: # Otherwise, selecting a node
            if self.action == "start":
                self.clearPath()
                self.start = self.board.get_vertex_from_position(self.display._convertToNormal((clicked.getX(), clicked.getY())))
                if self.start != None:
                    self.start_circle = self.display._drawCircle(self.start.pos, 20, "red")
                    if len(sys.argv) > 1:
                        for vertex in self.start.s_refs:
                            self.display._drawCircle(vertex.pos, 20, "white")
                            self.display.drawPath(self.start.pos, *[v.pos for v in self.start.s_refs[vertex]])
                    self.changed = True
                    self.action = None

            if self.action == "end":
                self.end = self.board.get_vertex_from_position(self.display._convertToNormal((clicked.getX(), clicked.getY())))
                if self.end != None:
                    self.end_circle = self.display._drawCircle(self.end.pos, 20, "blue")
                    self.changed = True
                    self.action = None

        # Check to see if we need to redraw the path
        if self.changed and self.start and self.end:
            path, s_path = self.algorithm.find_path(self.board.vertices.values(), self.start, self.end)
            self.settleCircles = [self.display._drawCircle(v.pos, 20, "red") for v in s_path]
            self.pathLines = self.display.drawPath([v.pos for v in path])
            self.num_settlements = len(s_path)
            self.display.update()

            changed = False

    def verifyPath(self):
        for edge in self.pathLines + self.settleCircles:
            edge.undraw()

        paths = self.verification.find_all_paths(self.board.vertices.values(), self.start, self.end, self.num_settlements - 1)
        self.verifyPaths = [(self.display.drawPath([v.pos for v in path], color = "gray"), [self.display._drawCircle(v.pos, 20, "gray") for v in s_path]) for path, s_path in paths]
        results = self.simulatePaths([y for x,y in paths])
        best = results.index(max(results))
        self.bestPath = self.display.drawPath([v.pos for v in paths[best][0]], color = "green")
        self.bestSettle = [self.display._drawCircle(v.pos, 25, "green") for v in paths[best][1]]

        for line in self.pathLines:
            line.draw(self.display.window)
        for circle in self.settleCircles:
            circle.draw(self.display.window)

    def simulatePaths(self, paths):
        turns = [0] * len(paths)
        resources = [[0,0,0,0,0] for _ in xrange(len(paths))]
        for _ in xrange(10000):
            roll = randint(1, 6) + randint(1, 6)
            for i, path in enumerate(paths):
                for v in path:
                    if roll != 7 and roll in v.roll:
                        s_res = v.roll[roll] 
                        for res in s_res:
                            resources[i][RESOURCE_ORDER[res]] += 1
        return [([x * x for x in res]) for res in resources]


    def clearPath(self):
        self.start = None
        self.end = None
        if self.end_circle:
            self.end_circle.undraw()
        if self.start_circle:
            self.start_circle.undraw()
        for edge in self.pathLines + self.settleCircles:
            edge.undraw()

    def clickedInBounds(self, point, bounds):
        return bounds[0] < point.getX() < bounds[2] and bounds[1] < point.getY() < bounds[3]


def GameLoop():
    # Buttons
    START_BUTTON = (20, 25, 120, 70, "Starting Node")
    END_BUTTON = (20, 100, 120, 150, "Ending Node")
    VERIFY_BUTTON = (20, 175, 120, 230, "Verify Paths")

    # Create the board
    board = Board(2, 3)
    EV().evaluateBoard(board)

    # Show the initial board
    display = Display()

    # Controller Initialization
    controller = Controller(display,\
                            board, 
                            dijkstra.DijkstraResourceSettlementAlgorithm, 
                            dijkstra.DijkstraPathAlgorithm)

    controller.drawButtons(START_BUTTON, END_BUTTON, VERIFY_BUTTON)

    while True:
        controller.handleClick()
        display.update()

    display.close()

if __name__ == "__main__":
    # DrawBoardTest()

    GameLoop()
