#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/ly_to_mei_new.py
# Purpose:                Converts a LilyPond document to a Lychee-MEI document.
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
'''
Converts a LilyPond document to a Lychee-MEI document.
'''

# NOTE for Lychee developers:
#
# The module "lychee.converters.lilypond_parser" is autogenerated from "lilypond.ebnf" using Grako.
#
# Run this command in this directory to regenerate the "lilypond_parser" module after you update
# the EBNF grammar specification:
# $ python -m grako -c -o lilypond_parser.py lilypond.ebnf

from lxml import etree

import lychee
from lychee.converters import lilypond_parser
from lychee.namespaces import mei
from lychee.signals import inbound


def convert(document, **kwargs):
    '''
    Convert a LilyPond document into an MEI document. This is the entry point for Lychee conversions.

    :param str document: The LilyPond document.
    :returns: The corresponding MEI document.
    :rtype: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    '''
    inbound.CONVERSION_STARTED.emit()
    section = convert_no_signals(document)
    inbound.CONVERSION_FINISH.emit(converted=section)


def convert_no_signals(document):
    '''
    It's the convert() function that returns the converted document rather than emitting it with
    the CONVERSION_FINISHED signal. Mostly for testing.
    '''

    parser = lilypond_parser.LilyPondParser(parseinfo=False)
    parsed = parser.parse(
        document,
        startrule='start',
        filename='file',
        trace=False,
        left_recursion=True,
        comments_re='\\%\\{.*?\\%\\}')

    if 'score' in parsed:
        check_version(parsed)
    elif 'staff' in parsed:
        parsed = {'score': [parsed]}
    elif isinstance(parsed, list) and 'measure' in parsed[0]:
        parsed = {'score': [{'staff': {'measures': parsed}}]}
    else:
        raise RuntimeError('Need score, staff, or measures for the top-level thing')

    converted = do_file(parsed)
    return converted


def check_version(parsed):
    '''
    Guarantees the version is at least somewhat compatible.

    If the major version is not '2', raises.
    If the minor version is other than '18', warns.
    '''
    if parsed['version']:
        if parsed['version'][0] != '2':
            raise RuntimeError()
        elif parsed['version'][1] != '18':
            lychee.log('The inbound LilyPond parsers expects version 2.18.x')


def do_file(parsed):
    '''
    Take the parsed result of a whole file and convert it.

    :param dict parsed: The LilyPond file straight from the parser.
    :returns: A converted ``<section>`` element in Lychee-MEI.
    :rtype: :class:`lxml.etree.Element`
    '''
    m_section = etree.Element(mei.SECTION)
    m_scoredef = etree.SubElement(m_section, mei.SCORE_DEF)
    m_staffgrp = etree.SubElement(m_scoredef, mei.STAFF_GRP)

    staff_n = 1
    for l_staff in parsed['score']:
        m_staffdef = etree.SubElement(m_staffgrp, mei.STAFF_DEF, {'n': str(staff_n), 'lines': '5'})
        do_staff(l_staff, m_section, staff_n, m_staffdef)
        staff_n += 1

    return m_section


def do_staff(l_staff, m_section, staff_n, m_staffdef):
    '''
    :param dict l_staff: A LilyPond staff from the parser.
    :param m_section: An MEI ``<section>`` element to put this staff into.
    :type m_section: :class:`lxml.etree.Element`
    :param int staff_n: The @n value for this ``<staff>``.
    '''
    m_staff = etree.SubElement(m_section, mei.STAFF, {'n': str(staff_n)})

    measure_n = 1
    for l_measure in l_staff['staff']['measures']:
        do_measure(l_measure, m_staff, measure_n, m_staffdef)
        measure_n += 1

    return m_staff


def set_initial_clef(l_clef, m_staffdef):
    '''
    Set a Lilypond ``\clef`` command as the initial clef for a staff.
    '''
    assert l_clef['ly_type'] == 'clef'

    if l_clef['type'] == 'bass':
        m_staffdef.set('clef.shape', 'F')
        m_staffdef.set('clef.line', '4')
    elif l_clef['type'] == 'tenor':
        m_staffdef.set('clef.shape', 'C')
        m_staffdef.set('clef.line', '4')
    elif l_clef['type'] == 'alto':
        m_staffdef.set('clef.shape', 'C')
        m_staffdef.set('clef.line', '3')
    elif l_clef['type'] == 'treble':
        m_staffdef.set('clef.shape', 'G')
        m_staffdef.set('clef.line', '2')

    return m_staffdef


def set_initial_time(l_time, m_staffdef):
    '''
    Set a Lilypond ``\time`` command as the initial time signature for a staff.
    '''
    assert l_time['ly_type'] == 'time'

    m_staffdef.set('meter.count', l_time['count'])
    m_staffdef.set('meter.unit', l_time['unit'])

    return m_staffdef


def set_initial_key(l_key, m_staffdef):
    '''
    Set a LilyPond ``\key`` command as the initial key signature for a staff.

    NOTE: this function supports major keys only, for now, and will raise RuntimeError on minor.
    '''
    assert l_key['ly_type'] == 'key'
    assert l_key['mode'] == 'major'

    CONV = {
        'ces': '7f',
        'ges': '6f',
        'des': '5f',
        'aes': '4f',
        'ees': '3f',
        'bes': '2f',
        'f': '1f',
        'c': '0',
        'g': '1s',
        'd': '2s',
        'a': '3s',
        'e': '4s',
        'b': '5s',
        'fis': '6s',
        'cis': '7s',
    }

    if l_key['accid']:
        keynote = l_key['keynote'] + l_key['accid']
    else:
        keynote = l_key['keynote']

    m_staffdef.set('key.sig', CONV[keynote])

    return m_staffdef


