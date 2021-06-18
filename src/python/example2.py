from src.python.states import StateCollection, State
from src.python.finite_automaton import NFA

# Introduction to Compiler Design
# Figure 1.5 to 1.9 example

if __name__ == "__main__":
    alphabet = ['a', 'b', 'c']

    # states
    s1 = State("1")
    s2 = State("2")
    s3 = State("3")
    s4 = State("4", acc=True)
    s5 = State("5")
    s6 = State("6")
    s7 = State("7")
    s8 = State("8")

    # transitions
    s1.add_transition(s2)
    s1.add_transition(s5)

    s2.add_transition(s3, 'a')

    s3.add_transition(s4, 'c')

    s5.add_transition(s6)
    s5.add_transition(s7)

    s6.add_transition(s8, 'a')

    s7.add_transition(s8, 'b')

    s8.add_transition(s1)

    all_states = StateCollection([s1, s2, s3, s4, s5, s6, s7, s8])

    nfa = NFA(alphabet, s1, all_states)
    nfa.export_as_gvfile("example2_nfa")
    dfa = nfa.to_DFA()
    dfa.export_as_gvfile("example2_dfa")
