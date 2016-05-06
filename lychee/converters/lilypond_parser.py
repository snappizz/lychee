#!/usr/bin/env python
# -*- coding: utf-8 -*-

# CAVEAT UTILITOR
#
# This file was automatically generated by Grako.
#
#    https://pypi.python.org/pypi/grako/
#
# Any changes you make to it will be overwritten the next time
# the file is generated.


from __future__ import print_function, division, absolute_import, unicode_literals

from grako.parsing import graken, Parser
from grako.util import re, RE_FLAGS, generic_main  # noqa


__version__ = (2016, 5, 6, 2, 48, 49, 4)

__all__ = [
    'LilyPondParser',
    'LilyPondSemantics',
    'main'
]

KEYWORDS = set([])


class LilyPondParser(Parser):
    def __init__(self,
                 whitespace=None,
                 nameguard=None,
                 comments_re='\\%\\{.*?\\%\\}',
                 eol_comments_re=None,
                 ignorecase=None,
                 left_recursion=True,
                 keywords=KEYWORDS,
                 **kwargs):
        super(LilyPondParser, self).__init__(
            whitespace=whitespace,
            nameguard=nameguard,
            comments_re=comments_re,
            eol_comments_re=eol_comments_re,
            ignorecase=ignorecase,
            left_recursion=left_recursion,
            keywords=keywords,
            **kwargs
        )

    @graken()
    def _start_(self):
        with self._choice():
            with self._option():
                self._score_()
            with self._option():
                self._staff_()
            self._error('no available options')

    @graken()
    def _version_stmt_(self):
        self._token('\\version')
        self._token('"')

        def sep1():
            self._token('.')

        def block1():
            self._pattern(r'[0-9]*')
        self._positive_closure(block1, prefix=sep1)
        self.name_last_node('@')
        self._token('"')

    @graken()
    def _instr_name_(self):
        self._constant('instr_name')
        self.name_last_node('ly_type')
        self._token('\\set')
        self._token('Staff.instrumentName')
        self._token('=')
        self._token('"')
        self._pattern(r'[A-Z a-z]*')
        self.name_last_node('instrument_name')
        self._token('"')

        self.ast._define(
            ['ly_type', 'instrument_name'],
            []
        )

    @graken()
    def _clef_(self):
        self._constant('clef')
        self.name_last_node('ly_type')
        self._token('\\clef')
        self._token('"')
        with self._group():
            with self._choice():
                with self._option():
                    self._token('bass')
                with self._option():
                    self._token('tenor')
                with self._option():
                    self._token('alto')
                with self._option():
                    self._token('treble')
                self._error('expecting one of: alto bass tenor treble')
        self.name_last_node('type')
        self._token('"')

        self.ast._define(
            ['ly_type', 'type'],
            []
        )

    @graken()
    def _key_(self):
        self._constant('key')
        self.name_last_node('ly_type')
        self._token('\\key')
        self._note_name_()
        self.name_last_node('keynote')
        with self._optional():
            self._accidental_symbol_()
            self.name_last_node('accid')
        self._token('\\')
        with self._group():
            with self._choice():
                with self._option():
                    self._token('major')
                with self._option():
                    self._token('minor')
                self._error('expecting one of: major minor')
        self.name_last_node('mode')

        self.ast._define(
            ['ly_type', 'keynote', 'accid', 'mode'],
            []
        )

    @graken()
    def _time_numerator_(self):
        self._pattern(r'[1-9][0-9]?')

    @graken()
    def _time_(self):
        self._constant('time')
        self.name_last_node('ly_type')
        self._token('\\time')
        self._time_numerator_()
        self.name_last_node('count')
        self._token('/')
        self._duration_number_()
        self.name_last_node('unit')

        self.ast._define(
            ['ly_type', 'count', 'unit'],
            []
        )

    @graken()
    def _staff_setting_(self):
        with self._choice():
            with self._option():
                self._clef_()
            with self._option():
                self._key_()
            with self._option():
                self._time_()
            with self._option():
                self._instr_name_()
            self._error('no available options')

    @graken()
    def _note_name_(self):
        with self._choice():
            with self._option():
                self._pattern(r'a')
            with self._option():
                self._pattern(r'b')
            with self._option():
                self._pattern(r'c')
            with self._option():
                self._pattern(r'd')
            with self._option():
                self._pattern(r'e')
            with self._option():
                self._pattern(r'f')
            with self._option():
                self._pattern(r'g')
            self._error('expecting one of: a b c d e f g')

    @graken()
    def _octave_(self):
        with self._choice():
            with self._option():
                self._token(',,')
            with self._option():
                self._token(',')
            with self._option():
                self._token("'''''")
            with self._option():
                self._token("''''")
            with self._option():
                self._token("'''")
            with self._option():
                self._token("''")
            with self._option():
                self._token("'")
            self._error("expecting one of: ' '' ''' '''' ''''' , ,,")

    @graken()
    def _accidental_symbol_(self):
        with self._choice():
            with self._option():
                self._pattern(r'is')
            with self._option():
                self._pattern(r'es')
            self._error('expecting one of: es is')

    @graken()
    def _accidental_(self):

        def block0():
            self._accidental_symbol_()
        self._positive_closure(block0)

    @graken()
    def _accidental_force_(self):
        with self._choice():
            with self._option():
                self._token('?')
            with self._option():
                self._token('!')
            self._error('expecting one of: ! ?')

    @graken()
    def _duration_number_(self):
        with self._choice():
            with self._option():
                self._token('512')
            with self._option():
                self._token('256')
            with self._option():
                self._token('128')
            with self._option():
                self._token('64')
            with self._option():
                self._token('32')
            with self._option():
                self._token('16')
            with self._option():
                self._token('8')
            with self._option():
                self._token('4')
            with self._option():
                self._token('2')
            with self._option():
                self._token('1')
            self._error('expecting one of: 1 128 16 2 256 32 4 512 64 8')

    @graken()
    def _duration_dots_(self):

        def block0():
            self._token('.')
        self._closure(block0)

    @graken()
    def _duration_(self):
        self._duration_number_()
        self.name_last_node('number')
        with self._optional():
            self._duration_dots_()
            self.name_last_node('dots')

        self.ast._define(
            ['number', 'dots'],
            []
        )

    @graken()
    def _note_(self):
        self._constant('note')
        self.name_last_node('ly_type')
        self._note_name_()
        self.name_last_node('note_name')
        with self._optional():
            self._accidental_()
            self.name_last_node('accidental')
        with self._optional():
            self._octave_()
            self.name_last_node('octave')
        with self._optional():
            self._accidental_force_()
            self.name_last_node('accidental_force')
        self._duration_()
        self.name_last_node('duration')

        self.ast._define(
            ['ly_type', 'note_name', 'accidental', 'octave', 'accidental_force', 'duration'],
            []
        )

    @graken()
    def _rest_(self):
        self._constant('rest')
        self.name_last_node('ly_type')
        self._pattern(r'r')
        self._duration_()
        self.name_last_node('duration')

        self.ast._define(
            ['ly_type', 'duration'],
            []
        )

    @graken()
    def _spacer_(self):
        self._constant('spacer')
        self.name_last_node('ly_type')
        self._pattern(r's')
        self._duration_()
        self.name_last_node('duration')

        self.ast._define(
            ['ly_type', 'duration'],
            []
        )

    @graken()
    def _node_(self):
        with self._choice():
            with self._option():
                self._note_()
            with self._option():
                self._rest_()
            with self._option():
                self._spacer_()
            with self._option():
                self._staff_setting_()
            self._error('no available options')

    @graken()
    def _nodes_(self):

        def block0():
            self._node_()
        self._positive_closure(block0)

    @graken()
    def _barcheck_(self):
        self._constant('barcheck')
        self.name_last_node('ly_type')
        self._token('|')

        self.ast._define(
            ['ly_type'],
            []
        )

    @graken()
    def _measure_(self):
        with self._group():
            self._nodes_()
            self._barcheck_()
        self.name_last_node('measure')

        self.ast._define(
            ['measure'],
            []
        )

    @graken()
    def _measures_(self):

        def block0():
            self._measure_()
        self._closure(block0)

    @graken()
    def _brace_l_(self):
        self._token('{')

    @graken()
    def _brace_r_(self):
        self._token('}')

    @graken()
    def _music_block_(self):
        self._brace_l_()
        self._measures_()
        self.name_last_node('measures')
        self._brace_r_()

        self.ast._define(
            ['measures'],
            []
        )

    @graken()
    def _token_new_(self):
        self._token('\\new')

    @graken()
    def _token_staff_(self):
        self._token('Staff')

    @graken()
    def _staff_(self):
        self._token_new_()
        self._token_staff_()
        self._music_block_()
        self.name_last_node('staff')

        self.ast._define(
            ['staff'],
            []
        )

    @graken()
    def _simul_l_(self):
        self._token('<<')

    @graken()
    def _simul_r_(self):
        self._token('>>')

    @graken()
    def _score_staff_content_(self):
        self._simul_l_()

        def block1():
            self._staff_()
        self._positive_closure(block1)
        self.name_last_node('@')
        self._simul_r_()

    @graken()
    def _layout_block_(self):
        self._token('\\layout')
        self._brace_l_()
        self._brace_r_()

    @graken()
    def _token_score_(self):
        self._token('\\score')

    @graken()
    def _score_(self):
        with self._optional():
            self._version_stmt_()
        self.name_last_node('version')
        self._token_score_()
        self._brace_l_()
        self._score_staff_content_()
        self.name_last_node('score')
        with self._optional():
            self._layout_block_()
            self.name_last_node('layout_block')
        self._brace_r_()

        self.ast._define(
            ['version', 'score', 'layout_block'],
            []
        )


