from typing import Dict, List


class State:

    def __init__(self, name: str, out: Dict, acc=False) -> None:
        self.name = name
        self.out  = out  # outgoing edges
        self.acc  = acc  # accepting or non-accepting state

    def __str__(self) -> str:
        output = ""
        for edge, char in self.out.items():
            if not char:
                char = "ε"
            output += f"{self.name} -> {edge} [label = \"{char}\"];\n"
        return output.strip()


class FiniteAutomata:

    def __init__(self, states: List[State]) -> None:
        self.states     = states
        self.accepting  = [state.name for state in states if state.acc]
        self.startstate = states[0].name  # first state in list is start (will raise exception if list empty)

    def print_as_gvfile(self) -> None:
        accstr = ''.join([' '+state for state in self.accepting])
        output = [
            f'digraph finite_state_machine {{',
        	f'rankdir=LR;',
            f'size="8,5"',
            f'node [shape = doublecircle];{accstr};',
            f'node [shape = circle];',
            f'startarrow [label= "", shape=none,height=.0,width=.0];',
            f'startarrow -> {self.startstate};'
        ]
        states_out = [str(state) for state in self.states]
        output.extend(states_out)
        output = '\n'.join(output) + '}'
        print(output)


if __name__ == "__main__":
    # new_states = [
    #     State("1", {"2": 'a'}, acc=True),
    #     State("2", {"1": 'a', "3": 'b'}, acc=True),
    #     State("3", {})
    # ]
    new_states = [
        State("1", {"2": 'a', "3": 'a'}),
        State("2", {"3": 'b', "4": 'a'}),
        State("3", {"2": '', "4": 'b'}, acc=True),
        State("4", {"5": ''}),
        State("5", {"2": 'a', "4": 'b'}, acc=True),
    ]
    finiteAutomata = FiniteAutomata(new_states)
    finiteAutomata.print_as_gvfile()