def set_instrument_name(l_name, m_staffdef):
    '''
    Set a Lilypond ``\set Staff.instrumentName`` command as the staff's instrument name.
    '''
    assert l_name['ly_type'] == 'instr_name'

    m_staffdef.set('label', l_name['instrument_name'])

    return m_staffdef


def do_measure(l_measure, m_staff, measure_n, m_staffdef):
    '''
    :param dict l_measure: A LilyPond measure from the parser.
    :param m_staff: An MEI ``<staff>`` element to put this measure into.
    :type m_staff: :class:`lxml.etree.Element`
    :param int measure_n: The @n value for this ``<measure>``.
    '''
    m_measure = etree.SubElement(m_staff, mei.MEASURE, {'n': str(measure_n)})
    m_layer = etree.SubElement(m_measure, mei.LAYER, {'n': '1'})

    initial_options_converters = {
        'clef': set_initial_clef,
        'key': set_initial_key,
        'instr_name': set_instrument_name,
        'time': set_initial_time,
    }
    node_converters = {
        'note': do_note,
        'rest': do_rest,
        'spacer': do_spacer,
    }

    passed_initial_settings = False
    for obj in l_measure['measure'][0]:
        if obj['ly_type'] in initial_options_converters and not passed_initial_settings:
            initial_options_converters[obj['ly_type']](obj, m_staffdef)

        elif obj['ly_type'] in initial_options_converters:
            # TODO
            lychee.log('Not converting {} in a measure from LilyPond'.format(obj['ly_type']))

        elif obj['ly_type'] in node_converters:
            if not passed_initial_settings:
                passed_initial_settings = True
            node_converters[obj['ly_type']](obj, m_layer)

        else:
            raise RuntimeError()

    return m_measure


def process_octave(l_oct):
    '''
    Convert an octave specifier from the parsed LilyPond into an MEI @oct attribute.
    '''
    convert_dict = {
        ",,": '1',
        ",": '2',
        "'''''": '8',
        "''''": '7',
        "'''": '6',
        "''": '5',
        "'": '4',
        None: '3'
    }
    return convert_dict[l_oct]


def process_accidental(l_accid, attrib):
    '''
    Convert an accidental specifier from the parsed LilyPond into an MEI @accid attribute, putting
    it in the "attrib" dictionary if given.
    '''
    convert_dict = {
        'eses': 'ff',
        'es': 'f',
        'is': 's',
        'isis': 'ss',
    }
    if l_accid:
        l_accid = ''.join(l_accid)
        attrib['accid.ges'] = convert_dict[l_accid]

    return attrib


def process_forced_accid(l_note, attrib):
    '''
    Given a parsed LilyPond note and the "attrib" dictionary for its yet-to-be-created MEI element,
    put stuff in attrib for a forced accidental, if required.
    '''
    if l_note['accidental_force'] == '!':
        if 'accid.ges' in attrib:
            attrib['accid'] = attrib['accid.ges']
        else:
            # show a natural
            attrib['accid'] = 'n'

    return attrib


def process_caut_accid(l_note, attrib, m_note):
    '''
    Given a parsed LilyPond note, the "attrib" dictionary of its already-created MEI element, and
    that MEI element, add an ``<accid>`` subelement to the ``<note>`` for a cautionary accidental,
    if required.

    :returns: The MEI ``<note>`` element.
    '''
    if l_note['accidental_force'] == '?':
        if 'accid.ges' in attrib:
            etree.SubElement(m_note, mei.ACCID, {'accid': attrib['accid.ges'], 'func': 'cautionary'})
        else:
            # show a natural
            etree.SubElement(m_note, mei.ACCID, {'accid': 'n', 'func': 'cautionary'})

    return m_note


def process_dots(l_note, attrib):
    '''
    Given a aprsed LilyPond note/rest/spacer and the "attrib" dictionary for its yet-to-be-created
    MEI element, put stuff in attrib for dots, if required.
    '''
    if len(l_note['duration']['dots']):
        attrib['dots'] = str(len(l_note['duration']['dots']))

    return attrib


def do_note(l_note, m_layer):
    assert l_note['ly_type'] == 'note'

    attrib = {
        'pname': l_note['note_name'],
        'dur': l_note['duration']['number'],
        'oct': process_octave(l_note['octave']),
    }

    process_accidental(l_note['accidental'], attrib)
    process_forced_accid(l_note, attrib)
    process_dots(l_note, attrib)

    m_note = etree.SubElement(m_layer, mei.NOTE, attrib)

    process_caut_accid(l_note, attrib, m_note)

    return m_note


def do_rest(l_rest, m_layer):
    assert l_rest['ly_type'] == 'rest'

    attrib = {
        'dur': l_rest['duration']['number'],
    }

    process_dots(l_rest, attrib)

    m_rest = etree.SubElement(m_layer, mei.REST, attrib)

    return m_rest


def do_spacer(l_spacer, m_layer):
    assert l_spacer['ly_type'] == 'spacer'

    attrib = {
        'dur': l_spacer['duration']['number'],
    }

    process_dots(l_spacer, attrib)

    m_space = etree.SubElement(m_layer, mei.SPACE, attrib)

    return m_space