class LilyPondSemantics(object):
    def start(self, ast):
        return ast

    def version_stmt(self, ast):
        return ast

    def instr_name(self, ast):
        return ast

    def clef(self, ast):
        return ast

    def key(self, ast):
        return ast

    def time_numerator(self, ast):
        return ast

    def time(self, ast):
        return ast

    def staff_setting(self, ast):
        return ast

    def note_name(self, ast):
        return ast

    def octave(self, ast):
        return ast

    def accidental_symbol(self, ast):
        return ast

    def accidental(self, ast):
        return ast

    def accidental_force(self, ast):
        return ast

    def duration_number(self, ast):
        return ast

    def duration_dots(self, ast):
        return ast

    def duration(self, ast):
        return ast

    def note(self, ast):
        return ast

    def rest(self, ast):
        return ast

    def spacer(self, ast):
        return ast

    def node(self, ast):
        return ast

    def nodes(self, ast):
        return ast

    def barcheck(self, ast):
        return ast

    def measure(self, ast):
        return ast

    def measures(self, ast):
        return ast

    def brace_l(self, ast):
        return ast

    def brace_r(self, ast):
        return ast

    def music_block(self, ast):
        return ast

    def token_new(self, ast):
        return ast

    def token_staff(self, ast):
        return ast

    def staff(self, ast):
        return ast

    def simul_l(self, ast):
        return ast

    def simul_r(self, ast):
        return ast

    def score_staff_content(self, ast):
        return ast

    def layout_block(self, ast):
        return ast

    def token_score(self, ast):
        return ast

    def score(self, ast):
        return ast


def main(
        filename,
        startrule,
        trace=False,
        whitespace=None,
        nameguard=None,
        comments_re='\\%\\{.*?\\%\\}',
        eol_comments_re=None,
        ignorecase=None,
        left_recursion=True,
        **kwargs):

    with open(filename) as f:
        text = f.read()
    whitespace = whitespace or None
    parser = LilyPondParser(parseinfo=False)
    ast = parser.parse(
        text,
        startrule,
        filename=filename,
        trace=trace,
        whitespace=whitespace,
        nameguard=nameguard,
        ignorecase=ignorecase,
        **kwargs)
    return ast

if __name__ == '__main__':
    import json
    ast = generic_main(main, LilyPondParser, name='LilyPond')
    print('AST:')
    print(ast)
    print()
    print('JSON:')
    print(json.dumps(ast, indent=2))
    print()
