#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/utils/music_utils.py
# Purpose:                Music utilities
#
# Copyright (C) 2017 Nathan Ho
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
Contains utilities that specifically concern LMEI as music notation. These tools are agnostic to any
inbound or outbound conversion formats, although they are useful in converters.
'''
import random
from lxml import etree
from lychee.namespaces import mei, xml
from lychee import exceptions
import fractions

KEY_SIGNATURES = {
    '7f': {'c': 'f', 'd': 'f', 'e': 'f', 'f': 'f', 'g': 'f', 'a': 'f', 'b': 'f'},
    '6f': {'c': 'f', 'd': 'f', 'e': 'f', 'f': 'n', 'g': 'f', 'a': 'f', 'b': 'f'},
    '5f': {'c': 'n', 'd': 'f', 'e': 'f', 'f': 'n', 'g': 'f', 'a': 'f', 'b': 'f'},
    '4f': {'c': 'n', 'd': 'f', 'e': 'f', 'f': 'n', 'g': 'n', 'a': 'f', 'b': 'f'},
    '3f': {'c': 'n', 'd': 'n', 'e': 'f', 'f': 'n', 'g': 'n', 'a': 'f', 'b': 'f'},
    '2f': {'c': 'n', 'd': 'n', 'e': 'f', 'f': 'n', 'g': 'n', 'a': 'n', 'b': 'f'},
    '1f': {'c': 'n', 'd': 'n', 'e': 'n', 'f': 'n', 'g': 'n', 'a': 'n', 'b': 'f'},
    '0': {'c': 'n', 'd': 'n', 'e': 'n', 'f': 'n', 'g': 'n', 'a': 'n', 'b': 'n'},
    '1s': {'c': 'n', 'd': 'n', 'e': 'n', 'f': 's', 'g': 'n', 'a': 'n', 'b': 'n'},
    '2s': {'c': 's', 'd': 'n', 'e': 'n', 'f': 's', 'g': 'n', 'a': 'n', 'b': 'n'},
    '3s': {'c': 's', 'd': 'n', 'e': 'n', 'f': 's', 'g': 's', 'a': 'n', 'b': 'n'},
    '4s': {'c': 's', 'd': 's', 'e': 'n', 'f': 's', 'g': 's', 'a': 'n', 'b': 'n'},
    '5s': {'c': 's', 'd': 's', 'e': 'n', 'f': 's', 'g': 's', 'a': 's', 'b': 'n'},
    '6s': {'c': 's', 'd': 's', 'e': 's', 'f': 's', 'g': 's', 'a': 's', 'b': 'n'},
    '7s': {'c': 's', 'd': 's', 'e': 's', 'f': 's', 'g': 's', 'a': 's', 'b': 's'},
}

# See http://music-encoding.org/documentation/3.0.0/data.DURATION.cmn/
DURATIONS = [
    "long", "breve", "1", "2", "4", "8", "16",
    "32", "64", "128", "256", "512", "1024", "2048"
]


def duration(m_thing):
    duration = m_thing.get("dur")
    if duration not in DURATIONS:
        raise exceptions.LycheeMEIError("Unknown duration: '{}'".format(duration))
    negative_log2_duration = DURATIONS.index(duration) - 2
    if negative_log2_duration >= 0:
        duration = fractions.Fraction(1, int(duration))
    else:
        duration = fractions.Fraction(2 ** -negative_log2_duration, 1)

    dots = m_thing.get("dots")
    if dots:
        dots = int(dots)
        duration = duration * fractions.Fraction(2 ** (dots + 1) - 1, 2 ** dots)
    return duration


def time_signature(m_staffdef):
    count = int(m_staffdef.get("meter.count", "4"))
    unit = int(m_staffdef.get("meter.unit", "4"))
    return count, unit


def measure_duration(m_staffdef):
    count, unit = time_signature(m_staffdef)
    return fractions.Fraction(count, unit)


def _make_beam(nodes_in_this_beam, m_layer):
    # Reject beams with 0 or 1 note.
    if len(nodes_in_this_beam) < 2:
        return

    xml_ids = []
    for node in nodes_in_this_beam:
        if not node.get(xml.ID):
            node.set(xml.ID, 'S-s-m-l-e' + ''.join([str(random.randint(0, 9)) for i in range(8)]))
        xml_id = node.get(xml.ID)
        xml_ids.append('#' + xml_id)

    beam_span = etree.Element(mei.BEAM_SPAN)
    beam_span.attrib.update({
        'plist': ' '.join(xml_ids),
        'startid': xml_ids[0],
        'endid': xml_ids[-1],
        })

    # Insert the new beamSpan after the last node in it.
    last_node = nodes_in_this_beam[-1]
    parent_of_last_node = last_node.getparent()
    index_of_last_node_in_parent = parent_of_last_node.index(last_node)
    parent_of_last_node.insert(index_of_last_node_in_parent + 1, beam_span)


def autobeam(m_layer, m_staffdef):
    if m_staffdef is None:
        m_staffdef = {}
    count, unit = time_signature(m_staffdef)
    unit = fractions.Fraction(1, unit)
    measure_length = measure_duration(m_staffdef)

    nodes_in_this_beam = []

    beat_phase = 0
    for m_node in m_layer:
        if m_node.get('dur'):

            this_node_is_beamable = (
                m_node.tag in (mei.NOTE, mei.CHORD) and
                m_node.get('dur') not in ('long', 'breve', '1', '2', '4'))
            this_node_interrupts_beams = (
                m_node.tag == mei.REST or (
                    m_node.tag in (mei.NOTE, mei.CHORD) and
                    m_node.get('dur') in ('long', 'breve', '1', '2', '4')))

            if this_node_interrupts_beams:
                _make_beam(nodes_in_this_beam, m_layer)
                nodes_in_this_beam = []
            if this_node_is_beamable:
                nodes_in_this_beam.append(m_node)

            beat_phase += duration(m_node)
            if beat_phase >= unit:
                beat_phase = beat_phase % unit
                if beat_phase == 0:
                    _make_beam(nodes_in_this_beam, m_layer)
                    nodes_in_this_beam = []
                    pass

    _make_beam(nodes_in_this_beam, m_layer)
