from ggsolver.logic.prefltl import *
from ggsolver.mdp.models import QualitativeMDP


def assign_rank(dfpa: DFPA):
    # FIXME: Creating a subgraph here will add hidden_nodes, hidden_edges property to preference graph.
    #   These properties have no use later on.
    #   (Pending feature request) SubGraph has options to not share hidden_nodes, hidden_edges properties with base graph.
    #   After the feature is available, update this code.
    pg = SubGraph(dfpa.pref_graph())
    np_rank = NodePropertyMap(graph=pg, default=None)

    nodes = set(pg.nodes())
    curr_rank = 0
    while len(nodes) > 0:
        nodes_at_curr_rank = {n for n in nodes if len(pg.successors(n)) == 0}
        for n in nodes_at_curr_rank:
            np_rank[n] = curr_rank
            pg.hide_node(n)
        curr_rank += 1
        nodes = nodes - nodes_at_curr_rank

    dfpa.pref_graph()["rank"] = np_rank
    print(pg["rank"])


class ProductPrefMDP(QualitativeMDP):
    def __init__(self, mdp:QualitativeMDP, dfpa:DFPA):
        super(QualitativeMDP, self).__init__()
        self._mdp = mdp
        self._dfpa = dfpa
        self._pref_graph = self._construct_pref_graph()

    def states(self):
        return list(itertools.product(self._mdp.states(), self._dfpa.states()))

    def actions(self):
        return self._mdp.actions()

    def delta(self, state, act):
        pass

    def pref_graph(self, force_reconstruct=False):
        if force_reconstruct:
            self._construct_pref_graph()
        return self._pref_graph

    def _construct_pref_graph(self):
        graph = Graph()
        pg = self._dfpa.pref_graph()

        # Nodes of preference graph have same identifier (MP-outcomes) as that in DFPA's nodes.
        node_ids = graph.add_nodes(len(pg["state"].keys()))

        np_state = graph["state"] = NodePropertyMap(graph)
        np_state.update({id_: pg["state"][id_] for id_ in node_ids})

        # Add states in product MDP to each node partition
        np_partition = graph["partition"] = NodePropertyMap(graph)
        for id_ in node_ids:
            dfpa_states = pg["partition"][id_]
            np_partition[id_] = {(mdp_st, dfpa_st) for mdp_st in self._mdp.states() for dfpa_st in dfpa_states}

        return graph


if __name__ == '__main__':
    mdp_ = QualitativeMDP(
        states=[f"s{i}" for i in range(8)] + ["sink"],
        actions=['alpha', 'beta'],
        trans_dict={
            "s0": {'alpha': ["s1"], 'beta': ["s2", "s4"]},
            "s1": {'alpha': ["s1", "s2", "s3"], 'beta': ["sink"]},
            "s2": {'alpha': ["s2"], 'beta': ["sink"]},
            "s3": {'alpha': ["s3"], 'beta': ["sink"]},
            "s4": {'alpha': ["s5", "s6"], 'beta': ["sink"]},
            "s5": {'alpha': ["s6"], 'beta': ["s2", "s7"]},
            "s6": {'alpha': ["s5", "s6"], 'beta': ["sink"]},
            "s7": {'alpha': ["s2", "s3"], 'beta': ["sink"]},
            "sink": {'alpha': ["sink"], 'beta': ["sink"]},
        },
        init_state="s0",
        final=["s6"]
        # final=["s6", "s7"]
        # final=["s2", "s3"]
    )

    formula_ = PrefScLTL("Fa > Fb")
    model_ = formula_.model()
    aut_ = formula_.translate()
    assign_rank(aut_)

    product_mdp_ = ProductPrefMDP(mdp_, aut_)
    print(product_mdp_.pref_graph()["partition"].items())