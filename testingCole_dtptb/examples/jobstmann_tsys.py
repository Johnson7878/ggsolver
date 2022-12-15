"""
We construct the Jobstmann example using a TSys and DFA.
The graph is defined as a transition system.
The objective, which is to eventually reach 3 or 4, is encoded as DFA.

Rmk. In general, it is recommended to define Automaton directly as a graph.
    Spot translate will yield a graph.
    >>> from ggsolver.spotaut import translate
    >>> aut = translate("Fa")
"""

from ggsolver import models
from pprint import pprint


class JobstmannTSys(models.TSys):
    def states(self):
        return list(range(8))

    def actions(self):
        return [(0, 1), (0, 3), (1, 0), (1, 2), (1, 4), (2, 4), (2, 2), (3, 0), (3, 4), (3, 5), (4, 3), (5, 3), (5, 6),
                (6, 6), (6, 7), (7, 0), (7, 3)]

    def delta(self, state, act):
        """
        Return `None` to skip adding an edge.
        """
        if state == act[0]:
            return act[1]
        return None

    def turn(self, state):
        if state in [0, 4, 6]:
            return 1
        else:
            return 2


class SpecDFA(models.Automaton):
    def __init__(self):
        super(SpecDFA, self).__init__()
        self._init_state = 0

    def states(self):
        return [0, 1]

    def atoms(self):
        return [f"p{i}" for i in range(8)]

    def delta(self, state, inp):
        """
        State 0 is initial state.
        """
        if state == 0 and inp in ["p3", "p4"]:
            return 1
        elif state == 1:
            return 1
        else:
            return 0

    def final(self, state):
        return state == 1

    def acc_cond(self):
        return models.Automaton.ACC_REACH


if __name__ == '__main__':
    tsys = JobstmannTSys()
    spec = SpecDFA()

    tsys_graph = tsys.graphify()
    dfa_graph = spec.graphify()

    print("----- Node properties")
    pprint(dfa_graph._node_properties)
    print("----- Edge properties")
    pprint(dfa_graph._edge_properties)
    print("----- Graph properties")
    pprint(dfa_graph._graph_properties)
