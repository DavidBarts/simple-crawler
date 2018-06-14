#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  I m p o r t s

import os, sys
import unicodedata

#  C l a s s e s

class WordParser(object):

    _INWORD = set(["Lu", "Ll", "Lt", "Lm", "Lo", "Mn", "Mc"])
    _RAPOS = "'’"
    _APOS = set([x for x in _RAPOS])

    def parse(self, text):
        global _accum, _waccum, _state
        self._accum = [ ]
        self._waccum = ''
        self._state = self._out
        for ch in text:
            self._state(ch)
        self._addword()
        return self._accum

    def _inword(self, ch):
        return ch in self._APOS or unicodedata.category(ch) in self._INWORD

    def _addword(self):
        scrubbed = self._waccum.strip(self._RAPOS)
        self._waccum = ''
        if scrubbed != '':
            self._accum.append(scrubbed)

    def _out(self, ch):
        if self._inword(ch):
            self._waccum = ch
            self._state = self._in

    def _in(self, ch):
        if self._inword(ch):
            self._waccum += ch
        else:
            self._addword()
            self._state = self._out
