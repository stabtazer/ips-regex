from src.python.states import StateCollection, State
from src.python.finite_automaton import NFA


if __name__ == "__main__":
    alphabet = ['a', 'b']

    # states
    s1 = State("1")
    s2 = State("2")
    s3 = State("3")
    s4 = State("4")
    s5 = State("5")
    s6 = State("6")
    s7 = State("7", acc=True)

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

    all_states = StateCollection([s1, s2, s3, s4, s5, s6, s7])

    nfa = NFA(alphabet, s1, all_states)
    nfa.print_as_gvfile()
    dfa = nfa.to_DFA()
    dfa.print_as_gvfile()
