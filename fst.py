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

    class Transition(object):
        def __init__(self, from_st, to_st, isym, osym, w):
            self.from_state = from_st
            self.to_state = to_st
            self.isym = isym
            self.osym = osym
            self.w = w
            
    def __init__(self):
        self.initial = None
        self.final = set()
        self.rm = {}
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

    def rm_transition(self, t):
        """
        Removes a transition from the FST.
        """
        if t in self.transitions:
            del self.transitions[t]
            del self.transitions_by_isym[t[2]][t]
            del self.transitions_by_osym[t[3]][t]
            del self.transitions_by_state[t[0]][t]
            
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
        
        h = [(self.initial, 0, [], 0, '')]
        paths = []
        chart = {}
        
        while len(paths) < n and len(h) > 0:
            accepted = False
            while len(h) > 0:
                h.sort(key=lambda p: p[1])
                curr = h.pop(0)
                #print(curr)
                if curr[0] in self.final:
                    accepted = True
                    break
                if curr[0] not in self.transitions_by_state:
                    continue
                if curr[0] in self.rm:
                    continue
                to_add = []
                for transition in self.transitions_by_state[curr[0]]:
                    if transition[0] in self.rm or transition[1] in self.rm:
                        continue
                    sym_cnt = curr[3]
                    sym = transition[3]
                    if sym == EPS:
                        sym = curr[4]
                    score = curr[1]+self.transitions_by_state[curr[0]][transition]
                    if transition[2] != EPS:
                        sym_cnt += 1
                    if (sym_cnt, sym) not in chart:
                        chart[(sym_cnt, sym)] = []
                    if len(chart[(sym_cnt, sym)]) < n+100 or chart[(sym_cnt, sym)][-1] >= score:
                        chart[(sym_cnt, sym)].append(score)
                        chart[(sym_cnt, sym)].sort()
                        chart[(sym_cnt, sym)] = chart[(sym_cnt, sym)][0:n+100]
                        h.append((transition[1], curr[1]+self.transitions_by_state[curr[0]][transition], curr[2]+[(transition[2], transition[3])], sym_cnt, sym))
            if accepted:
                istr = [w[0] for w in curr[2]]
                ostr = [w[1] for w in curr[2]]
                while EPS in ostr:
                    ostr.remove(EPS)
                while EPS in istr:
                    istr.remove(EPS)
                paths.append((curr[1], istr, ostr))
            if len(paths) > n:
                break
        
        return paths

    def rm_epseps(self):
        """
        Remove eps:eps transitions.
        TO DO: complete removal. Only some eps:eps are removed currently.
        """
        orig_transitions = self.transitions.copy()
        to_delete = set() 
        for t in orig_transitions:
            if t[2] == EPS and t[3] == EPS:
                to_delete.add(t)
                for t2 in orig_transitions:
                    if t2[1] == t[0]:
                        self.add_transition(t2[0], t[1], t2[2], t2[3])
                        to_delete.add(t2)
        for t in to_delete:
            self.rm_transition(t)

    def print_transitions(self):
        print(self.initial)
        print(self.final)
        for t in self.transitions:
            print(t, self.transitions[t])

    def save(self, fname):
        pickle.dump(self, open(fname, 'wb'))

def load(fname):
    f = pickle.load(open(fname, 'rb'))
    return f

def inverted(origf):
    """
    Create an inverted FST from another FST.
    """
    newf = FST()
    newf.initial = origf.initial
    newf.final = origf.final.copy()
    for t in origf.transitions:
        newf.add_transition(t[0], t[1], t[3], t[2], origf.transitions[t])

    return newf

def compose(f, g, prune=False):
    """
    Compose two FSTs, f and g.
    """

    def get_states(m):
        states = set()
        from_states = set()
        to_states = set()
        for t in m.transitions:
            if t[0] in m.rm or t[1] in m.rm:
                continue
            from_states.add(t[0])
            to_states.add(t[1])
        return from_states, to_states

    def remove_state(c, st):
        c.rm[st] = True
                    
    frst, tost = get_states(f)
    fstates = frst.union(tost)
    frst, tost = get_states(g)
    gstates = frst.union(tost)
    
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
                if t1[0] in f.rm or t1[1] in f.rm:
                    continue
                for t2 in gtrans:
                    if t2[0] in g.rm or t2[1] in g.rm:
                        continue
                    c.add_transition((t1[0], t2[0]),
                                     (t1[1], t2[1]),
                                     t1[2], t2[3],
                                     ftrans[t1] + gtrans[t2])

    if EPS in f.transitions_by_osym:
        ftrans = f.transitions_by_osym[EPS]
        for t1 in ftrans:
            if t1[0] in f.rm or t1[1] in f.rm:
                    continue
            for st2 in gstates:
                if st2 in g.rm:
                    continue
                c.add_transition((t1[0], st2),
                                  (t1[1], st2),
                                  t1[2], EPS, ftrans[t1])

    if EPS in g.transitions_by_isym:
        gtrans = g.transitions_by_isym[EPS]
        for t2 in gtrans:
            if t2[0] in g.rm or t2[1] in g.rm:
                continue
            for st1 in fstates:
                if st1 in f.rm:
                    continue
                c.add_transition((st1, t2[0]),
                                  (st1, t2[1]),
                                  EPS, t2[3], gtrans[t2])

    #if not prune:
    #    return c
    
    print("rm sink")
    # remove sink states

    removed = {}
    while True:
        sink = False
        frst, tost = get_states(c)
        for st in tost:
            if st in c.final:
                continue
            if st not in frst and st not in removed:
                #print("removed to state:", st)
                remove_state(c, st)
                removed[st] = True
                sink = True
        if not sink:
            break
    print("done")
    
    print("rm unreachable")
    # remove unreachable states
    # print('got states')
    removed = {}
    while True:
        unreachable = False
        frst, tost = get_states(c)
        for st in frst:
            if st == c.initial:
                continue
            if st not in tost and st not in removed:
                #print("removed from state:", st)
                remove_state(c, st)
                removed[st] = True
                unreachable = True
        if not unreachable:
            break
    print('Done')

    for t in c.transitions.copy():
        if t[0] in c.rm or t[1] in c.rm:
            c.rm_transition(t)

    frst, tost = get_states(c)
    for s in c.transitions_by_state.copy():
        if s not in frst and s not in tost:
            del c.transitions_by_state[s]  

    print(len(c.transitions), len(c.transitions_by_state))
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

