"""
Solver for SPI and SASI strategies.
"""
from ggsolver.mdp.reachability import ASWinReach, PWinReach
from ggsolver.models import Solver
from pprint import pprint


class SASIReach(Solver):
    """
    Alg. 1 from ACC 2023 paper.
    """
    def __init__(self, graph, final, **kwargs):
        """
        Instantiates a sure winning reachability game solver.

        :param graph: (Graph instance)
        :param final: (iterable) A list/tuple/set of final nodes in graph.
        :param kwargs: SureWinReach accepts no keyword arguments.
        """
        super(SASIReach, self).__init__(graph, **kwargs)
        self._final = final
        self._strategy_graph = None
        self._state2id = {self._graph["state"][uid]: uid for uid in self._graph.nodes()}

    def solve(self):
        print(f"Initialize iter_count=0")
        iter_count = 0

        set_r = set(self._final)
        # print(f"set_r={[self._graph['state'][node] for node in set_r]}")

        set_cal_w = []
        # print(f"set_cal_w={set_cal_w}")

        while len(set_r) > 0:
            print(f"--------- {iter_count + 1}-th iteration -----------")
            set_w = ASWinReach(self._graph, final=set_r)
            set_w.solve()
            set_w = set_w.win1()
            # print(f"set_r={[self._graph['state'][node] for node in set_r]}")
            # print(f"set_w={[self._graph['state'][node] for node in set_w]}")

            set_r = set()
            for uid in set_w:
                si, mi = self._graph["state"][uid]
                if mi == 0:
                    set_r.add((si, 1))

            set_r = {node for node in self._graph.nodes() if self._graph["state"][node] in set_r}

            if iter_count == 0:
                set_cal_w.insert(0, set(self._graph.nodes()) - set_w)

            set_cal_w.append(set_w)
            # print(f"set_cal_w={[{self._graph['state'][node] for node in level} for level in set_cal_w]}")

            iter_count += 1

        self._win1 = set_cal_w
        print("Num levels: ", len(self._win1))
        # print("------ win ---------")
        # iter_count = 0
        # for level in set_cal_w:
        #     # print(iter_count, [self._graph['state'][node] for node in level])
        #     iter_count += 1
        # print(f"win1={[[self._graph['state'][node] for node in level] for level in self._win1]}")

    def rank(self, state):
        uid = self._state2id[state]
        for rank in range(len(self._win1) - 1, -1, -1):
            if uid in self._win1[rank]:
                return rank


class SPIReach(Solver):
    """
    Alg. 1 from ACC 2023 paper.
    """
    def __init__(self, graph, final, **kwargs):
        """
        Instantiates a sure winning reachability game solver.

        :param graph: (Graph instance)
        :param final: (iterable) A list/tuple/set of final nodes in graph.
        :param kwargs: SureWinReach accepts no keyword arguments.
        """
        super(SPIReach, self).__init__(graph, **kwargs)
        self._final = final
        self._strategy_graph = None
        self._state2id = {self._graph["state"][uid]: uid for uid in self._graph.nodes()}

    def solve(self):
        print(f"Initialize iter_count=0")
        iter_count = 0

        set_r = set(self._final)
        # print(f"set_r={[self._graph['state'][node] for node in set_r]}")

        set_cal_w = []
        # print(f"set_cal_w={set_cal_w}")

        while len(set_r) > 0:
            print(f"--------- {iter_count + 1}-th iteration -----------")
            set_w = PWinReach(self._graph, final=set_r)
            set_w.solve()
            set_w = set_w.win1()
            # print(f"set_r={[self._graph['state'][node] for node in set_r]}")
            # print(f"set_w={[self._graph['state'][node] for node in set_w]}")

            set_r = set()
            for uid in set_w:
                si, mi = self._graph["state"][uid]
                if mi == 0:
                    set_r.add((si, 1))

            set_r = {node for node in self._graph.nodes() if self._graph["state"][node] in set_r}

            if iter_count == 0:
                set_cal_w.insert(0, set(self._graph.nodes()) - set_w)

            set_cal_w.append(set_w)
            # print(f"set_cal_w={[{self._graph['state'][node] for node in level} for level in set_cal_w]}")

            iter_count += 1

        self._win1 = set_cal_w
        print("Num levels: ", len(self._win1))
        # print("------ win ---------")
        # iter_count = 0
        # for level in set_cal_w:
        #     # print(iter_count, [self._graph['state'][node] for node in level])
        #     iter_count += 1
        # print(f"win1={[[self._graph['state'][node] for node in level] for level in self._win1]}")

    def rank(self, state):
        uid = self._state2id[state]
        for rank in range(len(self._win1) - 1, -1, -1):
            if uid in self._win1[rank]:
                return rank