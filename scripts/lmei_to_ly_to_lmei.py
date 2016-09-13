#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               scripts/ly_to_lmei_to_ly.py
# Purpose:                Converts an MEI document to LilyPond and back.
#
# Copyright (C) 2016 Nathan Ho
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
Converts an MEI document to LilyPond and back.
'''

from lxml import etree
from lychee.converters.inbound import lilypond as inbound_lilypond
from lychee.converters.outbound import lilypond as outbound_lilypond


def lmei_to_ly_to_lmei(lmei_string):
    mei_thing = etree.fromstring(lmei_string)
    lilypond_thing = outbound_lilypond.convert(mei_thing)
    converted_lmei_thing = inbound_lilypond.convert(lilypond_thing)
    converted_lmei_string = etree.tostring(converted_lmei_thing, pretty_print=True)
    return converted_lmei_string


if __name__ == '__main__':
    from helper_utils import run_conversion_helper_script

    run_conversion_helper_script(
        core_function=lmei_to_ly_to_lmei,
        description='Converts an MEI document to LilyPond and back.',
        input_file_type='LMEI',
        output_file_type='LMEI',
        )
