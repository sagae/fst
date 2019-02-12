#!/usr/bin/env python3

import fst
import re
import sys

if len(sys.argv) != 4:
    print('Usage:', sys.argv[0], 'vocab word2arpabet_FST arpabet2word_FST')
    sys.exit()

# initialize the arpabet to word FST
p2w = fst.FST()
p2w.set_initial(1)
p2w.set_final(1)

# initilize the word to arpabet FST
w2p = fst.FST()
w2p.set_initial(1)
w2p.set_final(1)

p2w_state_id = 2
w2p_state_id = 2

# get the vocabulary
fd = {}
with open(sys.argv[1], 'r', encoding='utf-8') as fp:
    for line in fp:
        toks = line.split()
        if int(toks[0]) > 1:
            fd[toks[1]] = int(toks[0])

# go through each entry in the CMU Pronunciation Dictionary
with open('cmudict.0.7a_SPHINX_40', 'r', encoding='utf-8') as fp:
    for line in fp:

        line = line.lower()
        if re.match('^[a-z]', line):
            toks = line.split()
            word = re.sub('\([0-9]+\)$', '', toks.pop(0))

            if word not in fd:
                continue

            toks2 = toks.copy()

            # build the word to arpabet FST
            from_st = 1
            to_st = 1
            first_sym = toks.pop(0)
            last_sym = None
            if len(toks) > 0:
                to_st = w2p_state_id
                w2p_state_id += 1
                last_sym = toks.pop(-1)
            w2p.add_transition(from_st, to_st, word, first_sym)
            from_st = to_st
            for sym in toks:
                to_st = w2p_state_id
                w2p_state_id += 1
                w2p.add_transition(from_st, to_st, fst.EPS, sym)
                from_st = to_st
            if last_sym is not None:
                w2p.add_transition(from_st, 1, fst.EPS, last_sym)
    
            # build the arpabet to word FST
            last_sym = toks2.pop()
            from_st = 1
            to_st = 1
            
            for sym in toks2:
                to_st = p2w_state_id
                p2w.add_transition(from_st, to_st, sym, fst.EPS)
                from_st = to_st
                p2w_state_id += 1

            p2w.add_transition(from_st, 1, last_sym, word)

print('done')
w2p.save(sys.argv[2])
p2w.save(sys.argv[3])
