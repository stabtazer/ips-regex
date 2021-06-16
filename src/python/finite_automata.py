from typing import Dict, List
from queue import Queue

class State:

    def __init__(self, name: str, alphabet, acc=False) -> None:
        self.name = name
        self.alphabet = alphabet
        self.out  = set() # outgoing transitions
        self.acc  = acc  # accepting or non-accepting state

    def add_transition(self, to_state, transition=''):
        if transition and transition not in self.alphabet:
            raise Exception(f"Transition '{transition}' not in alphabet")
        self.out.add((to_state, transition))

    def add_transitions(self, to_states, transition=''):
        """ Add multiple state transitions with same transition

        Args:
            to_states (List[State]): list of states
            transition (str, optional): The transition character. Defaults to '' = epsilon.
        """
        for state in to_states:
            self.add_transition(state, transition)

    def get_transitions(self, c):
        res = []
        for state, transition in self.out:
            if c == transition:
                res.append(state)
        return res

    def epsilon_closure(self):
        res = [self]
        for state, transition in self.out:
            if not transition:
                res.extend(state.epsilon_closure())
        return set(res)

    def __repr__(self):
        return self.name

    def __str__(self) -> str:
        output = ""
        for state, transitions in self.out:
            if not transitions:
                transitions = "ε"
            output += f"{self.name} -> {state.name} [label = \"{transitions}\"];\n"
        return output.strip()


class FiniteAutomata:

    def __init__(self, startstate, states: List[State], alphabet) -> None:
        self.states     = states
        self.accepting  = [state.name for state in states if state.acc]
        self.startstate = startstate  # first state in list is start (will raise exception if list empty)
        self.alphabet   = alphabet

    def get_starclosure(self):
        return self.startstate.epsilon_closure()

    @staticmethod
    def any_acc_state(states) -> bool:
        for s in states:
            if s.acc:
                return True
        return False

    @staticmethod
    def get_state_by_name(name, states) -> State:
        for s in states:
            if s.name == name:
                return s
        raise Exception("State not found")

    def to_DFA(self):
        print("NFA to DFA")
        
        s0 = self.startstate.epsilon_closure()
        is_acc = self.any_acc_state(s0)
        acc = 'accepting' if is_acc else 'non-acc'
        
        print(f"start = ec({{{self.startstate.name}}}) = {s0} = s0 ({acc})")

        # create new start state
        start_state = State('s0', self.alphabet, acc=is_acc)
        new_states = [start_state]

        new_state_sets = {'s0': s0}
        new_state_index = 1
        new_state_queue = Queue()
        new_state_queue.put((start_state, s0))
        while not new_state_queue.empty():
            print()
            state, states = new_state_queue.get()

            for c in self.alphabet:
                print(f"move({state.name},{c}) = ", end='')
                next_state_set = set()

                # check which transitions are possible from the state
                for s in states:
                    res = s.get_transitions(c)
                    if res:
                        next_state_set.update(res)

                if next_state_set:
                    # get epsilon closures                
                    print(f"ec({next_state_set}) = ", end='')
                    temp = set()
                    for s in next_state_set:
                        temp.update(s.epsilon_closure())

                    next_state_set = temp

                    index = ""
                    for s, item in new_state_sets.items():
                        if item == next_state_set:
                            index = s  # state name

                    print(f"{index}", end='')
                    if not index:
                        # create new state
                        new_state_name = 's'+str(new_state_index)
                        new_state_sets[new_state_name] = next_state_set

                        is_acc = self.any_acc_state(next_state_set)
                        acc = 'accepting' if is_acc else 'non-acc'

                        new_state = State(new_state_name, self.alphabet, acc=is_acc)
                        new_states.append(new_state)

                        new_state_queue.put((new_state, next_state_set))
                        new_state_index += 1
                        index = new_state_name
                        # next_state_set = sorted(next_state_set, key = lambda s: s.name)
                        print(f"{next_state_set} = ", end='')
                        
                        print(f"{index} ({acc})", end='')

                    t_state = self.get_state_by_name(index, new_states)
                    state.add_transition(t_state, c)
                    print()
                else:
                    print(f"ec({{}}) = ", end='')
                    print("undefined")
        # loop end
        return new_states



    def print_as_gvfile(self) -> None:
        accstr = ''.join([' '+state for state in self.accepting])
        output = [
            f'digraph finite_state_machine {{',
        	f'rankdir=LR;',
            f'size="8,5"',
            f'node [shape = doublecircle];{accstr};',
            f'node [shape = circle];',
            f'startarrow [label= "", shape=none,height=.0,width=.0];',
            f'startarrow -> {self.startstate.name};'
        ]
        states_out = [str(state) for state in self.states]
        output.extend(states_out)
        output = '\n'.join(output) + '}'
        print(output)


if __name__ == "__main__":
    alphabet = ['a', 'b']

    # states
    s1 = State("1", alphabet)
    s2 = State("2", alphabet)
    s3 = State("3", alphabet)
    s4 = State("4", alphabet)
    s5 = State("5", alphabet)
    s6 = State("6", alphabet)
    s7 = State("7", alphabet, acc=True)

    # transitions
    s1.add_transition(s2)
    s1.add_transition(s4)

    s2.add_transition(s3)
    s2.add_transition(s5)

    s3.add_transition(s2, 'a')
    
    s4.add_transition(s5, 'b')

    s5.add_transition(s6)

    s6.add_transition(s7, 'a')

    # s7 no outs

    alphabet = ['a', 'b']
    all_states = set([s1, s2, s3, s4, s5, s6, s7])
    finiteAutomata = FiniteAutomata(s1, all_states, alphabet)
    # print(finiteAutomata.get_starclosure())
    newstates = finiteAutomata.to_DFA()
    # newfiniteAutomata = FiniteAutomata(newstates[0], newstates, alphabet)
    # # finiteAutomata.print_as_gvfile()
    # newfiniteAutomata.print_as_gvfile()
    
