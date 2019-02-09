#!/usr/bin/env python3

import fst
import math
import sys

if len(sys.argv) == 4:
    vocabsize = int(sys.argv[3])
elif len(sys.argv) != 3:
    print("Usage:", sys.argv[0], "input_file output_file [vocabsize]")
    sys.exit(1)
else:
    vocabsize = 0

w_bigram_cnt = {}
w_unigram_cnt = {'<s>': 0}
wb_lambda = {}
w_cnt = 0

print("Building LM...")
with open(sys.argv[1], 'r', encoding='utf-8') as fp:
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

if vocabsize > 0:
    unk_cnt = 0
    types = sorted(w_unigram_cnt.items(), key=lambda a: a[1], reverse=True)
    for word, cnt in types[vocabsize:]:
        unk_cnt += cnt

w_unigram_cnt = dict(types[:vocabsize])
w_unigram_cnt['<unk>'] = unk_cnt

for (word, prev), cnt in list(w_bigram_cnt.items()):
    rm = False
    newword = word
    newprev = prev
    if word not in w_unigram_cnt:
        newword = '<unk>'
        rm = True
    if prev not in w_unigram_cnt:
        newprev = '<unk>'
        rm = True
    if (newword, newprev) not in w_bigram_cnt:
        w_bigram_cnt[(newword, newprev)] = 0
    if rm:
        del w_bigram_cnt[(word, prev)]
    w_bigram_cnt[(newword, newprev)] += cnt

for word in w_unigram_cnt:
    b = [nw for (nw, w) in w_bigram_cnt if w == word]
    wb_lambda[word] = len(b)/(len(b)+w_unigram_cnt[word])

wlm = fst.FST()
wlm.set_initial('<s>')
wlm.set_final('</s>')

for w, pw in w_bigram_cnt:
    bigram_p = wb_lambda[w] * w_bigram_cnt[(w, pw)]/w_unigram_cnt[pw]
    unigram_p = (1 - wb_lambda[w]) * w_unigram_cnt[w]/w_cnt
    logp = -1 * math.log(bigram_p + unigram_p)

    if not w == '</s>':
        wlm.add_transition(pw, w, w, w, logp)
    else:
        wlm.add_transition(pw, w, fst.EPS, fst.EPS, logp)
    
for w in w_unigram_cnt:
    unigram_p = w_unigram_cnt[w]/w_cnt
    logp = -1 * math.log(unigram_p)
    wlm.add_transition(w, '<unigram_state>', fst.EPS, fst.EPS, 0)
    wlm.add_transition('<unigram_state>', w, w, w, logp)
    
print("Done")

wlm.save(sys.argv[2])
