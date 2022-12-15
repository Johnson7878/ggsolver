import itertools

from ggsolver.models import Game
#from ggsolver.automata import DFA
from numba import njit
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

class DTPTBGame(Game):
    """
    delta(s, a) -> s
    """
    def __init__(self, **kwargs):
        """
        kwargs:
            * states: List of states
            * actions: List of actions
            * trans_dict: Dictionary of {state: {act: state}}
            * atoms: List of atoms
            * label: Dictionary of {state: List[atoms]}
            * final: List of states
            * turn: Dictionary of {state: turn}
        """
        super(DTPTBGame, self).__init__(
            **kwargs,
            is_deterministic=True,
            is_probabilistic=False,
            is_turn_based=True
        )


# class ProductWithDFA(DTPTBGame):
#     """
#     For the product to be defined, Game must implement `atoms` and `label` functions.
#     """
#     def __init__(self, game: DTPTBGame, aut: DFA):
#         super(ProductWithDFA, self).__init__()
#         self._game = game
#         self._aut = aut
#
#     def states(self):
#         #np here?
#         return list(itertools.product(self._game.states(), self._aut.states()))
#
#     def actions(self):
#         return self._game.actions()
#
#     def delta(self, state, act):
#         s, q = state
#         t = self._game.delta(s, act)
#         p = self._aut.delta(q, self._game.label(t))
#         return t, p
#
#     def init_state(self):
#         if self._game.init_state() is not None:
#             s0 = self.init_state()
#             q0 = self._aut.init_state()
#             return s0, self._aut.delta(q0, self._game.label(s0))
#
#     def final(self, state):
#         return 0 in self._aut.final(state[1])
#
#     def turn(self, state):
#         return self._game.turn(state[0])


class MyGame(Game):


    def matrixBuilder(self, game,states, actions):

        #grab states and actions

        #states = getattr(self, "states")
        #states = self.states
        n = len(states)
        states = dict(zip(states, range(len(states))))
        #actions = getattr(self, "actions")
        #actions = self.actions
        m = len(actions)
        actions = dict(zip(actions, range(len(actions))))

        matrix_M = np.zeros((n, n, m))
        matrix_A = np.zeros((n,n))
        for s in states:
            for a in actions:
                ds = game.delta(s,a)
                if(ds == None):
                    continue
                i = states[s]
                j = states[ds]
                k = actions[a]
                matrix_M[i,j,k]=1
                matrix_A[i,j]=1

        return matrix_A
