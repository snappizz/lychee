#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               scripts/ly_to_lmei.py
# Purpose:                Converts a LilyPond document to an MEI document.
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
Converts a LilyPond document to an MEI document.
'''

from lxml import etree
from lychee.converters.inbound import lilypond


def ly_to_lmei(lilypond_string):
    mei_thing = lilypond.convert(lilypond_string)
    lmei_string = etree.tostring(mei_thing, pretty_print=True)
    return lmei_string


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Converts a LilyPond document to an MEI document.')

    # Don't use argparse.FileType. It leaves file pointers open.

    parser.add_argument(
        'infile',
        type=str,
        help='Input LilyPond file name.'
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

            lilypond_string = input_file.read()
            lmei_string = ly_to_lmei(lilypond_string)
            output_file.write(lmei_string)
