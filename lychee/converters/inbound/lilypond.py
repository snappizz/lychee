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

.. warning::
    This module is intended for internal *Lychee* use only, so the API may change without notice.
    If you wish to use this module outside *Lychee*, please contact us to discuss the best way.

.. tip::
    We recommend that you use the converters indirectly.
    Refer to :ref:`how-to-use-converters` for more information.
'''

# NOTE for Lychee developers:
#
# The module "lychee.converters.lilypond_parser" is autogenerated from "lilypond.ebnf" using Grako.
#
# Run this command in this directory to regenerate the "lilypond_parser" module after you update
# the EBNF grammar specification:
# $ python -m grako -c -o lilypond_parser.py lilypond.ebnf

import collections

from lxml import etree

from lychee.converters.inbound import lilypond_parser
from lychee import exceptions
from lychee.logs import INBOUND_LOG as log
from lychee.namespaces import mei
from lychee.signals import inbound


_ACCIDENTAL_MAPPING = {
    'eses': 'ff',
    'es': 'f',
    'is': 's',
    'isis': 'ss',
}
_OCTAVE_MAPPING = {
    ",,": '1',
    ",": '2',
    "'''''": '8',
    "''''": '7',
    "'''": '6',
    "''": '5',
    "'": '4',
    None: '3'
}
_KEY_MAPPING = {
    'major': {
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
    },
    'minor': {
        'aes': '7f',
        'ees': '6f',
        'bes': '5f',
        'f': '4f',
        'c': '3f',
        'g': '2f',
        'd': '1f',
        'a': '0',
        'e': '1s',
        'b': '2s',
        'fis': '3s',
        'cis': '4s',
        'gis': '5s',
        'dis': '6s',
        'ais': '7s',
    },
}
ClefSpec = collections.namedtuple('ClefSpec', ('shape', 'line'))
_CLEF_MAPPING = {
    'bass': ClefSpec('F', '4'),
    'tenor': ClefSpec('C', '4'),
    'alto': ClefSpec('C', '3'),
    'treble': ClefSpec('G', '2'),
}
# defined at end of file: _STAFF_SETTINGS_FUNCTIONS


def check(condition, message=None):
    """
    Check that ``condition`` is ``True``.

    :param bool condition: This argument will be checked to be ``True``.
    :param str message: A failure message to use if the check does not pass.
    :raises: :exc:`exceptions.LilyPondError` when ``condition`` is anything other than ``True``.

    Use this function to guarantee that something is the case. This function replaces the ``assert``
    statement but is always executed (not only in debug mode).

    **Example 1**

    >>> check(5 == 5)

    The ``5 == 5`` evaluates to ``True``, so the function returns just fine.

    **Example 2**

    >>> check(5 == 4)

    The ``5 == 4`` evaluates to ``False``, so the function raises an :exc:`exceptions.LilyPondError`.
    """
    message = 'check failed' if message is None else message
    if condition is not True:
        raise exceptions.LilyPondError(message)


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

    with log.info('parse LilyPond') as action:
        parser = lilypond_parser.LilyPondParser(parseinfo=False)
        parsed = parser.parse(document, filename='file', trace=False)

    with log.info('convert LilyPond') as action:
        if 'score' in parsed:
            check_version(parsed)
        elif 'staff' in parsed:
            parsed = {'score': [parsed]}
        elif isinstance(parsed, list) and 'measure' in parsed[0]:
            parsed = {'score': [{'staff': {'measures': parsed}}]}
        else:
            raise RuntimeError('need score, staff, or measures for the top-level thing')

        converted = do_file(parsed)

    return converted


@log.wrap('info', 'check syntax version', 'action')
def check_version(parsed, action):
    '''
    Guarantees the version is at least somewhat compatible.

    If the major version is not '2', raises.
    If the minor version is other than '18', warns.
    '''
    if parsed['version']:
        if parsed['version'][0] != '2':
            raise RuntimeError('inbound LilyPond parser expects version 2.18.x')
        elif parsed['version'][1] != '18':
            action.failure('inbound LilyPond parser expects version 2.18.x')
    else:
        action.failure('missing version info')


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


@log.wrap('debug', 'set clef', 'action')
def set_initial_clef(l_clef, m_staffdef, action):
    '''
    Set the clef for a staff.

    :param dict l_time: The clef as parsed by Grako.
    :param m_staffdef: The LMEI <staffDef> on which to set the clef.
    :type m_staffdef: :class:`lxml.etree.Element`
    :returns: ``None``

    If the clef type is not recognized, :func:`set_initial_clef` emits a failure log message and
    does not set a clef.
    '''
    check(l_clef['ly_type'] == 'clef', 'did not receive a clef')
    if l_clef['type'] in _CLEF_MAPPING:
        m_staffdef.set('clef.shape', _CLEF_MAPPING[l_clef['type']].shape)
        m_staffdef.set('clef.line', _CLEF_MAPPING[l_clef['type']].line)
    else:
        action.failure('unrecognized clef type: {clef_type}', clef_type=l_clef['type'])


