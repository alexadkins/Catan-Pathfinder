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
        self.start = None
        self.end = None

        # Whether or not to recalculate the path
        self.changed = False
        self.drawn = {"start": None, "end": None}

    def handleClick(self):
        clicked = self.display.input()
        if clicked == None:
            return
        # Check if clicked buttons
        if self.clickedInBounds(clicked, self.buttons[0]):
            self.clearBoard()

            # Start Button
            self.action = "start"
            if self.drawn["start"] != None:
                self.clear("start")
        elif self.clickedInBounds(clicked, self.buttons[1]):
            # End Button
            self.action = "end"
            if self.drawn["end"] != None:
                self.clear("end")
        elif self.clickedInBounds(clicked, self.buttons[2]):
            # Verification Button
            if self.start and self.end:
                self.verifyPath()
        else: # Otherwise, selecting a node
            if self.action == "start":
                self.start = self.board.get_vertex_from_position(self.display._convertToNormal((clicked.getX(), clicked.getY())))
                if self.start != None:
                    self.drawn["start"] = [self.display._drawCircle(self.start.pos, 20, "red")]
                    self.changed = True
                    self.action = None

            if self.action == "end":
                self.end = self.board.get_vertex_from_position(self.display._convertToNormal((clicked.getX(), clicked.getY())))
                if self.end != None:
                    self.drawn["end"] = [self.display._drawCircle(self.end.pos, 20, "blue")]
                    self.changed = True
                    self.action = None

        # Check to see if we need to redraw the path
        if self.changed and self.start and self.end:
            path, s_path = self.algorithm.find_path(self.board.vertices.values(), self.start, self.end)
            
            self.drawn["chosen settlements"] = [self.display._drawCircle(v.pos, 20, "red") for v in s_path]
            self.drawn["chosen path"] = self.display.drawPath([v.pos for v in path])
            
            self.num_settlements = len(s_path)
            self.changed = False

        self.display.update()

    def verifyPath(self):
        self.clear("chosen path")
        self.clear("chosen settlements")

        paths = self.verification.find_all_paths(self.board.vertices.values(), self.start, self.end, self.num_settlements - 1)
        # Draw Verification Paths
        self.drawn["verification paths"] = []
        for path in paths[0]:
            self.drawn["verification paths"].extend(self.display.drawPath([v.pos for v in path], color = "gray") )
        self.drawn["verification settlements"] = [self.display._drawCircle(v.pos, 20, "gray") for path in paths[1] for v in path]
        
        results = self.simulatePaths(paths[1])
        best = results.index(max(results))

        self.drawn["best paths"] = self.display.drawPath([v.pos for v in paths[0][best]], color = "green")
        self.drawn["best settlements"] = [self.display._drawCircle(v.pos, 25, "green") for v in paths[1][best]]

        self.redraw("chosen path")
        self.redraw("chosen settlements")

    def simulatePaths(self, paths):
        resources = [[0,0,0,0,0] for _ in xrange(len(paths))]
        for _ in xrange(10000):
            roll = randint(1, 6) + randint(1, 6)
            if roll == 7:   continue
            for i, s_res in [(i, v.roll.get(roll, [])) for i, path in enumerate(paths) for v in path]:
                for res in s_res:
                    resources[i][RESOURCE_ORDER[res]] += 1
            
        return [([x * x for x in res]) for res in resources]
    
    def drawButtons(self, *args):
        self.buttons = []
        for arg in args:
            self.buttons.append(arg)
            self.display.drawButton(arg[-1], arg[0:2], arg[2:4], scale = True)

    def clearBoard(self):
        self.start = None
        self.end = None
        self.clear("verification paths")
        self.clear("verification settlements")
        self.clear("chosen path")
        self.clear("chosen settlements")
        self.clear("start")
        self.clear("end")
        self.clear("best paths")
        self.clear("best settlements")
        self.display.update()

    def clear(self, thing):
        if self.drawn.get(thing, None):
            for x in self.drawn[thing]:
                if x: x.undraw()

    def redraw(self, thing):
        if self.drawn.get(thing, None):
            for x in self.drawn[thing]:
                if x: x.draw(self.display.window)

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
