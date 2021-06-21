from src.python.states import StateCollection, State
from src.python.finite_automaton import DFA


if __name__ == "__main__":
    # alphabet
    alphabet = ['a', 'b']

    # states
    s0 = State("s0", acc=True)
    s1 = State("s1")
    s2 = State("s2")
    s3 = State("s3")
    s4 = State("s4")

    # transitions
    s0.add_transition(s1, 'a')
    s0.add_transition(s2, 'b')

    s1.add_transition(s2, 'a')
    s1.add_transition(s0, 'b')

    s2.add_transition(s3, 'a')
    s2.add_transition(s3, 'b')

    s3.add_transition(s4, 'a')
    s3.add_transition(s0, 'b')

    s4.add_transition(s0, 'b')
    s4.add_transition(s3, 'a')

    # NFA
    nfa = NFA(alphabet, s0, StateCollection([s0, s1, s2, s3, s4]))

    # NFA to DFA
    dfa = nfa.to_DFA()

    # DFA
    # dfa = DFA(alphabet, s0, StateCollection([s0, s1, s2, s3, s4]))

    # Minimize DFA
    minimized_dfa = dfa.minimize()
    
    nfa.print_as_gvfile()
    dfa.print_as_gvfile()
    minimized_dfa.print_as_gvfile()
