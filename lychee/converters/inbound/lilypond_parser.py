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

from grako.buffering import Buffer
from grako.parsing import graken, Parser
from grako.util import re, RE_FLAGS, generic_main  # noqa


__version__ = (2017, 5, 15, 1, 45, 4, 0)

__all__ = [
    'LilyPondParser',
    'LilyPondSemantics',
    'main'
]

KEYWORDS = set([])


class LilyPondBuffer(Buffer):
    def __init__(self,
                 text,
                 whitespace=None,
                 nameguard=None,
                 comments_re='\\%\\{.*?\\%\\}',
                 eol_comments_re=None,
                 ignorecase=None,
                 namechars='',
                 **kwargs):
        super(LilyPondBuffer, self).__init__(
            text,
            whitespace=whitespace,
            nameguard=nameguard,
            comments_re=comments_re,
            eol_comments_re=eol_comments_re,
            ignorecase=ignorecase,
            namechars=namechars,
            **kwargs
        )


class LilyPondParser(Parser):
    def __init__(self,
                 whitespace=None,
                 nameguard=None,
                 comments_re='\\%\\{.*?\\%\\}',
                 eol_comments_re=None,
                 ignorecase=None,
                 left_recursion=False,
                 parseinfo=False,
                 keywords=KEYWORDS,
                 namechars='',
                 **kwargs):
        super(LilyPondParser, self).__init__(
            whitespace=whitespace,
            nameguard=nameguard,
            comments_re=comments_re,
            eol_comments_re=eol_comments_re,
            ignorecase=ignorecase,
            left_recursion=left_recursion,
            parseinfo=parseinfo,
            keywords=keywords,
            namechars=namechars,
            **kwargs
        )

    def parse(self, text, *args, **kwargs):
        if not isinstance(text, Buffer):
            text = LilyPondBuffer(text, **kwargs)
        return super(LilyPondParser, self).parse(text, *args, **kwargs)

    @graken()
    def _start_(self):

        def block0():
            self._top_level_expression_()
        self._closure(block0)

    @graken()
    def _version_statement_(self):
        self._constant('version')
        self.name_last_node('ly_type')
        self._token('\\version')
        self._token('"')

        def sep2():
            self._token('.')

        def block2():
            self._pattern(r'[0-9]*')
        self._closure(block2, sep=sep2)
        self.name_last_node('version')
        self._token('"')
        self.ast._define(
            ['ly_type', 'version'],
            []
        )

    @graken()
    def _language_statement_(self):
        self._constant('language')
        self.name_last_node('ly_type')
        self._token('\\language')
        self._token('"')
        self._pattern(r'[^"]*')
        self.name_last_node('language')
        self._token('"')
        self.ast._define(
            ['language', 'ly_type'],
            []
        )

    @graken()
    def _instr_name_(self):
        self._constant('instr_name')
        self.name_last_node('ly_type')
        self._token('\\set')
        self._token('Staff.instrumentName')
        self._cut()
        self._token('=')
        self._token('"')
        self._pattern(r'[A-Z a-z0-9&]*')
        self.name_last_node('name')
        self._token('"')
        self.ast._define(
            ['ly_type', 'name'],
            []
        )

    @graken()
    def _clef_(self):
        self._constant('clef')
        self.name_last_node('ly_type')
        self._token('\\clef')
        self._cut()
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
        self._cut()
        self._pitch_name_()
        self.name_last_node('keynote')
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
            ['keynote', 'ly_type', 'mode'],
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
        self._cut()
        self._time_numerator_()
        self.name_last_node('count')
        self._token('/')
        self._duration_number_()
        self.name_last_node('unit')
        self.ast._define(
            ['count', 'ly_type', 'unit'],
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
    def _pitch_name_(self):
        with self._choice():
            with self._option():
                self._pattern(r'[a-z]{2,}')
            with self._option():
                self._pattern(r'[a-pt-z]')
            self._error('expecting one of: [a-pt-z] [a-z]{2,}')

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
        with self._choice():
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')

                    def block1():
                        self._duration_dots_()
                        self.name_last_node('dots')
                    self._positive_closure(block1)
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            with self._option():
                with self._group():
                    pass
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            self._error('no available options')
        self.ast._define(
            ['dots', 'dur'],
            []
        )

    @graken()
    def _tie_(self):
        self._constant('tie')
        self.name_last_node('ly_type')
        self._token('~')
        self.ast._define(
            ['ly_type'],
            []
        )

    @graken()
    def _slur_(self):
        self._constant('slur')
        self.name_last_node('ly_type')
        with self._group():
            with self._choice():
                with self._option():
                    self._token('(')
                with self._option():
                    self._token(')')
                self._error('expecting one of: ( )')
        self.name_last_node('slur')
        self.ast._define(
            ['ly_type', 'slur'],
            []
        )

    @graken()
    def _post_event_(self):
        with self._choice():
            with self._option():
                self._tie_()
            with self._option():
                self._slur_()
            self._error('no available options')

    @graken()
    def _notehead_(self):
        self._pitch_name_()
        self.name_last_node('pitch_name')
        self._cut()
        with self._optional():
            self._octave_()
            self.name_last_node('oct')
        with self._optional():
            self._accidental_force_()
            self.name_last_node('accid_force')
        self.ast._define(
            ['accid_force', 'oct', 'pitch_name'],
            []
        )

    @graken()
    def _note_(self):
        self._constant('note')
        self.name_last_node('ly_type')
        self._pitch_name_()
        self.name_last_node('pitch_name')
        self._cut()
        with self._optional():
            self._octave_()
            self.name_last_node('oct')
        with self._optional():
            self._accidental_force_()
            self.name_last_node('accid_force')

        with self._choice():
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')

                    def block5():
                        self._duration_dots_()
                        self.name_last_node('dots')
                    self._positive_closure(block5)
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            with self._option():
                with self._group():
                    pass
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            self._error('no available options')


        def block13():
            self._post_event_()
        self._closure(block13)
        self.name_last_node('post_events')
        self.ast._define(
            ['accid_force', 'dots', 'dur', 'ly_type', 'oct', 'pitch_name', 'post_events'],
            []
        )

    @graken()
    def _chord_note_(self):
        self._pitch_name_()
        self.name_last_node('pitch_name')
        self._cut()
        with self._optional():
            self._octave_()
            self.name_last_node('oct')
        with self._optional():
            self._accidental_force_()
            self.name_last_node('accid_force')


        def block4():
            self._post_event_()
        self._closure(block4)
        self.name_last_node('post_events')
        self.ast._define(
            ['accid_force', 'oct', 'pitch_name', 'post_events'],
            []
        )

    @graken()
    def _chord_(self):
        self._constant('chord')
        self.name_last_node('ly_type')
        self._token('<')
        with self._ifnot():
            self._token('<')

        def block2():
            self._chord_note_()
        self._closure(block2)
        self.name_last_node('notes')
        self._token('>')
        with self._choice():
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')

                    def block4():
                        self._duration_dots_()
                        self.name_last_node('dots')
                    self._positive_closure(block4)
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            with self._option():
                with self._group():
                    pass
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            self._error('no available options')


        def block12():
            self._post_event_()
        self._closure(block12)
        self.name_last_node('post_events')
        self.ast._define(
            ['dots', 'dur', 'ly_type', 'notes', 'post_events'],
            []
        )

    @graken()
    def _rest_(self):
        self._constant('rest')
        self.name_last_node('ly_type')
        self._pattern(r'r')
        with self._choice():
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')

                    def block2():
                        self._duration_dots_()
                        self.name_last_node('dots')
                    self._positive_closure(block2)
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            with self._option():
                with self._group():
                    pass
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            self._error('no available options')


        def block10():
            self._post_event_()
        self._closure(block10)
        self.name_last_node('post_events')
        self.ast._define(
            ['dots', 'dur', 'ly_type', 'post_events'],
            []
        )

    @graken()
    def _measure_rest_(self):
        self._constant('measure_rest')
        self.name_last_node('ly_type')
        self._pattern(r'R')
        with self._choice():
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')

                    def block2():
                        self._duration_dots_()
                        self.name_last_node('dots')
                    self._positive_closure(block2)
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            with self._option():
                with self._group():
                    pass
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            self._error('no available options')


        def block10():
            self._post_event_()
        self._closure(block10)
        self.name_last_node('post_events')
        self.ast._define(
            ['dots', 'dur', 'ly_type', 'post_events'],
            []
        )

    @graken()
    def _spacer_(self):
        self._constant('spacer')
        self.name_last_node('ly_type')
        self._pattern(r's')
        with self._choice():
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')

                    def block2():
                        self._duration_dots_()
                        self.name_last_node('dots')
                    self._positive_closure(block2)
            with self._option():
                with self._group():
                    self._duration_number_()
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            with self._option():
                with self._group():
                    pass
                    self.name_last_node('dur')
                    self._empty_closure()
                    self.name_last_node('dots')
            self._error('no available options')


        def block10():
            self._post_event_()
        self._closure(block10)
        self.name_last_node('post_events')
        self.ast._define(
            ['dots', 'dur', 'ly_type', 'post_events'],
            []
        )

    @graken()
    def _node_(self):
        with self._choice():
            with self._option():
                self._rest_()
            with self._option():
                self._spacer_()
            with self._option():
                self._note_()
            with self._option():
                self._measure_rest_()
            with self._option():
                self._chord_()
            with self._option():
                self._staff_setting_()
            self._error('no available options')

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
    def _music_node_(self):
        with self._choice():
            with self._option():
                self._rest_()
            with self._option():
                self._spacer_()
            with self._option():
                self._note_()
            with self._option():
                self._chord_()
            self._error('no available options')

    @graken()
    def _nodes_(self):

        def block0():
            with self._choice():
                with self._option():
                    with self._choice():
                        with self._option():
                            self._rest_()
                        with self._option():
                            self._spacer_()
                        with self._option():
                            self._note_()
                        with self._option():
                            self._chord_()
                        self._error('no available options')
                with self._option():
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
                with self._option():
                    self._barcheck_()
                self._error('no available options')
        self._positive_closure(block0)

    @graken()
    def _unmarked_layer_(self):
        self._nodes_()

    @graken()
    def _marked_layer_(self):
        self._token('{')
        self._nodes_()
        self.name_last_node('@')
        self._token('}')

    @graken()
    def _monophonic_layers_(self):
        self._unmarked_layer_()
        self.add_last_node_to_name('layers')
        self.ast._define(
            [],
            ['layers']
        )

    @graken()
    def _polyphonic_layers_(self):
        self._simul_l_()
        with self._group():

            def sep1():
                self._token('\\\\')

            def block1():
                self._marked_layer_()
            self._closure(block1, sep=sep1)
        self.name_last_node('layers')
        self._simul_r_()
        self.ast._define(
            ['layers'],
            []
        )

    @graken()
    def _brace_l_(self):
        self._token('{')

    @graken()
    def _brace_r_(self):
        self._token('}')

    @graken()
    def _staff_content_(self):

        def block1():
            self._staff_setting_()
        self._closure(block1)
        self.name_last_node('initial_settings')

        def block3():
            with self._group():
                with self._choice():
                    with self._option():
                        self._monophonic_layers_()
                    with self._option():
                        self._polyphonic_layers_()
                    self._error('no available options')
        self._positive_closure(block3)
        self.name_last_node('content')
        self.ast._define(
            ['content', 'initial_settings'],
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
        self._constant('staff')
        self.name_last_node('ly_type')
        self._token_new_()
        self._token_staff_()
        self._brace_l_()

        def block2():
            self._staff_setting_()
        self._closure(block2)
        self.name_last_node('initial_settings')

        def block4():
            with self._group():
                with self._choice():
                    with self._option():
                        self._monophonic_layers_()
                    with self._option():
                        self._polyphonic_layers_()
                    self._error('no available options')
        self._positive_closure(block4)
        self.name_last_node('content')

        self._brace_r_()
        self.ast._define(
            ['content', 'initial_settings', 'ly_type'],
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
        self._cut()

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
        with self._choice():
            with self._option():
                self._token('\\score')
            with self._option():
                self._token('\\new')
                self._token('Score')
            self._error('expecting one of: \\new \\score')

    @graken()
    def _score_(self):
        self._constant('score')
        self.name_last_node('ly_type')
        with self._optional():
            self._version_statement_()
        self.name_last_node('version')
        self._token_score_()
        with self._group():
            with self._choice():
                with self._option():
                    self._brace_l_()
                    self._score_staff_content_()
                    self.name_last_node('staves')
                    with self._optional():
                        self._layout_block_()
                        self.name_last_node('layout_block')
                    self._brace_r_()
                with self._option():
                    self._score_staff_content_()
                    self.name_last_node('staves')
                self._error('no available options')
        self.ast._define(
            ['layout_block', 'ly_type', 'staves', 'version'],
            []
        )

    @graken()
    def _top_level_expression_(self):
        with self._choice():
            with self._option():
                self._version_statement_()
            with self._option():
                self._language_statement_()
            with self._option():
                self._score_()
            with self._option():
                self._staff_()
            self._error('no available options')


class LilyPondSemantics(object):
    def start(self, ast):
        return ast

    def version_statement(self, ast):
        return ast

    def language_statement(self, ast):
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

    def pitch_name(self, ast):
        return ast

    def octave(self, ast):
        return ast

    def accidental_force(self, ast):
        return ast

    def duration_number(self, ast):
        return ast

    def duration_dots(self, ast):
        return ast

    def duration(self, ast):
        return ast

    def tie(self, ast):
        return ast

    def slur(self, ast):
        return ast

    def post_event(self, ast):
        return ast

    def notehead(self, ast):
        return ast

    def note(self, ast):
        return ast

    def chord_note(self, ast):
        return ast

    def chord(self, ast):
        return ast

    def rest(self, ast):
        return ast

    def measure_rest(self, ast):
        return ast

    def spacer(self, ast):
        return ast

    def node(self, ast):
        return ast

    def barcheck(self, ast):
        return ast

    def music_node(self, ast):
        return ast

    def nodes(self, ast):
        return ast

    def unmarked_layer(self, ast):
        return ast

    def marked_layer(self, ast):
        return ast

    def monophonic_layers(self, ast):
        return ast

    def polyphonic_layers(self, ast):
        return ast

    def brace_l(self, ast):
        return ast

    def brace_r(self, ast):
        return ast

    def staff_content(self, ast):
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

    def top_level_expression(self, ast):
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
        left_recursion=False,
        parseinfo=False,
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
