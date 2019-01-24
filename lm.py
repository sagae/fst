#!/usr/bin/env python3

import fst
import math
import sys

if len(sys.argv) != 3:
    print("Usage:", sys.argv[0], "input_file output_file")
    sys.exit(1)

w_bigram_cnt = {}
w_unigram_cnt = {'<s>': 0}
w_cnt = 0

print("Building LM...")
with open(sys.argv[1], 'r') as fp:
    for line in fp:
        prev = '<s>'
        w_unigram_cnt[prev] += 1
        sent = line.split() + ['</s>']
        while '.' in sent:
            sent.remove('.')
        for token in line.split() + ['</s>']:
            w_cnt += 1
            if token in w_unigram_cnt:
                w_unigram_cnt[token] += 1
            else:
                w_unigram_cnt[token] = 1
            if (token, prev) in w_bigram_cnt:
                w_bigram_cnt[(token, prev)] += 1
            else:
                w_bigram_cnt[(token, prev)] = 1
            prev = token

wlm = fst.FST()
wlm.set_initial('<s>')
wlm.set_final('</s>')

for w, pw in w_bigram_cnt:
    if not w == '</s>':
        wlm.add_transition(pw, w, w, w, -1 * math.log(w_bigram_cnt[(w, pw)]/w_unigram_cnt[pw]))
    else:
        wlm.add_transition(pw, w, fst.EPS, fst.EPS, -1 * math.log(w_bigram_cnt[(w, pw)]/w_unigram_cnt[pw]))

print("Done")

wlm.save(sys.argv[2])
