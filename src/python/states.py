from typing import Iterable, List, Set
from src.python.transitions import Transition, TransitionCollection


class State:

    def __init__(self, name: str, acc=False, origin: str = '') -> None:
        self.transitions = TransitionCollection()  # initialize collection
        self.name = name
        self.acc = acc  # accepting or non-accepting state
        self.origin = origin  # to print original states after minimize

    # Methods
    def add_transition(self, to_state: 'State', label: str = '') -> None:
        self.transitions.add(Transition(to_state, label))

    def get_epsilon_transitions(self) -> List['State']:
        return self.transitions.get_epsilon_transitions()

    def get_label_transitions(self, label: str) -> List['State']:
        trans = self.transitions.get_label_transitions(label)
        return [t.to_state for t in trans]

    def epsilon_closure(self, visited_states:
                        List['State'] = []) -> Set['State']:
        res = [self]
        eps_trans = self.get_epsilon_transitions()
        for state in eps_trans:
            if not visited_states or state not in visited_states:
                # * Avoid loop by 'marking' visited states
                update_visited_states = eps_trans + visited_states
                res.extend(state.epsilon_closure(update_visited_states))
        return set(res)

    def __repr__(self):
        return self.name

    def __str__(self) -> str:
        output = ""
        for label, transitions in self.transitions.tbl.items():
            for transition in transitions:
                output += f"{self.name} -> {transition.to_state.name} "
                output += f"[label = \"{label}\"];\n"
        return output.strip()


class StateCollection:

    def __init__(self, states: Iterable[State] = []) -> None:
        self.states_by_name = {}
        self.accepting = []
        for state in states:
            self.add(state)

    # Methods
    def add(self, state):
        self.states_by_name[state.name] = state
        if state.acc:
            self.accepting.append(state)

    def get(self, state_name):
        try:
            res = self.states_by_name[state_name]
        except KeyError:
            res = None
        return res

    def move(self, label) -> 'StateCollection':
        res = set()
        for _, state in self.states_by_name.items():
            res.update(state.get_label_transitions(label))
        return StateCollection(res)

    def ec(self):
        new_states = []
        for _, state in self.states_by_name.items():
            temp = state.epsilon_closure()
            for state in temp:
                new_states.append(state)
        for state in new_states:
            self.add(state)

    def any_epsilon(self) -> bool:
        for _, state in self.states_by_name.items():
            if state.transitions.any_epsilon():
                return True
        return False

    def any_ambiguous_transitions(self) -> bool:
        for _, state in self.states_by_name.items():
            if state.transitions.any_ambiguous_transitions():
                return True
        return False

    def any_accepting(self) -> bool:
        if self.accepting:
            return True
        else:
            return False

    def state_names(self):
        """ Set of states represented by their names (sorted) """
        res = []
        for _, state in self.states_by_name.items():
            res.append(state.name)
        res.sort()
        output = ", ".join(res)
        return f"{{{output}}}"

    def __iter__(self):
        """ Make class object iterable """
        return (state for
                _, state in self.states_by_name.items())

    def __str__(self) -> str:
        res = []
        for _, state in self.states_by_name.items():
            res += [str(state)]
        return '\n'.join(res)

    def __eq__(self, sc: 'StateCollection') -> bool:
        """ Comparison of two StateCollections by dictionary """
        return self.states_by_name == sc.states_by_name
