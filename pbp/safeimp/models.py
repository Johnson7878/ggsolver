import logging
from ggsolver.mdp.models import QualitativeMDP
from ggsolver.mdp.reachability import ASWinReach
from tqdm import tqdm
logging.basicConfig(level=logging.INFO)


class PrefModel:
    def __init__(self, outcomes, pref):
        """
        Enumerated outcomes. {1: [s0, s1, ...], 2: [s1, s2, ...], ... }.
        Pref: (1, 2), (2, 3) over indices of sets.
        """
        self._outcomes = outcomes
        self._pref = pref

    def __getitem__(self, idx):
        return self._outcomes[idx]

    def outcomes(self):
        return list(self._outcomes.values())

    def outcomes_dict(self):
        return self._outcomes

    def is_strictly_preferred(self, more_idx, less_idx):
        return (more_idx, less_idx) in self._pref and (less_idx, more_idx) not in self._pref

    def is_indifferent(self, more_idx, less_idx):
        return (more_idx, less_idx) in self._pref and (less_idx, more_idx) in self._pref

    def is_incomparable(self, more_idx, less_idx):
        return (more_idx, less_idx) not in self._pref and (less_idx, more_idx) not in self._pref


class ImprovementMDP(QualitativeMDP):
    def __init__(self, mdp, pref_model: PrefModel):
        super(ImprovementMDP, self).__init__()
        self._mdp = mdp
        self._pref = pref_model
        self._outcomes = dict()
        self._winning_regions = dict()
        self._mp_outcomes = self._compute_mp_outcomes()

    def states(self):
        return [(st, 0) for st in self._mdp.states()] + [(st, 1) for st in self._mdp.states()]

    def actions(self):
        return self._mdp.actions()

    def delta(self, state, act):
        # Decouple state
        si, mi = state

        # Initialize output
        next_states = set()

        # Condition 1
        next_mdp_states = self._mdp.delta(si, act)
        for n_state in next_mdp_states:
            # Condition 2 (Safety)
            if any(self._pref.is_strictly_preferred(r1, r2)
                   for r1 in self._mp_outcomes[si]
                   for r2 in self._mp_outcomes[n_state]):
                continue

            # Condition 3
            if any(self._pref.is_strictly_preferred(r2, r1)
                   for r1 in self._mp_outcomes[si]
                   for r2 in self._mp_outcomes[n_state]) or \
                    (len(self._mp_outcomes[si]) == 0 and len(self._mp_outcomes[n_state]) > 0):
                next_states.add((n_state, 1))

            # Condition 4
            else:
                next_states.add((n_state, 0))

        return next_states

    def init_state(self):
        return self._mdp.init_state(), 0

    def final(self, state):
        return [(st, 1) for st in self._mdp.states()]

    def _compute_mp_outcomes(self):
        # Initialize output dictionary
        mp_outcomes = {st: set() for st in self._mdp.states()}

        # Compute winning region for all outcomes.
        winning_regions = self._compute_winning_regions()
        self._winning_regions = winning_regions

        # For each state, v, identify outcomes(v).
        outcomes = {st: set() for st in self._mdp.states()}
        for idx, win in winning_regions.items():
            for node in win.win1():
                outcomes[win.graph()["state"][node]].add(idx)
        self._outcomes = outcomes
        # print(outcomes)

        # Compute MP(v).
        for st, out_st in outcomes.items():
            mp_outcomes[st] = {f for f in out_st if not any(self._pref.is_strictly_preferred(g, f) for g in out_st)}

        return mp_outcomes

    def _compute_winning_regions(self):
        print(f"Computing winning regions ... ")
        graph = self._mdp.graphify()
        # PATCH (in general final states should be determined in model)
        win = {idx: ASWinReach(graph, final={node for node in graph.nodes()
                                             if graph["state"][node] in final and graph["state"][node][3][idx] == 1})
               for idx, final in self._pref.outcomes_dict().items()}

        pbar = tqdm(win)
        for idx in pbar:
            pbar.set_description(f"Solving for winning regions {idx}/{len(win)}")
            win[idx].solve()
        return win