@log.wrap('debug', 'set time signature')
def set_initial_time(l_time, m_staffdef):
    '''
    Set the time signature for a staff.

    :param dict l_time: The time specification as parsed by Grako.
    :param m_staffdef: The LMEI <staffDef> on which to set the time signature.
    :type m_staffdef: :class:`lxml.etree.Element`
    :returns: ``None``
    '''
    check(l_time['ly_type'] == 'time', 'did not receive a time specification')
    m_staffdef.set('meter.count', l_time['count'])
    m_staffdef.set('meter.unit', l_time['unit'])


@log.wrap('debug', 'set key signature')
def set_initial_key(l_key, m_staffdef):
    '''
    Set the key signature for a staff.

    :param dict l_key: The key specification as parsed by Grako.
    :param m_staffdef: The LMEI <staffDef> on which to set the key signature.
    :type m_staffdef: :class:`lxml.etree.Element`
    :returns: ``None``
    '''
    check(l_key['ly_type'] == 'key', 'did not receive a key specification')

    if l_key['accid']:
        keynote = l_key['keynote'] + l_key['accid']
    else:
        keynote = l_key['keynote']

    m_staffdef.set('key.sig', _KEY_MAPPING[l_key['mode']][keynote])


@log.wrap('debug', 'set instrument name')
def set_instrument_name(l_name, m_staffdef):
    """
    Set the instrument name for a staff.

    :param dict l_name: The instrument name as parsed by Grako.
    :param m_staffdef: The LMEI <staffDef> on which to set the instrument name.
    :type m_staffdef: :class:`lxml.etree.Element`
    :returns: ``None``
    """
    check(l_name['ly_type'] == 'instr_name', 'did not receive an instrument name')
    m_staffdef.set('label', l_name['name'])


@log.wrap('info', 'convert staff', 'action')
def do_staff(l_staff, m_section, m_staffdef, action):
    '''
    :param dict l_staff: The LilyPond Staff context from Grako.
    :param m_section: The LMEI <section> that will hold the staff.
    :type m_section: :class:`lxml.etree.Element`
    :param m_staffdef: The LMEI <staffDef> used to define this staff.
    :type m_staffdef: :class:`lxml.etree.Element`
    :returns: ``None``
    :raises: :exc:`exceptions.LilyPondError` when the ``l_staff`` argument is not a staff.
    :raises: :exc:`exceptions.LilyPondError` when the ``m_staffdef`` argument does not have an @n attribute.

    .. note:: This function assumes that the ``m_staffdef`` argument is already present in the score.
        That is, the <staffDef> does not become a child element of the <staff> in this function.

    If the Staff context contains unknown staff settings, :func:`do_staff` emits a failure log
    message and continues processing the following settings and Voices in the Staff context.

    The @n attribute is taken from the ``m_staffdef`` argument. If the @n attribute is missing,
    :func:`do_staff` raises :exc:`exceptions.LilyPondError`.

    This function will use a single <staff> element whenever possible. However, each change between
    monophonic and polyphonic notation produces a new <staff> element. The following example shows
    a section with two staves; the second staff is split between two <staff> elements for technical
    reasons, but the @n attribute indicates they should be displayed as the same staff.

    .. sourcecode:: xml

        <section>
            <staff n="1"><!-- some content --></staff>
            <staff n="2"><!-- some monophonic content --></staff>
            <staff n="2"><!-- some polyphonic content --></staff>
        </section>
    '''
    check(l_staff['ly_type'] == 'staff', 'did not receive a staff')
    check(m_staffdef.get('n') is not None, '<staffDef> is missing @n')

    for l_setting in l_staff['initial_settings']:
        with log.debug('handle staff setting') as action:
            if l_setting['ly_type'] in _STAFF_SETTINGS_FUNCTIONS:
                _STAFF_SETTINGS_FUNCTIONS[l_setting['ly_type']](l_setting, m_staffdef)
                action.success('converted {ly_type}', ly_type=l_setting['ly_type'])
            else:
                action.failure('unknown staff setting: {ly_type}', ly_type=l_setting['ly_type'])

    for i, l_each_staff in enumerate(l_staff['content']):
        with log.debug('convert staff @n={staff_n}:{i}', staff_n=m_staffdef.get('n'), i=i):
            m_each_staff = etree.SubElement(m_section, mei.STAFF, {'n': m_staffdef.get('n')})
            for layer_n, l_layer in enumerate(l_each_staff['layers']):
                # we must add 1 to layer_n or else the @n would start at 0, not 1
                do_layer(l_layer, m_each_staff, layer_n + 1)


