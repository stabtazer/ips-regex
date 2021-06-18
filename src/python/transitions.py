from typing import List, Set


class Transition:

    def __init__(self, to_state: 'State', label: str = '') -> None:
        self.epsilon = False
        self.to_state = to_state
        self.label = label  # transition label (character)
        if not label:
            self.label = 'ε'
            self.epsilon = True


class TransitionCollection:
    """ Transitions for a given state
    """

    def __init__(self, transitions: List[Transition] = []) -> None:
        self.tbl = {}  # transitions by label
        for transition in transitions:
            self.add(transition)

    # Methods
    def add(self, transition: Transition):
        """ Add new transition to collection """
        try:
            self.tbl[transition.label].add(transition)
        except KeyError:
            self.tbl[transition.label] = set([transition])

    def get_epsilon_transitions(self) -> List['State']:
        """ Get all epsilon transitions from the state """
        eps_trans = []
        for _, transitions in self.tbl.items():
            for transition in transitions:
                if transition.epsilon:
                    eps_trans.append(transition.to_state)
        return eps_trans

    def get_label_transitions(self, label: str) -> Set['State']:
        try:
            return self.tbl[label]
        except KeyError:
            return set()

    # Conditions not allowed in DFA
    def any_epsilon(self) -> bool:
        for _, transitions in self.tbl.items():
            for transition in transitions:
                if transition.epsilon:
                    return True
        return False

    def any_ambiguous_transitions(self) -> bool:
        for _, transitions in self.tbl.items():
            if len(transitions) > 1:
                return True
        return False
