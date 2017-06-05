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
from lychee import exceptions
import fractions


PITCH_NAMES = 'cdefgab'

KEY_SIGNATURES = {
    '7f': 'fffffff',
    '6f': 'fffnfff',
    '5f': 'nffnfff',
    '4f': 'nffnnff',
    '3f': 'nnfnnff',
    '2f': 'nnfnnnf',
    '1f': 'nnnnnnf',
    '0': 'nnnnnnn',
    '1s': 'nnnsnnn',
    '2s': 'snnsnnn',
    '3s': 'snnssnn',
    '4s': 'ssnssnn',
    '5s': 'ssnsssn',
    '6s': 'ssssssn',
    '7s': 'sssssss',
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
