from ggsolver.models import *
from ggsolver.dtptb.reach import *
from parallel_dtptb.solver import *
from pprint import pprint
import numpy as np
import time
import logging

from parallel_dtptb.models import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


class JobstmannGame(MyGame):
    def __init__(self, final):
        super(JobstmannGame, self).__init__()
        self.param_final = final

    def states(self):
        #numpy array?
        return list(range(4))
        #return list(range(8))


    def actions(self):
        #numpy array?
        return [(0, 1), (1, 2), (2, 3)]
        # return [(0, 1), (0, 3), (1, 0), (1, 2), (1, 4), (2, 4), (2, 2), (3, 0), (3, 4), (3, 5), (4, 1), (4, 3), (5, 3),
        #         (5, 6), (6, 6), (6, 7), (7, 0), (7, 3)]

    def delta(self, state, act):
        """
        Return `None` to skip adding an edge.
        """
        #numba build here?
        if state == act[0]:
            return act[1]
        return None

    def final(self, state):
        #numba here
        return True if state in self.param_final else False

    def turn(self, state):
        #numba here?
        #this is player 1 vs player 2 declaration
        if state in [2]:
        #if state in [0, 4, 6]:
            return 1
        else:
            return 2


if __name__ == '__main__':
    tic = time.perf_counter()
    game = JobstmannGame(final={3})
    #game = JobstmannGame(final={3, 5, 6})
    states = game.states()
    actions = game.actions()

    graph = game.matrixBuilder(game,states,actions)
    #-----------------------
    #win = SWinReach(graph)
    #SWinReach.solve()
    final = SWinReacher.solver(game,game=game,G=graph,T=graph.T,final=game.param_final,i=1)
    print('winning region: ',final)
    toc = time.perf_counter()
    print('\n', f"Completed in {toc - tic} seconds")

    # game2 = JobstmannGame(final={1, 2, 3, 6, 7})
    # graph2 = game2.graphify()
    # win2 = SWinSafe(graph2, player=2)
    # win2.solve()
    # print(f"{win2.win_region(1)=}")
    # print(f"{win2.win_region(2)=}")

    # # Print the generated graph
    # print(f"Printing {graph}")
    # print(f"Nodes: {list(graph.nodes())}")
    # pprint(f"Edges: {list(graph.edges())}")
    #
    # print("----- Node properties")
    # pprint(graph._node_properties)
    # print("----- Edge properties")
    # pprint(graph._edge_properties)
    # print("----- Graph properties")
    # pprint(graph._graph_properties)

