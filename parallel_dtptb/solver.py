import logging
from ggsolver.graph import NodePropertyMap
from ggsolver.util import ColoredMsg
from ggsolver.models import Solver
from functools import reduce
from tqdm import tqdm
import numpy as np
from numba import njit
logger = logging.getLogger(__name__)


class SWinReacher(Solver):
    """
    Computes sure winning region for player 1 or 2 to reach a set of final states in a deterministic
    two-player turn-based game.

    Implements Zielonka's recursive algorithm.

    Cole's scrappy implementation of a matrix-game construction with the ZR algo. In this seciton,
    I build out the ZR algo with matricies and lists, while explaining the usage (or lack of) numba
    in this section.
    """


    #can't use numba here as a result of the game objects/calls to game class that
    #conflict with numba (NOT RAW DATA TYPE FOR COMPILATION)
    def solver(self, game,G, T,final,i):
        """ This is where the ZR algo goes"""

        #@njit
        #...Interesting that this made the performance worse, must be used with append
        #helper func to identify adjacent nodes
        def adj(matrix, row):
            temp = []
            for col in range(np.shape(matrix)[1]):
                if matrix[row, col] == 1:
                    #temp.append(col)
                    temp += [col]
            return temp

        #------------PARAMETERS------------
        #self,game = game objects (self wasn't allowing access to previous game)
        #G = matrix_A from models (2D graph matrix)
        # T = G.T
        # Removed = removed set with nodes filtered out (initialized to empty set)
        #final = list of final states------converted to A later on
        # i = attracting player (potentially turn??)

        #in the future, create function that identifies removed nodes in game
        #Removed = set()
        Removed = []
        for iter in range(np.shape(G)[0]):
            if G[iter,iter] == 1 and game.turn(iter) == 2:
                for iter1 in range(np.shape(G)[0]):
                    if G[iter1,iter] == 1 and game.turn(iter)==2:
                        Removed += [iter1]

        #Removed = {1,2}
        A = list(final)


        #initialize tmpMap with list representation of node connections
        #0 = final state
        #-1 = node connecting to path of final state
        tmpMap = np.zeros((np.shape(G)[0],))
        for x in range(np.shape(G)[0]):
            if x in A:
                tmpMap[x] = 0
            else:
                tmpMap[x] = -1

        #bulk of ZR algo, here we expand our final states and iteratively solve our attractor (or win region)
        index = 0
        while index < len(A):
            for v0 in adj(T, A[index]):
                if v0 not in Removed:
                    if tmpMap[v0] == -1:
                       if game.turn(v0) == i:
                           #get player 1
                            A.append(v0)
                            tmpMap[v0] = 0

                       else:
                           #get player 2
                           adj_counter = -1
                           for x in adj(G,v0):
                               if x not in Removed:
                                   adj_counter += 1
                           tmpMap[v0] = adj_counter
                           if adj_counter == 0:
                               A.append(v0)
                    if (game.turn(v0)== 2) and (tmpMap[v0] > 0):
                        tmpMap[v0] -= 1
                        if tmpMap[v0] == 0:
                            A.append(v0)
            index += 1
        return A
# class SWinSafe(SWinReach):
#     """
#     Computes sure winning region for player 1 or player 2 to remain within a set of final states in a deterministic
#     two-player turn-based game.
#
#     Solves the dual reachability game to determine the winning nodes and edges in the safety game.
#
#     :param graph: (Graph or SubGraph instance) A graph or subgraph of a deterministic two-player turn-based game.
#     :param final: (Iterable) The set of final states. By default, the final states are determined using
#         node property "final" of the graph.
#     :param player: (int) The player who has the reachability objective.
#         Value should be 1 for player 1, and 2 for player 2.
#     """
#     def __init__(self, graph, final=None, player=1, **kwargs):
#         super(SWinSafe, self).__init__(graph, **kwargs)
#         self._final = final if final is not None else self.get_final_states()
#
#     def get_final_states(self):
#         """ Determines the final states using "final" property of the input graph. """
#         return {uid for uid in self.graph().nodes() if self.graph()["final"][uid]}
#
#     def solve(self):
#         """ Solves the dual reachability game to solve the safety game. """
#
#         # Reset solver
#         self.reset()
#
#         # Formulate and solve dual reachability game
#         final = set(self.graph().nodes()) - self._final
#         dual_player = 1 if self._player == 1 else 2
#         dual_solver = SWinReach(self.graph(), final, dual_player)
#         dual_solver.solve()
#
#         # Process the output back to safety game
#         self._solution = dual_solver.solution()
#         self._node_winner = self._solution["node_winner"]
#         self._edge_winner = self._solution["edge_winner"]
#
#         # Mark the game to be solved
#         self._is_solved = True
#
#
# ASWinReach = SWinReach
# ASWinSafe = SWinSafe
