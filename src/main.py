from models import Board, Hexagon, Vertex, RESOURCE_ORDER
from views import Display
from evaluators import EvaluatorA as EV
from algorithms import dijkstra
from random import randint, choice
from copy import deepcopy
import sys


class Controller:
    def __init__(self, display, board, algorithm, verification, MAGIC = 1):
        self.display = display
        self.board = board
        self.algorithm = algorithm()
        self.verification = verification()

        self.MAGIC = MAGIC
        self.initMembers()
        
        if display:
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
                self.drawVerification()
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
            path, s_path = self.findBestPath()
            self.drawn["chosen settlements"] = [self.display._drawCircle(v.pos, 20, "red") for v in s_path]
            self.drawn["chosen path"] = self.display.drawPath([v.pos for v in path])
        
            self.changed = False

        self.display.update()

    def findBestPath(self):
        path, s_path = self.algorithm.find_path(self.board.vertices.values(), self.start, self.end)
        self.chosenPath = s_path
        self.num_settlements = len(s_path)
        return path, s_path

    def drawVerification(self):
        self.clear("chosen path")
        self.clear("chosen settlements")

        best, paths = self.simulatePaths()
        # Draw Verification Paths
        self.drawn["verification paths"] = []
        for path in paths[0]:
            self.drawn["verification paths"].extend(self.display.drawPath([v.pos for v in path], color = "gray") )
        self.drawn["verification settlements"] = [self.display._drawCircle(v.pos, 20, "gray") for path in paths[1] for v in path]
        
        self.drawn["best paths"] = self.display.drawPath([v.pos for v in paths[0][best]], color = "green")
        self.drawn["best settlements"] = [self.display._drawCircle(v.pos, 25, "green") for v in paths[1][best]]

        self.redraw("chosen path")
        self.redraw("chosen settlements")

    def simulatePaths(self):
        draw, paths = self.verification.find_all_paths(self.board.vertices.values(), self.start, self.end, self.num_settlements - 1)
        chosen = paths.index(self.chosenPath)
        resources = [[0,0,0,0,0] for _ in xrange(len(paths))]
        for _ in xrange(10000):
            roll = randint(1, 6) + randint(1, 6)
            if roll == 7:   continue
            for i, s_res in [(i, v.roll.get(roll, [])) for i, path in enumerate(paths) for v in path]:
                for res in s_res:
                    resources[i][RESOURCE_ORDER[res]] += 1
        
        # means = [float(sum(res))/len(res) for res in resources]
        # variance = [sum([(means[i] - x) ** 2 for x in res])**.5 for i,res in enumerate(resources)]

        # results = [sum(res) + variance[i] * self.MAGIC for i, res in enumerate(resources)]
        results = [sum([x*x for x in res]) * self.MAGIC * sum([1 for x in res if x != 0])/5 for res in resources]

        # results = [sum(res)/(variance[i]**.5) for i,res in enumerate(resources)]
        # medians = [sorted(res)[2] for res in resources]
        # results = [sum(res)/(sum(res)/abs(float(len(res)) - medians[i])) for i,res in enumerate(resources)]
        best = results.index(max(results))
        
        return best, (draw, paths)

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
    # EXIT_BUTTON = (20, 250, 120, 310, "Exit")

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

    controller.drawButtons(START_BUTTON, END_BUTTON, VERIFY_BUTTON)#, EXIT_BUTTON)

    while True:
        # try:
        controller.handleClick()
        display.update()
        # except: 
        #     pass

    display.close()

def AutomatedLoop():
    board = Board(2,3)
    EV().evaluateBoard(board)

    controller = Controller(None,
                            board, 
                            dijkstra.DijkstraResourceSettlementAlgorithm, 
                            dijkstra.DijkstraPathAlgorithm)

    adding = True
    prev = 1.0
    controller.MAGIC = .375
    coeff_dict = {}

    while prev > .05:
        results = []
        
        for _ in xrange(20):
            controller.start = choice(board.vertices.values())
            controller.end = choice(board.vertices.values())
            try:
                controller.findBestPath()

                best, (_, paths) = controller.simulatePaths()

                evaled = set(paths[best])
                chosen = set(controller.chosenPath)

                results.append(len(evaled.symmetric_difference(chosen))/float(len(evaled)))
            except:
                print controller.start, controller.end

        new = sum(results)/float(len(results))
        print "COEFF:", controller.MAGIC, " error:", new
        if new > prev + .05:
            adding ^= True
        
        controller.MAGIC *= 1 + (adding * 2 - 1) * .5
        if controller.MAGIC in coeff_dict:
            print "Looped back around"
            # break
        else:
            coeff_dict[controller.MAGIC] = new

        prev = new


if __name__ == "__main__":
    # DrawBoardTest()

    GameLoop()

    # AutomatedLoop()
