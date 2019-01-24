# fst.py
#
# Weighted Finite State Transducers, with composition and
# shortest paths.

import pickle

EPS='<eps>'

class FST(object):
    """
    A finite-state transducer, defined as an initial state,
    a set of final states, and a set of weighted transitions.
    Each transition from state1 to state2 with input symbol
    isym and output symbol osym is a tuple
    (state1, state2, isym, osym). Transitions are additionally
    indexed by state1, isym and osym.
    """    
    def __init__(self):
        self.initial = None
        self.final = set()
        self.transitions = {}
        self.transitions_by_isym = {}
        self.transitions_by_osym = {}
        self.transitions_by_state = {}
        
    def add_transition(self, state1, state2, isym, osym, weight=0):
        """
        Add a transition to the FST. If the transition already
        exists, add weight to the existing weight.
        """
        if (state1, state2, isym, osym) not in self.transitions:
            self.transitions[(state1, state2, isym, osym)] = 0
        self.transitions[(state1, state2, isym, osym)] += weight
        if state1 not in self.transitions_by_state:
            self.transitions_by_state[state1] = {}
        if isym not in self.transitions_by_isym:
            self.transitions_by_isym[isym] = {}
        if osym not in self.transitions_by_osym:
            self.transitions_by_osym[osym] = {}
        if (state1, state2, isym, osym) not in self.transitions_by_state[state1]:
            self.transitions_by_state[state1][(state1, state2, isym, osym)] = 0
        if (state1, state2, isym, osym) not in self.transitions_by_isym[isym]:
            self.transitions_by_isym[isym][(state1, state2, isym, osym)] = 0
        if (state1, state2, isym, osym) not in self.transitions_by_osym[osym]:
            self.transitions_by_osym[osym][(state1, state2, isym, osym)] = 0
            
        self.transitions_by_state[state1][(state1, state2, isym, osym)] += weight
        self.transitions_by_isym[isym][(state1, state2, isym, osym)] += weight
        self.transitions_by_osym[osym][(state1, state2, isym, osym)] += weight

    def set_initial(self, s):
        """
        Set the initial state. There is only one initial state.
        """
        self.initial = s

    def set_final(self, s):
        """
        Set state s as a final state. There can be multiple final states.
        """
        self.final.add(s)

    def unset_final(self, s):
        if s in self.final:
            self.final.remove(s)

    def short_paths(self, n=1):
        """
        Find n shortest paths. 
        Won't work with negative weights.
        """
        if self.initial == None:
            return None
        if len(self.final) == 0:
            return None

        # Best first search, from the initial state to any of
        # the final states. Won't work with negative weights.
        
        h = [(self.initial, 0, [])]
        paths = []

        while len(paths) < n and len(h) > 0:
            accepted = False
            while len(h) > 0:
                h.sort(key=lambda p: p[1])
                curr = h.pop(0)
                if curr[0] in self.final:
                    accepted = True
                    break
                if curr[0] not in self.transitions_by_state:
                    continue
                for transition in self.transitions_by_state[curr[0]]:
                    h.append((transition[1], curr[1]+self.transitions_by_state[curr[0]][transition], curr[2]+[(transition[2], transition[3])]))
            if accepted:
                istr = [w[0] for w in curr[2]]
                ostr = [w[1] for w in curr[2]]
                while EPS in ostr:
                    ostr.remove(EPS)
                paths.append((curr[1], istr, ostr))
            if len(paths) > n:
                break
        
        return paths
    
    def print_transitions(self):
        for t in self.transitions:
            print(t, self.transitions[t])

    def save(self, fname):
        pickle.dump(self, open(fname, 'wb'))

def load(fname):
    f = pickle.load(open(fname, 'rb'))
    return f

def compose(f, g):
    """
    Compose two FSTs, f and g.
    """
    c = FST()
    c.initial = (f.initial, g.initial)
    
    for ff in f.final:
        for gf in g.final:
            c.set_final((ff, gf))
    
    for osym in f.transitions_by_osym:
        if osym == EPS:
            continue
        ftrans = f.transitions_by_osym[osym]
        if osym in g.transitions_by_isym:
            gtrans = g.transitions_by_isym[osym]
            for t1 in ftrans:
                for t2 in gtrans:
                    c.add_transition((t1[0], t2[0]),
                                     (t1[1], t2[1]),
                                     t1[2], t2[3],
                                     ftrans[t1] + gtrans[t2])

    if EPS in f.transitions_by_osym:
        ftrans = f.transitions_by_osym[EPS]
        for t1 in ftrans:
            for st2 in set([s2 for (s1, s2, isym, osym) in g.transitions]):
                c.add_transitions((t1[0], st2),
                                  (t1[1], st2),
                                  t1[2], EPS, ftrans[t1])

    if EPS in g.transitions_by_isym:
        gtrans = g.transitions_by_isym[EPS]
        for t2 in gtrans:
            for st1 in set([s2 for (s1, s2, isym, osym) in f.transitions]):
                c.add_transitions((st1, t2[0]),
                                  (st1, t2[1]),
                                  EPS, t2[3], gtrans[t2])
    
    return c

def linear_chain(syms):
    """
    Create a linear chain FST, encoding a string.
    syms is a list containing the symbols of the string.
    """
    f = FST()
    curr_state = 0
    f.set_initial(curr_state)
    for s in syms:
        next_state = curr_state + 1
        f.add_transition(curr_state, next_state, s, s, 0)
        curr_state = next_state
    f.set_final(curr_state)
    return f

def linear_chain_from_string(mystr, sep=''):
    """
    Create a linear chain FST, encoding a string.
    mystr is a string, and sep is the separator. If no
    separator is provided, the string is split into
    characters.
    """
    if sep == '':
        toks = list(mystr)
    else:
        toks = mystr.split(sep=sep)

    return linear_chain(toks)

def main():

    # Encode a string as an FST, using white space as separator
    myfst1 = linear_chain_from_string("This is a test", ' ')

    # Create an FST transition by transition
    myfst2 = FST()
    myfst2.add_transition('w0', 'w0', 'This', 'this', 1)
    myfst2.add_transition('w0', 'w0', 'This', 'This', 0)
    myfst2.add_transition('w0', 'w0', 'is', 'is', 1)
    myfst2.add_transition('w0', 'w0', 'a', 'one', 1)
    myfst2.add_transition('w0', 'w0', 'a', 'a', 0)
    myfst2.add_transition('w0', 'w0', 'test', 'test', 0)

    myfst2.set_initial('w0')
    myfst2.set_final('w0')

    # Compose the two FSTs
    c = compose(myfst1, myfst2)

    # Find the shortest paths 
    cpaths = c.short_paths(10)
    print(cpaths)
    
if __name__ == '__main__':
    main()

