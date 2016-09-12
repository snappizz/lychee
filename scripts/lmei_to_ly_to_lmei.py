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
    import argparse

    parser = argparse.ArgumentParser(
        description='Converts an MEI document to LilyPond and back.')

    # Don't use argparse.FileType. It leaves file pointers open.

    parser.add_argument(
        'infile',
        type=str,
        help='Input MEI file name.'
        )

    parser.add_argument(
        'outfile',
        type=str,
        help='Output MEI file name.'
        )

    args = parser.parse_args()

    input_file_name = args.infile
    output_file_name = args.outfile

    with open(input_file_name, 'r') as input_file:
        with open(output_file_name, 'w') as output_file:

            lmei_string = input_file.read()
            converted_lmei_string = lmei_to_ly_to_lmei(lmei_string)
            output_file.write(converted_lmei_string)
