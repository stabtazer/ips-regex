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
        # if states have origin then include
        originstr = []
        for state in self.sc:
            if state.origin:
                originstr += [f"{state.name} [label = \"{state.name}"+r'\n'+f"{state.origin}\"]"]

        if originstr:
            output.extend(originstr)

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

    def minimize(self, verbose=True):
        # Initialize variable(s)
        self.name_index = 1

        # -- helper functions ----------------------------------------------- #
        def acc_to_str(is_acc: bool) -> str:
            return 'acc' if is_acc else 'non-acc'

        def next_group_name():
            """ Ex: first group = 'G1', next = 'G2' """
            name = 'G'+str(self.name_index)
            self.name_index += 1
            return name

        def add_unmarked_groups_to_queue(groups, q) -> None:
            q.queue.clear()  # clear queue
            for unmarked_group in groups:
                # only add groups with at least two states
                if len(groups[unmarked_group].states_by_name) > 1:
                    q.put(unmarked_group)

        def final_singleton_output(groups) -> str:
            out = []
            for gn in groups:

                # final output for singletons
                if len(groups[gn].states_by_name) == 1:

                    # fetching singleton
                    for key, item in groups[gn].states_by_name.items():
                        sn = key
                        state = item
                        break

                    # 'pseudo'-array header
                    header = f"{gn}  "+'  '.join([c for c in self.alphabet])
                    out += [
                        f"\nFinal table for {gn}:\n",
                        f"\n{header}\n",
                        "-"*(len(header)+1)  # pretty printing array line
                    ]

                    res = []
                    # to check consistency we use string matching
                    for c in self.alphabet:
                        label_transitions = state.get_label_transitions(c)

                        # * There can only be one or zero transitions in the
                        # * returned list because graph is DFA
                        if label_transitions:
                            to_state = label_transitions[0]

                            # get group name
                            for gn, states in groups.items():
                                if states.get(to_state.name):
                                    res.append(gn)
                        else:
                            res.append(' -')

                    # add the result to results as tuple
                    res = ' '.join(res)
                    out += [f"\n{sn}  {res}"]
                out += ["\n"]
            return out

        #######################################################################
        # start by creating two new groups:
        # G1 for all accepting states
        # G2 for all non-acc. states
        #######################################################################
        groups = {}
        g1_name = next_group_name()
        g2_name = next_group_name()
        groups[g1_name] = StateCollection()  # G1
        groups[g2_name] = StateCollection()  # G2

        for state in self.sc:
            if state.acc:
                groups[g1_name].add(state)
            else:
                groups[g2_name].add(state)

        # output strings
        output = ['-'*80 + "\nMinimizing DFA\n" + '-'*80 + "\n"]
        output += [
            f"{g1_name} = {groups[g1_name].state_names():<13} accepting\n",
            f"{g2_name} = {groups[g2_name].state_names():<13} non-accepting\n"
        ]

        # Initialize queue for new groups and related DFA state sets
        unmarked_groups = Queue()
        add_unmarked_groups_to_queue(groups, unmarked_groups)

        while not unmarked_groups.empty():

            # get next state set from queue
            group_name = unmarked_groups.get()
            group_to_check = groups[group_name]

            # output strings
            # 'pseudo'-array header
            header = f"{group_name}  " + '  '.join([c for c in self.alphabet])
            output += [
                f"\nChecking {group_name}:\n",
                f"\n{header}\n",
                "-"*(len(header)+1)  # pretty printing array line
            ]

            results = []
            for state in group_to_check:
                res = []
                # to check consistency we use string matching
                for c in self.alphabet:
                    label_transitions = state.get_label_transitions(c)

                    # * There can only be one or zero transitions in the
                    # * returned list because graph is DFA
                    if label_transitions:
                        to_state = label_transitions[0]

                        # get group name
                        for gn, states in groups.items():
                            if states.get(to_state.name):
                                res.append(gn)
                    else:
                        res.append(' -')

                # add the result to results as tuple
                res = ' '.join(res)
                results.append((state, res))

                # output strings
                output += [f"\n{state.name}  {res}"]
            output += ["\n"]

            # Is group consistent??
            is_consistent = True
            rows = len(results)
            for i in range(1, rows):
                if results[0][1] != results[i][1]:
                    is_consistent = False
                    break
            if is_consistent:
                output += [f"\n{group_name} is consistent!\n"]
            else:
                output += [f"\nNot consistent! Split {group_name} into:\n\n"]

                # Split into new groups
                # * First: group the identical states
                new_groups = {}
                for r in results:
                    # to_groups: remember, just a simple string
                    state, to_groups = r
                    try:
                        new_groups[to_groups].append(state)
                    except KeyError:
                        new_groups[to_groups] = [state]

                # * Second: create new groups and add to groups
                for row, states in new_groups.items():

                    next_name = next_group_name()
                    gc = StateCollection(states)
                    groups[next_name] = gc

                    # output strings
                    output += [
                        f"{next_name} = {gc.state_names()}\t(row {row})\n"
                    ]

                # * Third: 'mark' original group as obsolete (remove)
                groups.pop(group_name)

                # * Fourth: reset queue
                add_unmarked_groups_to_queue(groups, unmarked_groups)

                # output strings
                output += [
                    f"\nMarking {group_name} obsolete!\n",
                    "Reset queue (unmark groups)\n",
                    "\n--\n"
                ]
        # while-loop end

        #######################################################################
        # Create new minimized DFA and final output strings
        #######################################################################

        # output strings - singleton groups
        output += final_singleton_output(groups)

        # output strings - final transition table
        header = f"    " + '  '.join([c for c in self.alphabet])
        output += [
            f"\nFinal transition table:\n",
            f"\n{header}\n",
            "-"*(len(header)+1)  # pretty printing array line
        ]

        minimized_sc = StateCollection()
        start_state = None
        for group_name, sc in groups.items():
            ###################################################################
            # Every new group in groups has a StateCollection with
            # original states. We need to figure out which of the new groups
            # the original states belong to, in order to make the new table
            # for G transitions.
            ###################################################################

            # Create new State
            is_start = sc.get(self.start.name)
            start = "start, " if is_start else ''
            origin = sc.state_names().replace(' ', '')
            accepting = sc.any_accepting()

            existing_state = minimized_sc.get(group_name)
            if existing_state:
                # already exists - add origin and acc
                existing_state.origin = origin
                existing_state.acc = accepting
                new_state = existing_state
            else:
                new_state = State(group_name, acc=accepting, origin=origin)
                # add to StateCollections
                minimized_sc.add(new_state)

            if is_start:
                start_state = new_state

            res = []
            for c in self.alphabet:
                state_transitions = sc.move(c)
                is_acc = state_transitions.any_accepting()

                if state_transitions.states_by_name:
                    # just pick one, as they are consistent
                    for key in state_transitions.states_by_name:
                        sn = key
                        break

                    # get group name
                    for gn, states in groups.items():
                        if states.get(sn):
                            # check to see if it already exists
                            t_state = minimized_sc.get(gn)
                            if not t_state:  # not found - create
                                t_state = State(gn)  # will be updated later

                            new_state.add_transition(t_state, c)
                            res.append(gn)
                else:
                    res.append(' -')

            # add the result to results as tuple
            res = ' '.join(res)

            # output strings
            output += [f"\n{group_name}  {res}    {start}{acc_to_str(is_acc)}"]
        output += ["\n"]

        if verbose:
            print(''.join(output))
        return DFA(self.alphabet, start_state, minimized_sc)

    def __repr__(self):
        return "DFA"
