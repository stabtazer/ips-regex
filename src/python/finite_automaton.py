from typing import List
from queue import Queue
from src.python.states import StateCollection, State


class FiniteAutomaton:

    def __init__(self, alphabet: List[str],
                 startstate: State,
                 state_collection: StateCollection) -> None:
        self.alphabet = alphabet
        self.start = startstate
        self.sc = state_collection

    def to_graphviz(self) -> str:
        accstr = ''.join(
            [' '+state.name for state in self.sc.accepting])
        output = [
            f'digraph finite_state_machine {{',
            f'rankdir=LR;',
            f'size="8,5"',
            f'node [shape = doublecircle];{accstr};',
            f'node [shape = circle];',
            f'startarrow [label= "", shape=none,height=.0,width=.0];',
            f'startarrow -> {self.start.name};'
        ]
        states_out = [str(self.sc)]
        output.extend(states_out)
        output = '\n'.join(output) + '}'
        return output

    def print_as_gvfile(self) -> None:
        commentline = '#' + '='*79
        print(commentline)
        print(f"# Graphviz file format")
        print(f"# Graph type: {self}")
        print(commentline)
        print(self.to_graphviz())

    def export_as_gvfile(self, filename) -> None:
        path = f'src/graphviz/{filename}.gv'
        print(f"Exporting FA to graphviz file: {path}")
        with open(path, 'w') as f:
            f.write(self.to_graphviz())


class NFA(FiniteAutomaton):

    def to_DFA(self, verbose=True) -> 'DFA':
        # helper functions
        def acc_to_str(is_acc: bool) -> str:
            return 'accepting' if is_acc else 'non-acc'

        output = [
            '-'*80 + "\nNFA to DFA\n" + '-'*80 + "\n"
            ]

        s0 = StateCollection(self.start.epsilon_closure())  # StateCollection

        is_acc = s0.any_accepting()
        acc = acc_to_str(is_acc)

        output += [
            f"start = ec({{{self.start.name}}}) = {s0.state_names()} = s0 ({acc})\n"
        ]

        # create new start state
        start_state = State('s0', acc=is_acc)
        new_states = StateCollection([start_state])

        new_state_sets = {start_state.name: s0}
        new_state_index = 1
        new_state_queue = Queue()
        new_state_queue.put((start_state, s0))
        while not new_state_queue.empty():

            output += ["\n"]
            state, states = new_state_queue.get()

            for c in self.alphabet:

                output += [f"move({state.name},{c}) = "]

                # check which transitions are possible from the state'

                next_state_set = states.move(c)

                if next_state_set.states_by_name:  # dictionary not empty
                    # get epsilon closures

                    # TODO: Validate str output
                    output += [
                        f"ec({next_state_set.state_names()}) = "
                        ]

                    next_state_set.ec()

                    index = ""
                    for s, item in new_state_sets.items():
                        if item == next_state_set:  # needs to be equal
                            index = s  # state name

                    output += [f"{index}"]

                    if not index:
                        # create new state
                        new_state_name = 's'+str(new_state_index)
                        new_state_sets[new_state_name] = next_state_set

                        is_acc = next_state_set.any_accepting()
                        acc = 'accepting' if is_acc else 'non-acc'

                        new_state = State(new_state_name, acc=is_acc)
                        new_states.add(new_state)

                        new_state_queue.put((new_state, next_state_set))
                        new_state_index += 1
                        index = new_state_name

                        output += [f"{next_state_set.state_names()} = "]

                        output += [f"{index} ({acc})"]

                    t_state = new_states.get(index)
                    state.add_transition(t_state, c)

                    output += ["\n"]
                else:
                    output += [f"ec({{}}) = undefined\n"]
        # loop end
        if verbose:
            print(''.join(output))
        return DFA(self.alphabet, start_state, new_states)

    def __repr__(self):
        return "NFA"


class DFA(FiniteAutomaton):

    def __init__(self, alphabet: List[str],
                 startstate: State,
                 state_collection: StateCollection) -> None:
        super().__init__(alphabet, startstate, state_collection)
        self.validate()

    def validate(self) -> None:
        # check if DFA has legal transitions
        if self.sc.any_epsilon():
            raise Exception("Illegal DFA: cannot have epsilon transitions.")
        elif self.sc.any_ambiguous_transitions():
            raise Exception("Illegal DFA: cannot ambiguous transitions.")
        else:
            pass

    def __repr__(self):
        return "DFA"
