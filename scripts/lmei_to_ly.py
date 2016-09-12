#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               scripts/lmei_to_ly.py
# Purpose:                Converts an MEI document to a LilyPond document.
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
Converts an MEI document to a LilyPond document.
'''

from lxml import etree
from lychee.converters.outbound import lilypond


def lmei_to_ly(lmei_string):
    mei_thing = etree.fromstring(lmei_string)
    lilypond_string = lilypond.convert(mei_thing)
    return lilypond_string


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Converts an MEI document to a LilyPond document.')

    # Don't use argparse.FileType. It leaves file pointers open.

    parser.add_argument(
        'infile',
        type=str,
        help='Input LMEI file name.'
        )

    parser.add_argument(
        'outfile',
        type=str,
        help='Output LilyPond file name.'
        )

    args = parser.parse_args()

    input_file_name = args.infile
    output_file_name = args.outfile

    with open(input_file_name, 'r') as input_file:
        with open(output_file_name, 'w') as output_file:

            lmei_string = input_file.read()
            lilypond_string = lmei_to_ly(lmei_string)
            output_file.write(lilypond_string)
