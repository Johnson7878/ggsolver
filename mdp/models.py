from ggsolver.models import Game


def filter_kwargs(states=None, actions=None, trans_dict=None, init_state=None, final=None):
    kwargs = dict()
    if states is not None:
        kwargs["states"] = states

    if actions is not None:
        kwargs["actions"] = actions

    if trans_dict is not None:
        kwargs["trans_dict"] = trans_dict

    if init_state is not None:
        kwargs["init_state"] = init_state

    if final is not None:
        kwargs["final"] = final

    return kwargs


class QualitativeMDP(Game):
    """
    delta(s, a) -> [s]
    """
    def __init__(self, states=None, actions=None, trans_dict=None, init_state=None, final=None):
        kwargs = filter_kwargs(states, actions, trans_dict, init_state, final)
        super(QualitativeMDP, self).__init__(
            **kwargs,
            is_deterministic=False,
            is_probabilistic=False,
            is_turn_based=False
        )