@log.wrap('debug', 'convert voice/layer', 'action')
def do_layer(l_layer, m_container, layer_n, action):
    '''
    Convert a LilyPond Voice context into an LMEI <layer> element.

    :param l_layer: The LilyPond Voice context from Grako.
    :type l_layer: list of dict
    :param m_container: The MEI <measure> or <staff> that will hold the layer.
    :type m_container: :class:`lxml.etree.Element`
    :returns: The new <layer> element.
    :rtype: :class:`lxml.etree.Element`
    :param int layer_n: The @n attribute value for this <layer>.

    If the Voice context contains an unknown node type, :func:`do_layer` emits a failure log message
    and continues processing the following nodes in the Voice context.
    '''
    m_layer = etree.SubElement(m_container, mei.LAYER, {'n': str(layer_n)})

    node_converters = {
        'chord': do_chord,
        'note': do_note,
        'rest': do_rest,
        'spacer': do_spacer,
    }

    for obj in l_layer:
        with log.debug('node conversion') as action:
            if obj['ly_type'] in node_converters:
                node_converters[obj['ly_type']](obj, m_layer)
                action.success('converted {ly_type}', ly_type=obj['ly_type'])
            else:
                action.failure('unknown node type: {ly_type}', ly_type=obj['ly_type'])

    return m_layer


@log.wrap('debug', 'add octave', 'action')
def process_octave(l_oct, action):
    '''
    Convert an octave specifier from the parsed LilyPond into an MEI @oct attribute.

    :param str l_oct: The "octave" part of the LilyPond note as provided by Grako. May also be ``None``.
    :returns: The LMEI octave number.
    :rtype: str

    If the octave is not recognized, :func:`process_octave` emits a failure log message and returns
    the same value as if ``l_oct`` were ``None``.
    '''
    if l_oct in _OCTAVE_MAPPING:
        return _OCTAVE_MAPPING[l_oct]
    else:
        action.failure('unknown octave: {octave}', octave=l_oct)
        return _OCTAVE_MAPPING[None]


@log.wrap('debug', 'add accidental', 'action')
def process_accidental(l_accid, attrib, action):
    '''
    Add an accidental to the LMEI note, if required.

    :param l_accid: The LilyPond accidental as provided by Grako.
    :type l_accid: list of str
    :param dict attrib: The attributes for the MEI <note/> element *before* creation.
    :returns: The ``attrib`` argument.

    If the accidental is not recognized, :func:`process_accidental` emits a failure log message and
    returns the ``attrib`` argument unchanged.
    '''
    if l_accid:
        l_accid = ''.join(l_accid)
        if l_accid in _ACCIDENTAL_MAPPING:
            attrib['accid.ges'] = _ACCIDENTAL_MAPPING[l_accid]
        else:
            action.failure('unknown accidental: {accid}', accid=l_accid)

    return attrib


@log.wrap('debug', 'add forced accidental', 'action')
def process_forced_accid(l_note, attrib, action):
    '''
    Add a forced accidental to the LMEI note, if required.

    :param dict l_note: The LilyPond note from Grako.
    :param dict attrib: The attributes for the MEI <note/> element *before* creation.
    :returns: The ``attrib`` argument.
    '''
    if l_note['accid_force'] == '!':
        if 'accid.ges' in attrib:
            attrib['accid'] = attrib['accid.ges']
        else:
            # show a natural
            attrib['accid'] = 'n'

    return attrib


@log.wrap('debug', 'add cautionary accidental', 'action')
def process_caut_accid(l_note, m_note, action):
    '''
    Add a cautionary accidental to the LMEI note, if required.

    :param dict l_note: The LilyPond note from Grako.
    :param m_note: The MEI <note/> element.
    :type m_note: :class:`lxml.etree.Element`
    :returns: The ``m_note`` argument.
    '''
    if l_note['accid_force'] == '?':
        if m_note.get('accid.ges') is not None:
            attribs = {'accid': m_note.get('accid.ges'), 'func': 'caution'}
        else:
            # show a natural
            attribs = {'accid': 'n', 'func': 'caution'}
        etree.SubElement(m_note, mei.ACCID, attribs)

    return m_note


