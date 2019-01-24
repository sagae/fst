#!/usr/bin/env python3

import fst
import math
import sys

bigram_cnt = {}
unigram_cnt = {'<s>': 0}
cnt = 0

if len(sys.argv) != 3:
    print("Usage:", sys.argv[0], "input_file output_file")
    sys.exit(1)

print("Building character LM...")
with open(sys.argv[1], 'r') as fp:
    for line in fp:
        for token in line.split():
            prev = '<s>'
            unigram_cnt[prev] += 1
            for ch in list(token) + ['</s>']:
                cnt += 1
                if ch in unigram_cnt:
                    unigram_cnt[ch] += 1
                else:
                    unigram_cnt[ch] = 1
                if (ch, prev) in bigram_cnt:
                    bigram_cnt[(ch, prev)] += 1
                else:
                    bigram_cnt[(ch, prev)] = 1
                prev = ch

lm = fst.FST()
lm.set_initial('<s>')
lm.set_final('</s>')

for w, pw in bigram_cnt:
    if not w == '</s>':
        lm.add_transition(pw, w, w, w, -1 * math.log(bigram_cnt[(w, pw)]/unigram_cnt[pw]))
    else:
        lm.add_transition(pw, w, fst.EPS, fst.EPS, -1 * math.log(bigram_cnt[(w, pw)]/unigram_cnt[pw]))

print("Done")

lm.save(sys.argv[2])
