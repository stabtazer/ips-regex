from src.python.states import StateCollection, State
from src.python.finite_automaton import DFA


if __name__ == "__main__":
    alphabet = ['a', 'b']

    # states
    s1 = State("s1", acc=True)
    s2 = State("s2", acc=True)
    s3 = State("s3")
    s4 = State("s4")

    # transitions
    s1.add_transition(s2, 'a')

    s2.add_transition(s1, 'a')
    s2.add_transition(s3, 'b')

    s3.add_transition(s4, 'a')
    s4.add_transition(s3, 'b')

    all_states = StateCollection([s1, s2, s3, s4])

    dfa = DFA(alphabet, s1, all_states)
    minimized_dfa = dfa.minimize()
    # minimized_dfa.print_as_gvfile()
    # minimized_dfa.export_as_gvfile("after_min_example")