@log.wrap('debug', 'process dots', 'action')
def process_dots(l_node, attrib, action):
    """
    Handle the @dots attribute for a chord, note, rest, or spacer rest.

    :param dict l_node: The LilyPond node from Grako.
    :param dict attrib: The attribute dictionary that will be given to the :class:`Element` constructor.
    :returns: The ``attrib`` dictionary.

    Converts the "dots" member of ``l_node`` to the appropriate number in ``attrib``. If there is
    no "dots" member in ``l_node``, submit a "failure" log message and assume there are no dots.
    """
    if 'dots' in l_node:
        if l_node['dots']:
            attrib['dots'] = str(len(l_node['dots']))
    else:
        action.failure("missing 'dots' in the LilyPond node")

    return attrib


@log.wrap('debug', 'convert chord', 'action')
def do_chord(l_chord, m_layer, action):
    """
    Convert a LilyPond chord to an LMEI <chord/>.

    :param dict l_chord: The LilyPond chord from Grako.
    :param m_layer: The MEI <layer> that will hold the chord.
    :type m_layer: :class:`lxml.etree.Element`
    :returns: The new <chord/> element.
    :rtype: :class:`lxml.etree.Element`
    :raises: :exc:`exceptions.LilyPondError` if ``l_chord`` does not contain a Grako chord
    """
    check(l_chord['ly_type'] == 'chord', 'did not receive a chord')

    attrib = {'dur': l_chord['dur']}
    process_dots(l_chord, attrib)

    m_chord = etree.SubElement(m_layer, mei.CHORD, attrib)

    for l_note in l_chord['notes']:
        attrib = {
            'pname': l_note['pname'],
            'oct': process_octave(l_note['oct']),
        }

        process_accidental(l_note['accid'], attrib)
        process_forced_accid(l_note, attrib)

        m_note = etree.SubElement(m_chord, mei.NOTE, attrib)

        process_caut_accid(l_note, m_note)

    return m_chord


@log.wrap('debug', 'convert note', 'action')
def do_note(l_note, m_layer, action):
    """
    Convert a LilyPond note to an LMEI <note/>.

    :param dict l_note: The LilyPond note from Grako.
    :param m_layer: The MEI <layer> that will hold the note.
    :type m_layer: :class:`lxml.etree.Element`
    :returns: The new <note/> element.
    :rtype: :class:`lxml.etree.Element`
    :raises: :exc:`exceptions.LilyPondError` if ``l_note`` does not contain a Grako note
    """
    check(l_note['ly_type'] == 'note', 'did not receive a note')

    attrib = {
        'pname': l_note['pname'],
        'dur': l_note['dur'],
        'oct': process_octave(l_note['oct']),
    }

    process_accidental(l_note['accid'], attrib)
    process_forced_accid(l_note, attrib)
    process_dots(l_note, attrib)

    m_note = etree.SubElement(m_layer, mei.NOTE, attrib)

    process_caut_accid(l_note, m_note)

    return m_note


@log.wrap('debug', 'convert rest', 'action')
def do_rest(l_rest, m_layer, action):
    """
    Convert a LilyPond rest to an LMEI <rest/>.

    :param dict l_rest: The LilyPond rest from Grako.
    :param m_layer: The LMEI <layer> that will hold the rest.
    :type m_layer: :class:`lxml.etree.Element`
    :returns: The new <rest/> element.
    :rtype: :class:`lxml.etree.Element`
    :raises: :exc:`exceptions.LilyPondError` if ``l_rest`` does not contain a Grako rest
    """
    check(l_rest['ly_type'] == 'rest', 'did not receive a rest')

    attrib = {
        'dur': l_rest['dur'],
    }

    process_dots(l_rest, attrib)

    m_rest = etree.SubElement(m_layer, mei.REST, attrib)

    return m_rest


@log.wrap('debug', 'convert spacer', 'action')
def do_spacer(l_spacer, m_layer, action):
    """
    Convert a LilyPond spacer rest to an LMEI <space/>.

    :param dict l_spacer: The LilyPond spacer rest from Grako.
    :param m_layer: The LMEI <layer> that will hold the space.
    :type m_layer: :class:`lxml.etree.Element`
    :returns: The new <space/> element.
    :rtype: :class:`lxml.etree.Element`
    :raises: :exc:`exceptions.LilyPondError` if ``l_spacer`` does not contain a Grako spacer rest
    """
    check(l_spacer['ly_type'] == 'spacer', 'did not receive a spacer rest')

    attrib = {
        'dur': l_spacer['dur'],
    }

    process_dots(l_spacer, attrib)

    m_space = etree.SubElement(m_layer, mei.SPACE, attrib)

    return m_space


# this is at the bottom so the functions will already be defined
_STAFF_SETTINGS_FUNCTIONS = {
    'clef': set_initial_clef,
    'key': set_initial_key,
    'instr_name': set_instrument_name,
    'time': set_initial_time,
}
