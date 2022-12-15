__version__ = "0.1.5"


CHANGELOG = {
    "0.1.2": [
        "Added new docker latest, devel images. Updated installation instructions in documentation.",
        "Added `is_isomorphic_to` function to Graph class. Updated docs and example.",
    ],
    "0.1.3": [
        "Added `logic.pl` module with `simplify, evaluate, to_plformula` and `all_sat` methods for PL formulas.",
        "Moved `sigma` method to `Automaton` class with default implementation.",
        "Fixed the representation of `Automaton` acceptance conditions.",
        "Added new module: `automata`, with `DFA, Monitor, DBA, DCBA, DPA` classes. Docs and example added.",
        "Automaton can be constructed by passing components (Q, AP, Trans, q0, F) to the constructor.",
    ],
    "0.1.4": [
        "Bugfix in `SpotAutomaton.is_semi_deterministic() function. ",
        "SpotAutomaton.acc_cond adheres to ggsolver.models.Automaton convention.",
        "Made init arguments to classes in ggsolver.automata optional.",
        "Added Automaton.from_automaton() function to construct DFA, DBA ... from SpotAutomaton."
        "Added example for translating LTL to DFA."
    ],
    "0.1.5": [
        "Pointed graphify implemented for GraphicalModel. ",
        "SubGraph class added. ",
        "Solvers now operate on SubGraph on given graph to construct node_winner, edge_winner properties.",
        "GraphicalModel.states() is now REQUIRED to return a list of hashable objects.",
        "dtptb package added for deterministic two-player turn-based games. "
        "SWin, ASWin for algorithms for reachability and safety added.",
        "mdp package added for qualitative Markov decision processes. ASWin, PWin algorithms for reachability added.",
        "Added progress bars to graphify and solvers in dtptb package.",
        "[Bugfix] input_domain stores the name of function (= graph property) that stores the input domain. Thus, "
        "the reconstructed graphical model has the same input domain functions as the original model.",
    ],
    "0.1.6": [
        "SpotAutomaton inputs `atoms` as optional parameters. "
        "Users can specify any atoms that do not appear in the input formula.",
        "Automaton graphify merges edges using PL formula for edge labels.",

    ]
}
