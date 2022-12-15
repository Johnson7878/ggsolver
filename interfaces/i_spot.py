"""
Defines an interface from spot automaton to ggsolver automaton.
"""

import spot
# from ggsolver.models import Automaton, models.register_property
import ggsolver.models as models 
from dd.autoref import BDD


class SpotAutomaton(models.Automaton):
    """
    `SpotAutomaton` constructs an :class:`models.Automaton` from an LTL specification string using
    `spot` (https://spot.lrde.epita.fr/) with customizations for `ggsolver`.

    **Customizations:** Since `ggsolver` contains several algorithms for reactive/controller synthesis,
    we prefer to construct deterministic automata. Given an LTL formula, `SpotAutomaton` automatically
    determines the best acceptance condition that would result in a deterministic automaton..

    Programmer's note: The graphified version of automaton does not use PL formulas as edge labels.
    This is intentionally done to be able to run our codes on robots that may not have logic libraries installed.
    """
    def __init__(self, formula=None, options=None, atoms=None):
        """
        Given an LTL formula, SpotAutomaton determines the best options for spot.translate() function
        to generate a deterministic automaton in ggsolver.models.Automaton format.

        :param formula: (str) LTL formula.
        :param options: (List/Tuple of str) Valid options for spot.translate() function. By default, the
            value is `None`, in which case, the options are determined automatically. See description below.

        **Default translation options:** While constructing an automaton using `spot`, we use the following
        options: `deterministic, high, complete, unambiguous, SBAcc`. If selected acceptance condition
        is parity, then we use `colored` option as well.

        The default options can be overriden. For quick reference, the following description is copied from
        `spot` documentation (spot.lrde.epita.fr/doxygen).

        The optional arguments should be strings among the following:
        - at most one in 'GeneralizedBuchi', 'Buchi', or 'Monitor',
        'generic', 'parity', 'parity min odd', 'parity min even',
        'parity max odd', 'parity max even', 'coBuchi'
        (type of acceptance condition to build)

        - at most one in 'Small', 'Deterministic', 'Any'
          (preferred characteristics of the produced automaton)
        - at most one in 'Low', 'Medium', 'High'
          (optimization level)
        - any combination of 'Complete', 'Unambiguous',
          'StateBasedAcceptance' (or 'SBAcc' for short), and
          'Colored' (only for parity acceptance)
        """
        # Construct the automaton
        super(SpotAutomaton, self).__init__(input_domain="atoms")

        # Instance variables
        self._formula = formula
        self._user_atoms = set(atoms) if atoms is not None else set()

        # If options are not given, determine the set of options to generate deterministic automaton with
        # state-based acceptance condition.
        if options is None:
            options = self._determine_options()

        print(f"[INFO] Translating {self._formula} with options={options}.")
        self.spot_aut = spot.translate(formula, *options)

        # Set the acceptance condition (in ggsolver terms)
        name = self.spot_aut.acc().name()
        if name == "Büchi" and spot.mp_class(formula).upper() in ["B", "S"]:
            self._acc_cond = (models.Automaton.ACC_SAFETY, 0)
        elif name == "Büchi" and spot.mp_class(formula).upper() in ["G"]:
            self._acc_cond = (models.Automaton.ACC_REACH, 0)
        elif name == "Büchi" and spot.mp_class(formula).upper() in ["O", "R"]:
            self._acc_cond = (models.Automaton.ACC_BUCHI, 0)
        elif name == "co-Büchi":
            self._acc_cond = (models.Automaton.ACC_COBUCHI, 0)
        elif name == "all":
            self._acc_cond = (models.Automaton.ACC_SAFETY, 0)
        else:  # name contains "parity":
            self._acc_cond = (models.Automaton.ACC_PARITY, 0)

    def _determine_options(self):
        """
        Determines the options based on where the given LTL formula lies in Manna-Pnueli hierarchy.
        """
        mp_cls = spot.mp_class(self.formula())
        if mp_cls.upper() == "B" or mp_cls.upper() == "S":
            return 'Monitor', "Deterministic", "High", "Complete", "Unambiguous", "SBAcc"
        elif mp_cls.upper() == "G" or mp_cls.upper() == "O" or mp_cls.upper() == "R":
            return 'Buchi', "Deterministic", "High", "Complete", "Unambiguous", "SBAcc"
        elif mp_cls.upper() == "P":
            return 'coBuchi', "Deterministic", "High", "Complete", "Unambiguous", "SBAcc"
        else:  # cls.upper() == "T":
            return 'parity min even', "Deterministic", "High", "Complete", "Unambiguous", "SBAcc", "colored"

    def states(self):
        """ States of automaton. """
        return list(range(self.spot_aut.num_states()))

    def atoms(self):
        """ Atomic propositions appearing in LTL formula. """
        return list({str(ap) for ap in self.spot_aut.ap()} | self._user_atoms)

    def delta(self, state, inp):
        """
        Transition function of automaton. For a deterministic automaton, returns a single state. Otherwise,
        returns a list/tuple of states.

        :param state: (object) A valid state.
        :param inp: (list) List of atoms that are true (an element of sigma).
        """
        # Preprocess inputs
        inp_dict = {p: True for p in inp} | {p: False for p in self.atoms() if p not in inp}

        # Initialize a BDD over set of atoms. 
        bdd = BDD()
        bdd.declare(*self.atoms())

        # Get spot BDD dict to extract formula 
        bdd_dict = self.spot_aut.get_dict()
        
        # Get next states
        next_states = []
        for t in self.spot_aut.out(state):
            label = spot.bdd_format_formula(bdd_dict, t.cond)
            label = spot.formula(label)
            if label.is_ff():
                continue
            elif label.is_tt():
                next_states.append(int(t.dst))
            else:
                label = spot.formula(label).to_str('spin')
                v = bdd.add_expr(label)
                if bdd.let(inp_dict, v) == bdd.true:
                    next_states.append(int(t.dst))

        # Return based on whether automaton is deterministic or non-deterministic.
        #   If automaton is deterministic but len(next_states) = 0, then automaton is incomplete, return None.
        if self.is_deterministic() and len(next_states) > 0:
            return next_states[0]

        if not self.is_deterministic():
            return next_states

    def init_state(self):
        """ Initial state of automaton. """
        return int(self.spot_aut.get_init_state_number())

    def final(self, state):
        """ Maps every state to its acceptance set. """
        if not self.is_state_based_acc():
            raise NotImplementedError
        return list(self.spot_aut.state_acc_sets(state).sets())

    def acc_cond(self):
        """
        Returns acceptance condition according to ggsolver definitions:
        See `ACC_REACH, ...` variables in models.Automaton class.
        See :meth:`SpotAutomaton.spot_acc_cond` for acceptance condition in spot's nomenclature.
        """
        return self._acc_cond

    def num_acc_sets(self):
        """ Number of acceptance sets. """
        return self.spot_aut.num_sets()

    def is_deterministic(self):
        """ Is the automaton deterministic? """
        return bool(self.spot_aut.prop_universal() and self.spot_aut.is_existential())

    def is_unambiguous(self):
        """
        There is at most one run accepting a word (but it might be recognized several time).
        See https://spot.lrde.epita.fr/concepts.html.
        """
        return bool(self.spot_aut.prop_unambiguous())

    def is_terminal(self):
        """
        models.Automaton is weak, accepting SCCs are complete, accepting edges may not go to rejecting SCCs.
        An automaton is weak if the transitions of an SCC all belong to the same acceptance sets.

        See https://spot.lrde.epita.fr/concepts.html
        """
        return bool(self.spot_aut.prop_terminal())

    def is_stutter_invariant(self):
        """
        The property recognized by the automaton is stutter-invariant
        (see https://www.lrde.epita.fr/~adl/dl/adl/michaud.15.spin.pdf)
        """
        return bool(self.spot_aut.prop_stutter_invariant())

    def is_complete(self):
        """ Is the automaton complete? """
        return bool(spot.is_complete(self.spot_aut))

    @models.register_property(models.Automaton.GRAPH_PROPERTY)
    def is_semi_deterministic(self):
        """
        Is the automaton semi-deterministic?
        See https://spot.lrde.epita.fr/doxygen/namespacespot.html#a56b3f00b7b93deafb097cad595998783
        """
        return bool(spot.is_semi_deterministic(self.spot_aut))

    @models.register_property(models.Automaton.GRAPH_PROPERTY)
    def acc_name(self):
        """ Name of acceptance condition as per spot's nomenclature. """
        return self.spot_aut.acc().name()

    @models.register_property(models.Automaton.GRAPH_PROPERTY)
    def spot_acc_cond(self):
        """
        Acceptance condition in spot's nomenclature.
        """
        return str(self.spot_aut.get_acceptance())

    @models.register_property(models.Automaton.GRAPH_PROPERTY)
    def formula(self):
        """ The LTL Formula. """
        return self._formula

    @models.register_property(models.Automaton.GRAPH_PROPERTY)
    def is_state_based_acc(self):
        """ Is the acceptance condition state-based? """
        return bool(self.spot_aut.prop_state_acc())

    @models.register_property(models.Automaton.GRAPH_PROPERTY)
    def is_weak(self):
        """
        Are transitions of an SCC all belong to the same acceptance sets?
        """
        return bool(self.spot_aut.prop_weak())

    @models.register_property(models.Automaton.GRAPH_PROPERTY)
    def is_inherently_weak(self):
        """ Is it the case that accepting and rejecting cycles cannot be mixed in the same SCC? """
        return bool(self.spot_aut.prop_inherently_weak())
