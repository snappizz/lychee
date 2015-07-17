#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/abjad_to_mei.py
# Purpose:                Converts an MEI document to an Abjad document.
#
# Copyright (C) 2015 Jeffrey Treviño
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
Converts an MEI document to an Abjad document.

..  container:: example

    **Example 1.** Initializes from mei Element Tree:

    ::

        >>> root = ETree.Element("note",dots="1",dur="4",oct="4",pname="c")
        >>> ETree.SubElement(root,"accid",accid="sd",func="cautionary")
        >>> tree = ETree.ElementTree(root)
        >>> note = meiTreeToAbjadNote(tree)

    ..  doctest::

        >>> note
        Note("cqs'4.")
'''


from lxml import etree as ETree
from abjad import *
from abjad.tools.scoretools.NoteHead import NoteHead
from abjad.tools.scoretools.FixedDurationTuplet import FixedDurationTuplet
from abjad.tools.durationtools.Multiplier import Multiplier
from abjad.tools.durationtools.Duration import Duration

'''
from abjad.tools.scoretools.Note import Note
from abjad.tools.scoretools.Rest import Rest
from abjad.tools.scoretools.Chord import Chord
from abjad.tools.durationtools.Multiplier import Multiplier
from abjad.tools.durationtools.Duration import Duration
from abjad.tools.scoretools.Voice import Voice
from abjad.tools.scoretools.Staff import Staff
from abjad.tools.scoretools.Score import Score
from abjad.tools.scoretools.StaffGroup import StaffGroup
from abjad.tools.scoretools.NoteHead import NoteHead
from abjad.tools.durationtools.Duration import Duration
'''

_MEINS = '{http://www.music-encoding.org/ns/mei}'
_XMLNS = '{http://www.w3.org/XML/1998/namespace}id'
ETree.register_namespace('mei', _MEINS[1:-1])

#import lychee
#from lychee.signals import outbound


def convert(document, **kwargs):
    '''
    Convert an MEI document into an Abjad document.

    :param document: The MEI document.
    :type document: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    :returns: The corresponding MEI document.
    :rtype: object
    '''
    outbound.CONVERSION_STARTED.emit()
    lychee.log('{}.convert(document="{}")'.format(__name__, document))

    # TODO: put the conversion stuff here
    # TODO: CONVERSION_FINISH should be called with the Abjad result

    outbound.CONVERSION_FINISH.emit(converted='<Abjad stuff>')
    lychee.log('{}.convert() after finish signal'.format(__name__))


def convert_accidental_mei_to_abjad(mei_accidental_string):
    # helper that converts an mei accidental string to an Abjad accidental string
    accidental_dictionary = {'f': 'f', 's': 's', 'ff': 'ff', 'x': 'ss', 'su': 'tqs', 
                            'sd': 'qs', 'fd': 'tqf', 'fu': 'qf'}
    return accidental_dictionary[mei_accidental_string]


def octave_integer_to_string(octave_integer):
    if octave_integer == 3:
        return ''
    elif octave_integer > 3:
        return "'" * (octave_integer - 3)
    else:
        return "," * (3 - octave_integer)


def append_accidental(mei_note):
    # append accidental string, if one should be appended
    accid_element = mei_note.findall('./accid')
    if len(accid_element):
    # if cautionary accidental
        accid = accid_element[0].get('accid')
        if accid != 'n':
        # that isn't a natural
            return convert_accidental_mei_to_abjad(accid)
    else:
    # if normal accidental
        accid = mei_note.get('accid.ges')
        if accid:
            if accid != 'n':
                return convert_accidental_mei_to_abjad(accid)
    return ''
        
def make_abjad_note_from_string(the_string,mei_note):
     #append the duration
        the_string += str(mei_note.get('dur'))
        if mei_note.get('dots'):
            for x in range(int(mei_note.get('dots'))):
                the_string += '.'
        # and create a note
        return Note(the_string)

def set_forced(output,mei_note):
    if mei_note.get('accid'):
        if hasattr(output,'is_forced'):
            output.is_forced = True
        else:
            output.note_head.is_forced = True

def set_cautionary(output, mei_note):
    accid = mei_note.findall('accid')
    if len(accid):
        if hasattr(output, 'is_cautionary'):
            output.is_cautionary = True
        else:
            output.note_head.is_cautionary = True
        

def mei_note_to_abjad_note(mei_note):
    the_string = ""
    # append pitch name
    the_string += mei_note.get('pname')
    the_string += append_accidental(mei_note)
    # octave tick string
    the_string += octave_integer_to_string(int(mei_note.get('octave')))
    #if the mei note Element has a duration,
    if mei_note.get('dur'):
       output = make_abjad_note_from_string(the_string,mei_note)
    else:
        # otherwise create an abjad NoteHead
        output = NoteHead(the_string)
    # set forced
    set_forced(output,mei_note)
    # set cautionary
    set_cautionary(output, mei_note)
    return output
        

def mei_rest_to_abjad_rest(mei_rest):
    the_string = "r"
    the_string += mei_rest.get('dur')
    if mei_rest.get('dots'):
        for x in range(int(mei_rest.get('dots'))):
            the_string += '.'
    abjad_rest = Rest(the_string)
    return abjad_rest



def mei_chord_to_abjad_chord(mei_chord):
    dots = mei_chord.get('dots')
    dur = mei_chord.get('dur')
    abjad_duration = Duration()
    lily_dur_string = dur
    if dots:
        for x in range(int(dots)):
            lily_dur_string += "."
    abjad_duration = abjad_duration.from_lilypond_duration_string(lily_dur_string)
    noteheads = []
    for child in mei_chord:
        noteheads.append(mei_note_to_abjad_note(child))
    abjad_chord = Chord(noteheads,abjad_duration)
    return abjad_chord

def mei_element_to_abjad_leaf(mei_element):
    if mei_element.tag == 'rest':
        return mei_rest_to_abjad_rest(mei_element)
    elif mei_element.tag == 'note':
        return mei_note_to_abjad_note(mei_element)
    elif mei_element.tag == 'chord':
        return mei_chord_to_abjad_chord(mei_element)

def mei_layer_to_abjad_voice(mei_layer):
    abjad_voice = Voice()
    for child in mei_layer:
        abjad_voice.append(mei_element_to_abjad_leaf(child))
    return abjad_voice

def mei_staff_to_abjad_staff(mei_staff):
    abjad_staff = Staff()
    for layer in mei_staff:
        abjad_staff.append(mei_layer_to_abjad_voice(layer))
    return abjad_staff

def mei_section_to_abjad_score(mei_section):
    if len(mei_section) == 0:
        return Score()
    abjad_score = Score()
    score_def = mei_section[0]
    mei_global_staff_group = score_def[0]
    staffs = mei_section[1:]
    for element in mei_global_staff_group:
        if element.tag == 'staffDef':
            staff_index = int(element.get('n')) - 1
            abjad_staff = mei_staff_to_abjad_staff(staffs[staff_index])
            abjad_score.append(abjad_staff)
        elif element.tag == 'staffGrp':
            abjad_staff_group = StaffGroup()
            for staffDef in element:
                staff_index = int(staffDef.get('n')) - 1
                abjad_staff_group.append(mei_staff_to_abjad_staff(staffs[staff_index]))
            abjad_score.append(abjad_staff_group)
    return abjad_score


def tupletspan_element_to_empty_tuplet(mei_tupletspan):
    numerator = mei_tupletspan.get('numBase')
    duration = str(mei_tupletspan.get('dur'))
    if numerator != None:
        denominator = mei_tupletspan.get('num')
        multiplier = Multiplier(int(numerator), int(denominator))
        return Tuplet(multiplier, [])
    if duration != None:
        dots = mei_tupletspan.get('dots')
        dur_string = duration
        if dots != None:
            for x in range(int(dots)):
                dur_string += '.'
        duration = Duration()
        duration = duration.from_lilypond_duration_string(dur_string)
        return FixedDurationTuplet(duration, [])


def mei_tupletspan_to_abjad_tuplet(mei_tupletspan):
    if isinstance(mei_tupletspan, list):
        # list beginning with tuplet span and continuing with spanned Elements
        # set up the outermost tuplet and components list
        abjad_outermost_tuplet = tupletspan_element_to_empty_tuplet(mei_tupletspan[0])
        tuplet_components = []
        for x,element in enumerate(mei_tupletspan[1:]):
            #iterate through the list; if you hit a tuplet, recurse
            if element.tag == '{}tupletspan'.format(_MEINS):
                plist = element.get('plist').split()
                end_index = x + len(plist) + 1
                recursion_list = [element]
                recursion_list.extend(mei_tupletspan[x:end_index])
                abjad_tuplet = mei_tupletspan_to_abjad_tuplet(recursion_list)
                tuplet_components.append(abjad_tuplet)
            else:
                #convert the element and add it to the list
                mei_element = mei_element_to_abjad_leaf(element)
                tuplet_components.append(mei_element)
        abjad_outermost_tuplet.extend(tuplet_components)
        abjad_outermost_tuplet = abjad_outermost_tuplet.to_fixed_duration_tuplet()
        return abjad_outermost_tuplet
    elif hasattr(mei_tupletspan, 'xpath'):
        return tupletspan_element_to_empty_tuplet(mei_tupletspan)
    else:
        raise AssertionError("Input argument isn't a list or Element.")
        