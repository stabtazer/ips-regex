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
        # Initialize variable(s)
        self.name_index = 0

        # -- helper functions ----------------------------------------------- #
        def acc_to_str(is_acc: bool) -> str:
            return 'accepting' if is_acc else 'non-acc'

        def next_state_name():
            """ Ex: start state = 's0', next = 's1' """
            name = 's'+str(self.name_index)
            self.name_index += 1
            return name

        #######################################################################
        # ec(start_state) -> start_set:
        # Gives us the set of states reachable from
        # the NFA start state through epsilon transitions
        #######################################################################
        start_set = StateCollection(self.start.epsilon_closure())

        # create new start state
        new_state_name = next_state_name()
        start_state = State(new_state_name, acc=start_set.any_accepting())

        # create new StateCollection for all the final DFA states
        dfa_states = StateCollection([start_state])

        # output strings
        output = ['-'*80 + "\nNFA to DFA\n" + '-'*80 + "\n"]
        output += [
            f"start = ec({{{self.start.name}}}) = ",
            f"{start_set.state_names()} = {new_state_name} ",
            f"({acc_to_str(start_state.acc)})\n"
        ]

        #######################################################################
        # dfa_state_sets: Dictionary linking the new DFA states with the NFA
        # state sets which is used to determine if a new DFA state should be
        # created or if the NFA set is already linked to an existing DFA state
        #######################################################################
        dfa_state_sets = {start_state.name: start_set}

        # Initialize queue for new DFA states and related NFA state sets
        new_state_queue = Queue()
        new_state_queue.put((start_state, start_set))

        while not new_state_queue.empty():

            # output strings - spacing
            output += ["\n"]

            # get next state set from queue
            dfa_state, nfa_state_set = new_state_queue.get()

            # check possible transitions for every label in alphabet
            for c in self.alphabet:

                # output strings
                output += [f"move({dfa_state.name},{c}) = "]

                ###############################################################
                # move(c): check which transitions are reachable from the state
                # through the label c
                ###############################################################
                next_state_set = nfa_state_set.move(c)

                if next_state_set.states_by_name:  # dictionary not empty

                    # output strings
                    output += [f"ec({next_state_set.state_names()}) = "]

                    # get epsilon closures
                    next_state_set.ec()

                    ###########################################################
                    # check if next_state_set already is referenced by
                    # a new DFA state
                    ###########################################################
                    new_state_name = ''
                    for sn, nfa_states in dfa_state_sets.items():
                        if nfa_states == next_state_set:  # needs to be equal
                            new_state_name = sn  # sn: state name

                    # output strings
                    temp = [f"{new_state_name}\n"]

                    if not new_state_name:

                        # create new state
                        new_state_name = next_state_name()
                        new_state = State(new_state_name,
                                          acc=next_state_set.any_accepting())

                        # add new state to DFA StateCollection
                        dfa_state_sets[new_state_name] = next_state_set
                        dfa_states.add(new_state)

                        # enqueue new DFA state and related NFA state set
                        new_state_queue.put((new_state, next_state_set))

                        # output strings - overwrite temp
                        temp = [
                            f"{next_state_set.state_names()} = ",
                            f"{new_state_name} ({acc_to_str(new_state.acc)})\n"
                            ]

                    ###########################################################
                    # Add the transition to the new DFA state for the current
                    # label c. This can be an already existing DFA state,
                    # including dfa_state (loop) or a new state created in the
                    # current iteration.
                    ###########################################################
                    to_state = dfa_states.get(new_state_name)
                    dfa_state.add_transition(to_state, c)

                    # output strings
                    output += temp
                else:
                    output += [f"ec({{}}) = undefined\n"]

        # while-loop end
        # print output if verbose = True
        if verbose:
            print(''.join(output))
        return DFA(self.alphabet, start_state, dfa_states)

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
