#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  I m p o r t s

import os, sys
import unicodedata

#  C l a s s e s

class KW(object):

    def __init__(self):
        self._single = { }
        self._double = { }
        self._triple = { }

    def parse(self, words):
        back1 = back2 = None
        for word in words:
            word = word.lower()
            self._update(self._single, word)
            if back1 is not None:
                phrase = back1 + ' ' + word
                self._update(self._double, phrase)
            if back2 is not None:
                phrase = back2 + ' ' + phrase
                self._update(self._triple, phrase)
            back2 = back1
            back1 = word

    def _update(self, d, w):
        if w in d:
            d[w] += 1
        else:
            d[w] = 1

    @property
    def single(self):
        return self._single

    @property
    def double(self):
        return self._double

    @property
    def triple(self):
        return self._triple
