#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/tests/test_lilypond_parser.py
# Purpose:                Tests for the "lilypond_parser" module.
#
# Copyright (C) 2016 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
Tests for the "lilypond_parser" module.

The tests in this file are only for the parser, not the translator. In other words, these tests are
for the code generated by Grako from the "lilypond.ebnf" file, and not for the code that translates
the Grako-parsed data into Lychee-MEI. (Yes, of course, what we actually need to test is the grammar,
not the generated code, but we can't very well do that, can we?)
"""

from __future__ import unicode_literals

from grako.exceptions import FailedLookahead, FailedParse
import pytest

from lychee.converters.inbound import lilypond_parser


parser = lilypond_parser.LilyPondParser()



class TestNotehead(object):
    """
    For the "notehead" rule and its subrules.
    """

    def test_notehead_1(self):
        """With a valid pitch name."""
        content = 'a'
        expected = {'pname': 'a', 'accid': [], 'oct': None, 'accid_force': None}
        actual = parser.parse(content, rule_name='notehead')
        assert expected == actual

    def test_notehead_2(self):
        """With an invalid pitch name."""
        content = 'Q'
        with pytest.raises(FailedParse):
            parser.parse(content, rule_name='notehead')

    def test_notehead_3(self):
        """One accidental"""
        content = 'bes'
        expected = {'pname': 'b', 'accid': ['es'], 'oct': None, 'accid_force': None}
        actual = parser.parse(content, rule_name='notehead')
        assert expected == actual

    def test_notehead_4(self):
        """Double accidental"""
        content = 'fisis'
        expected = {'pname': 'f', 'accid': ['is', 'is'], 'oct': None, 'accid_force': None}
        actual = parser.parse(content, rule_name='notehead')
        assert expected == actual

    def test_notehead_5(self):
        """Okay if the accidental doesn't make sense"""
        content = 'cesis'
        expected = {'pname': 'c', 'accid': ['es', 'is'], 'oct': None, 'accid_force': None}
        actual = parser.parse(content, rule_name='notehead')
        assert expected == actual

    def test_notehead_6(self):
        """
        But the accidental needs to have the right letters.
        NB: it doesn't fail because this rule by itself needn't consume all the text
        """
        content = 'am'
        expected = {'pname': 'a', 'accid': [], 'oct': None, 'accid_force': None}
        actual = parser.parse(content, rule_name='notehead')
        assert expected == dict(actual)

    def test_notehead_7(self):
        """With an octave."""
        content = 'des,'
        expected = {'pname': 'd', 'accid': ['es'], 'oct': ',', 'accid_force': None}
        actual = parser.parse(content, rule_name='notehead')
        assert expected == actual

    def test_notehead_8(self):
        """With ? forced accidental."""
        content = "eisis''?"
        expected = {'pname': 'e', 'accid': ['is', 'is'], 'oct': "''", 'accid_force': '?'}
        actual = parser.parse(content, rule_name='notehead')
        assert expected == actual

    def test_notehead_9(self):
        """With ! forced accidental."""
        content = 'gis,,!'
        expected = {'pname': 'g', 'accid': ['is'], 'oct': ',,', 'accid_force': '!'}
        actual = parser.parse(content, rule_name='notehead')
        assert expected == actual

    def test_notehead_10(self):
        """With an octave but no accidental."""
        content = 'a,'
        expected = {'pname': 'a', 'accid': [], 'oct': ',', 'accid_force': None}
        actual = parser.parse(content, rule_name='notehead')
        assert expected == actual

    def test_notehead_11(self):
        """With an octave, forced accidental, but no accidental."""
        content = 'b,?'
        expected = {'pname': 'b', 'accid': [], 'oct': ',', 'accid_force': '?'}
        actual = parser.parse(content, rule_name='notehead')
        assert expected == actual

    def test_notehead_12(self):
        """With a forced accidental but no octave or accidental."""
        content = 'c!'
        expected = {'pname': 'c', 'accid': [], 'oct': None, 'accid_force': '!'}
        actual = parser.parse(content, rule_name='notehead')
        assert expected == actual


class TestDuration(object):
    """
    For the "duration" rule.
    """

    def test_duration_1(self):
        """With a dur and no dots."""
        content = '4'
        expected = {'dur': '4', 'dots': []}
        actual = parser.parse(content, rule_name='duration')
        assert expected == actual

    def test_duration_2(self):
        """With a dur and two dots."""
        content = '256..'
        expected = {'dur': '256', 'dots': ['.', '.']}
        actual = parser.parse(content, rule_name='duration')
        assert expected == actual

    def test_duration_3(self):
        """
        With a dot but no dur.
        The rule consumes no input and causes a parse error elsewhere.
        """
        content = ''
        expected = {'dur': None, 'dots': []}
        actual = parser.parse(content, rule_name='duration')
        assert expected == actual

    def test_duration_4(self):
        """When it's all missing"""
        content = ''
        expected = {'dur': None, 'dots': []}
        actual = parser.parse(content, rule_name='duration')
        assert expected == actual


class TestNoteChordRestSpacer(object):
    """
    For---you guessed it---notes, chords, rests, and spacers. And the "music_node" rule that matches
    on any one of those.
    """

    def test_note_1(self):
        """Works as expected."""
        content = 'bes,!256..'
        expected = {'pname': 'b', 'accid': ['es'], 'oct': ',', 'accid_force': '!', 'dur': '256',
            'dots': ['.', '.'], 'ly_type': 'note', 'post_events': []}
        actual = parser.parse(content, rule_name='note')
        assert expected == actual

    def test_note_2(self):
        """
        Pitch and duration are in the wrong order.
        NB: it doesn't fail; the ! isn't consumed, and will cause a failure later
        """
        content = 'c4!'
        expected = {'pname': 'c', 'accid': [], 'oct': None, 'accid_force': None, 'dur': '4',
            'dots': [], 'ly_type': 'note', 'post_events': []}
        actual = parser.parse(content, rule_name='note')
        assert expected == actual

    def test_note_3(self):
        """Works without duration."""
        content = 'bes,'
        expected = {'pname': 'b', 'accid': ['es'], 'oct': ',', 'accid_force': None, 'dur': None,
            'dots': [], 'ly_type': 'note', 'post_events': []}
        actual = parser.parse(content, rule_name='note')
        assert expected == actual

    def test_chord_1(self):
        """Works as expected (two noteheads)."""
        content = '<bes,! ees,?>256..'
        expected = {
            'notes': [
                {'pname': 'b', 'accid': ['es'], 'oct': ',', 'accid_force': '!', 'post_events': []},
                {'pname': 'e', 'accid': ['es'], 'oct': ',', 'accid_force': '?', 'post_events': []},
            ],
            'dur': '256',
            'dots': ['.', '.'],
            'ly_type': 'chord',
            'post_events': []
        }
        actual = parser.parse(content, rule_name='chord')
        assert expected == actual

    def test_chord_2(self):
        """
        Works as expected (one notehead).
        NB: Why? Because it's valid for LilyPond and MEI.
        """
        content = '<bes,!>256..'
        expected = {
            'notes': [
                {'pname': 'b', 'accid': ['es'], 'oct': ',', 'accid_force': '!', 'post_events': []},
            ],
            'dur': '256',
            'dots': ['.', '.'],
            'ly_type': 'chord',
            'post_events': []
        }
        actual = parser.parse(content, rule_name='chord')
        assert expected == actual

    def test_chord_3(self):
        """
        Works as expected (no noteheads).
        NB: Why? Because it's valid for LilyPond and MEI.
        """
        content = '<>256..'
        expected = {
            'notes': [],
            'dur': '256',
            'dots': ['.', '.'],
            'ly_type': 'chord',
            'post_events': []
        }
        actual = parser.parse(content, rule_name='chord')
        assert expected == actual

    def test_chord_4(self):
        """With three noteheads and no duration."""
        content = "<bes,! ees,? g'>"
        expected = {
            'notes': [
                {'pname': 'b', 'accid': ['es'], 'oct': ',', 'accid_force': '!', 'post_events': []},
                {'pname': 'e', 'accid': ['es'], 'oct': ',', 'accid_force': '?', 'post_events': []},
                {'pname': 'g', 'accid': [], 'oct': "'", 'accid_force': None, 'post_events': []},
            ],
            'dur': None,
            'dots': [],
            'ly_type': 'chord',
            'post_events': []
        }
        actual = parser.parse(content, rule_name='chord')
        print(str(actual))
        assert expected == actual

    def test_chord_5(self):
        """
        With a "simultaneous" indicator, make sure it doesn't eat the first <
        """
        content = '<< { d4 } \\ { f4 } >>'
        with pytest.raises(FailedLookahead):
            parser.parse(content, rule_name='chord')

    def test_rest_1(self):
        """Works as expected."""
        content = 'r256..'
        expected = {'dur': '256', 'dots': ['.', '.'], 'ly_type': 'rest', 'post_events': []}
        actual = parser.parse(content, rule_name='rest')
        assert expected == actual

    def test_rest_2(self):
        """Works without duration."""
        content = 'r'
        expected = {'dur': None, 'dots': [], 'ly_type': 'rest', 'post_events': []}
        actual = parser.parse(content, rule_name='rest')
        assert expected == actual

    def test_spacer_1(self):
        """Works as expected."""
        content = 's256..'
        expected = {'dur': '256', 'dots': ['.', '.'], 'ly_type': 'spacer', 'post_events': []}
        actual = parser.parse(content, rule_name='spacer')
        assert expected == actual

    def test_spacer_2(self):
        """Works without duration."""
        content = 's'
        expected = {'dur': None, 'dots': [], 'ly_type': 'spacer', 'post_events': []}
        actual = parser.parse(content, rule_name='spacer')
        assert expected == actual

    def test_measure_rest_1(self):
        """Works as expected."""
        content = 'R256..'
        expected = {'dur': '256', 'dots': ['.', '.'], 'ly_type': 'measure_rest', 'post_events': []}
        actual = parser.parse(content, rule_name='measure_rest')
        assert expected == actual

    def test_measure_rest_2(self):
        """Works without duration."""
        content = 'R'
        expected = {'dur': None, 'dots': [], 'ly_type': 'measure_rest', 'post_events': []}
        actual = parser.parse(content, rule_name='measure_rest')
        assert expected == actual

    def test_music_node_1(self):
        """music_node: note"""
        content = 'bes,!256..'
        expected = {'pname': 'b', 'accid': ['es'], 'oct': ',', 'accid_force': '!', 'dur': '256',
            'dots': ['.', '.'], 'ly_type': 'note', 'post_events': []}
        actual = parser.parse(content, rule_name='music_node')
        assert expected == actual

    def test_music_node_2(self):
        """music_node: chord"""
        content = '<bes,! ees,?>256..'
        expected = {
            'notes': [
                {'pname': 'b', 'accid': ['es'], 'oct': ',', 'accid_force': '!', 'post_events': []},
                {'pname': 'e', 'accid': ['es'], 'oct': ',', 'accid_force': '?', 'post_events': []},
            ],
            'dur': '256',
            'dots': ['.', '.'],
            'ly_type': 'chord',
            'post_events': []
        }
        actual = parser.parse(content, rule_name='music_node')
        assert expected == actual

    def test_music_node_3(self):
        """music_node: rest"""
        content = 'r256..'
        expected = {'dur': '256', 'dots': ['.', '.'], 'ly_type': 'rest', 'post_events': []}
        actual = parser.parse(content, rule_name='music_node')
        assert expected == actual

    def test_music_node_4(self):
        """music_node: spacer"""
        content = 's256..'
        expected = {'dur': '256', 'dots': ['.', '.'], 'ly_type': 'spacer', 'post_events': []}
        actual = parser.parse(content, rule_name='music_node')
        assert expected == actual


class TestLayers(object):
    """
    For polyphonic and monophonic layers.
    """

    def test_unmarked_layer_1(self):
        """With one music node."""
        content = 's256..'
        expected = [{'dur': '256', 'dots': ['.', '.'], 'ly_type': 'spacer', 'post_events': []}]
        actual = parser.parse(content, rule_name='unmarked_layer')
        assert expected == actual

    def test_unmarked_layer_2(self):
        """With two music nodes."""
        content = 's2 s4'
        expected = [
            {'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
            {'dur': '4', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
        ]
        actual = parser.parse(content, rule_name='unmarked_layer')
        assert expected == actual

    def test_unmarked_layer_3(self):
        """With three music nodes, the second without a duration."""
        content = 's2 s s4.'
        expected = [
            {'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
            {'dur': None, 'dots': [], 'ly_type': 'spacer', 'post_events': []},
            {'dur': '4', 'dots': ['.'], 'ly_type': 'spacer', 'post_events': []},
        ]
        actual = parser.parse(content, rule_name='unmarked_layer')
        assert expected == actual

    def test_marked_layer_1(self):
        """With one music node."""
        content = '{s256..}'
        expected = [{'dur': '256', 'dots': ['.', '.'], 'ly_type': 'spacer', 'post_events': []}]
        actual = parser.parse(content, rule_name='marked_layer')
        assert expected == actual

    def test_marked_layer_2(self):
        """With two music nodes."""
        content = '{s2 s4}'
        expected = [
            {'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
            {'dur': '4', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
        ]
        actual = parser.parse(content, rule_name='marked_layer')
        assert expected == actual

    def test_marked_layer_3(self):
        """With three music nodes, the second without a duration."""
        content = '{s2 s s4.}'
        expected = [
            {'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
            {'dur': None, 'dots': [], 'ly_type': 'spacer', 'post_events': []},
            {'dur': '4', 'dots': ['.'], 'ly_type': 'spacer', 'post_events': []},
        ]
        actual = parser.parse(content, rule_name='marked_layer')
        assert expected == actual

    def test_monophonic_layers_1(self):
        """With three music nodes, the second without a duration."""
        content = 's2 s s4.'
        expected = {'layers': [[
            {'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
            {'dur': None, 'dots': [], 'ly_type': 'spacer', 'post_events': []},
            {'dur': '4', 'dots': ['.'], 'ly_type': 'spacer', 'post_events': []},
        ]]}
        actual = parser.parse(content, rule_name='monophonic_layers')
        assert expected == actual

    def test_polyphonic_layers_1(self):
        """With one Voice context."""
        content = '<< { s2 } >>'
        expected = {'layers': [
            [{'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},],
        ]}
        actual = parser.parse(content, rule_name='polyphonic_layers')
        assert expected == actual

    def test_polyphonic_layers_2(self):
        """With two Voice contexts."""
        content = r'<< { s2 } \\ { s4 s } >>'
        expected = {'layers': [
            [{'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},],
            [
                {'dur': '4', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
                {'dur': None, 'dots': [], 'ly_type': 'spacer', 'post_events': []},
            ],
        ]}
        actual = parser.parse(content, rule_name='polyphonic_layers')
        assert expected == actual

    def test_polyphonic_layers_3(self):
        """With three Voice contexts."""
        content = r'<< { s2 } \\ { s4 } \\ { s16 } >>'
        expected = {'layers': [
            [{'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},],
            [{'dur': '4', 'dots': [], 'ly_type': 'spacer', 'post_events': []},],
            [{'dur': '16', 'dots': [], 'ly_type': 'spacer', 'post_events': []},],
        ]}
        actual = parser.parse(content, rule_name='polyphonic_layers')
        assert expected == actual

    def test_polyphonic_layers_4(self):
        """With no Voice contexts."""
        content = '<< >>'
        expected = {'layers': []}
        actual = parser.parse(content, rule_name='polyphonic_layers')
        assert expected == actual


class TestVersionStatement(object):
    """
    For the \version statement.
    """

    def test_version_statement_1(self):
        """Given a real version, it does fine."""
        content = r'\version "2.18.0"'
        expected = ['2', '18', '0']
        actual = parser.parse(content, rule_name='version_stmt')
        assert expected == actual

    def test_version_statement_2(self):
        """LilyPond fills in the rest with zeroes."""
        content = r'\version "2"'
        expected = ['2']
        actual = parser.parse(content, rule_name='version_stmt')
        assert expected == actual

    def test_version_statement_3(self):
        """LilyPond doesn't mind this either."""
        content = r'\version ""'
        expected = ['']
        actual = parser.parse(content, rule_name='version_stmt')
        assert expected == actual

    def test_version_statement_4(self):
        """LilyPond doesn't mind this either."""
        content = r'\version "123.234.3.432444.52"'
        expected = ['123', '234', '3', '432444', '52']
        actual = parser.parse(content, rule_name='version_stmt')
        assert expected == actual


class TestStaffSettings(object):
    """
    For staff objects like instrument name, clef, and so on.
    """

    def test_instr_name_1(self):
        """Instrument name is one word."""
        content = r'\set Staff.instrumentName = "Clarinet"'
        expected = {'ly_type': 'instr_name', 'name': 'Clarinet'}
        actual = parser.parse(content, rule_name='instr_name')
        assert expected == actual

    def test_instr_name_2(self):
        """Instrument name is two words."""
        content = r'\set Staff.instrumentName = "Kazoos 3 & 4"'
        expected = {'ly_type': 'instr_name', 'name': 'Kazoos 3 & 4'}
        actual = parser.parse(content, rule_name='instr_name')
        assert expected == actual

    def test_clef_1(self):
        """Clef."""
        content = r'\clef "alto"'
        expected = {'ly_type': 'clef', 'type': 'alto'}
        actual = parser.parse(content, rule_name='clef')
        assert expected == actual

    def test_key_1(self):
        """Key, major without accidental."""
        content = r'\key f \major'
        expected = {'ly_type': 'key', 'keynote': 'f', 'accid': None, 'mode': 'major'}
        actual = parser.parse(content, rule_name='key')
        assert expected == actual

    def test_key_2(self):
        """Key, minor with accidental."""
        content = r'\key fis \minor'
        expected = {'ly_type': 'key', 'keynote': 'f', 'accid': 'is', 'mode': 'minor'}
        actual = parser.parse(content, rule_name='key')
        assert expected == actual

    def test_time_1(self):
        """Usual time signature."""
        content = r'\time 3/4'
        expected = {'ly_type': 'time', 'count': '3', 'unit': '4'}
        actual = parser.parse(content, rule_name='time')
        assert expected == actual

    def test_time_2(self):
        """Unusual time signature."""
        content = r'\time 46/128'
        expected = {'ly_type': 'time', 'count': '46', 'unit': '128'}
        actual = parser.parse(content, rule_name='time')
        assert expected == actual

    def test_time_3(self):
        """Invalid time signature."""
        content = r'\time 46/590'
        with pytest.raises(FailedParse):
            print(str(parser.parse(content, rule_name='time')))

    def test_staff_setting_1(self):
        """Instrument name with the "staff_setting" rule."""
        content = r'\set Staff.instrumentName = "Tuba"'
        expected = {'ly_type': 'instr_name', 'name': 'Tuba'}
        actual = parser.parse(content, rule_name='staff_setting')
        assert expected == actual

    def test_staff_setting_2(self):
        """Clef with the "staff_setting" rule."""
        content = r'\clef "bass"'
        expected = {'ly_type': 'clef', 'type': 'bass'}
        actual = parser.parse(content, rule_name='staff_setting')
        assert expected == actual

    def test_staff_setting_3(self):
        """Key with the "staff_setting" rule."""
        content = r'\key fis \minor'
        expected = {'ly_type': 'key', 'keynote': 'f', 'accid': 'is', 'mode': 'minor'}
        actual = parser.parse(content, rule_name='staff_setting')
        assert expected == actual

    def test_staff_setting_4(self):
        """Time ith the "staff_setting" rule."""
        content = r'\time 3/4'
        expected = {'ly_type': 'time', 'count': '3', 'unit': '4'}
        actual = parser.parse(content, rule_name='staff_setting')
        assert expected == actual


class TestStaffAndMusicBlock(object):
    """
    Tests for \new Staff { } and the stuff inside.
    """

    def test_staff_content_1(self):
        """With an initial setting and monophonic stuff."""
        content = r'\time 3/4  s2 s4 | s2'
        expected = {
            'ly_type': 'staff',
            'initial_settings': [{'ly_type': 'time', 'count': '3', 'unit': '4'}],
            'content': [{'layers': [[
                {'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
                {'dur': '4', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
                {'ly_type': 'barcheck'},
                {'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
            ]]}],
        }
        actual = parser.parse(content, rule_name='staff_content')
        assert expected == dict(actual.asjson())

    def test_staff_content_2(self):
        """Without an initial setting, one chunk of polyphonic stuff."""
        content = r'<< { s2 s4 } \\ { r2 r4 } >>'
        expected = {
            'ly_type': 'staff',
            'initial_settings': [],
            'content': [{'layers': [
                [
                    {'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
                    {'dur': '4', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
                ],
                [
                    {'dur': '2', 'dots': [], 'ly_type': 'rest', 'post_events': []},
                    {'dur': '4', 'dots': [], 'ly_type': 'rest', 'post_events': []},
                ],
            ]}],
        }
        actual = parser.parse(content, rule_name='staff_content')
        assert expected == dict(actual.asjson())

    def test_staff_content_3(self):
        """With two initial settings, a chunk of polyphonic stuff, then a monophonic chunk."""
        content = r"""\time 3/4 \clef "bass" << { s2 s4 } \\ { r2 r4 } >> bes,128"""
        expected = {
            'ly_type': 'staff',
            'initial_settings': [
                {'ly_type': 'time', 'count': '3', 'unit': '4'},
                {'ly_type': 'clef', 'type': 'bass'},
            ],
            'content': [
                {'layers': [
                    [
                        {'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
                        {'dur': '4', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
                    ],
                    [
                        {'dur': '2', 'dots': [], 'ly_type': 'rest', 'post_events': []},
                        {'dur': '4', 'dots': [], 'ly_type': 'rest', 'post_events': []},
                    ],
                ]},
                {'layers': [[{'pname': 'b', 'accid': ['es'], 'oct': ',', 'accid_force': None,
                             'dur': '128', 'dots': [], 'ly_type': 'note', 'post_events': []}]],
                },
            ],
        }
        actual = parser.parse(content, rule_name='staff_content')
        assert expected == dict(actual.asjson())

    def test_staff_1(self):
        """test_staff_content_1() but with a staff"""
        content = r'\new Staff { \time 3/4  s2 s4 | s2 }'
        expected = {
            'ly_type': 'staff',
            'initial_settings': [{'ly_type': 'time', 'count': '3', 'unit': '4'}],
            'content': [{'layers': [[
                {'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
                {'dur': '4', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
                {'ly_type': 'barcheck'},
                {'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
            ]]}],
        }
        actual = parser.parse(content, rule_name='staff')
        assert expected == dict(actual.asjson())

    def test_staff_2(self):
        """test_staff_content_2() but with a staff"""
        content = r'\new Staff { << { s2 s4 } \\ { r2 r4 } >> }'
        expected = {
            'ly_type': 'staff',
            'initial_settings': [],
            'content': [{'layers': [
                [
                    {'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
                    {'dur': '4', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
                ],
                [
                    {'dur': '2', 'dots': [], 'ly_type': 'rest', 'post_events': []},
                    {'dur': '4', 'dots': [], 'ly_type': 'rest', 'post_events': []},
                ],
            ]}],
        }
        actual = parser.parse(content, rule_name='staff')
        assert expected == dict(actual.asjson())

    def test_staff_3(self):
        """test_staff_content_3() but with a staff"""
        content = r"""\new Staff { \time 3/4 \clef "bass" << { s2 s4 } \\ { r2 r4 } >> bes,128 }"""
        expected = {
            'ly_type': 'staff',
            'initial_settings': [
                {'ly_type': 'time', 'count': '3', 'unit': '4'},
                {'ly_type': 'clef', 'type': 'bass'},
            ],
            'content': [
                {'layers': [
                    [
                        {'dur': '2', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
                        {'dur': '4', 'dots': [], 'ly_type': 'spacer', 'post_events': []},
                    ],
                    [
                        {'dur': '2', 'dots': [], 'ly_type': 'rest', 'post_events': []},
                        {'dur': '4', 'dots': [], 'ly_type': 'rest', 'post_events': []},
                    ],
                ]},
                {'layers': [[{'pname': 'b', 'accid': ['es'], 'oct': ',', 'accid_force': None,
                             'dur': '128', 'dots': [], 'ly_type': 'note', 'post_events': []}]],
                },
            ],
        }
        actual = parser.parse(content, rule_name='staff')
        assert expected == dict(actual.asjson())
