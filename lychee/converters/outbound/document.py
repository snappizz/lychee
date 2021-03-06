#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/document_outbound.py
# Purpose:                "Converts" document metadata into an easier format for clients.
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
Export MEI document metadata as JSON objects.

.. warning::
    This module is intended for internal *Lychee* use only, so the API may change without notice.
    If you wish to use this module outside *Lychee*, please contact us to discuss the best way.

.. tip::
    We recommend that you use the converters indirectly.
    Refer to :ref:`how-to-use-converters` for more information.

.. note:: This is an outbound converter that does not emit signals directly. Refer to the
    :mod:`lychee.signals.outbound` module for more information.


Output Sample
-------------

Here is a sample of the data outputted from this module. This includes all possible values, but a
real score is unlikely to do so.

::

    {
        'headers': {
            'fileDesc': {
                'titleStmt': {
                    'title': {
                        'main': 'This is the Main Title',
                        'subordinate': 'This is a subtitle',
                        'abbreviated': 'Main Title',
                        'alternative': 'Sample Document for You',
                    }
                },
                'respStmt': [
                    {
                        'id': 'p1234',
                        'full': 'Danceathon W. Smith',
                        'given': 'Danceathon',
                        'other': 'Wilfreda',
                        'family': 'Smith'
                    },
                    {
                        'id': 'p5678',
                        'full': '卓文萱',
                        'given': '文萱',
                        'other': 'Genie',
                        'family': '卓'
                    },
                ],
                'arranger': {
                    'full': 'Robert W. Smith'
                },
                'composer': {
                    'id': 'p5678'
                },
                'author': { ... },
                'editor': { ... },
                'funder': { ... },
                'librettist': { ... },
                'lyricist': { ... },
                'sponsor': { ... }
                'pubStmt': {
                    'unpub': 'This is an unpublished Lychee-MEI document.'
                }
            }
        },
        'sections': {
            'score_order': ['Sme-s-m-l-e1234567', 'Sme-s-m-l-e9029823'],
            'Sme-s-m-l-e1234567': {
                # things about the section with this "id"
                # NOTE: many more things will be exported later
                'label': 'A',
                # NOTE: in <staffGrp> only @n and @label are exported at the moment
                'staffGrp': [
                    [{'n': '1', 'label': 'Violin I'}, {'n': '2', 'label': 'Violin II'}],
                    {'n': '3', 'label': 'Viola'},
                    [{'n': '4', 'label': 'Violoncello'}, {'n': '5', 'label': 'Contrabasso'}]
                ],
                'last_changeset': '34e92f3e7b17'
            },
            'Sme-s-m-l-e9029823': {
                'label': 'B',
                'staffGrp': [
                    [{'n': '1', 'label': 'Right Hand'}, {'n': '2', 'label': 'Left Hand'}]
                ],
                'last_changeset': '01d9ce76929b'
            },
            'Sme-s-m-l-e9176572': {
                # NOTE: this section has nested sections
                'label': 'C',
                'last_changeset': '8e552c8c9c2f',
                'sections': {
                'score_order': ['Sme-s-m-l-e9029823', 'Sme-s-m-l-e1795937'],
                    'Sme-s-m-l-e9029823': {
                        # NOTE: this section is linked to the one earlier with the same @xml:id
                        'label': 'a',
                        'staffGrp': [
                            [{'n': '1', 'label': 'Right Hand'}, {'n': '2', 'label': 'Left Hand'}]
                        ],
                        'last_changeset': '6074c498c731'
                    },
                    'Sme-s-m-l-e1795937': {
                        'label': 'b',
                        'staffGrp': [
                            [{'n': '1', 'label': 'Right Hand'}, {'n': '2', 'label': 'Left Hand'}]
                        ],
                        'last_changeset': 'fac50d50a9d3'
                    }
                }
            }
        }
    }


Notes about Header Information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following Lychee-MEI, the different members of "title" may be one of the following: main, subordinate,
abbreviated, alternative, translated, uniform. The "main" title will always be included, though it
may be a placeholder.

The "roles" members ("arranger," "composer," and so on) refer to people. They may either use an "id"
field to refer to a user described in the "respStmt" section, or they may contain names.

While the "pubStmt" section is virtually useless at the moment (because Lychee is not aware when
one of its documents becomes published) it is included for completeness. It is required for a
complete and valid MEI document.

Data from the "workDesc" and "revisionDesc" MEI elements will be added later, as peers to the
"fileDesc" member, once they are implemented in Lychee.


Notes about Section Information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The nesting of ``<staffGrp>`` information reflects the nesting of the original elements. The
top-level "staffGrp" member is a list; its elements are either a dict (with at least "n" and "label"
members) or another list (which will likewise contain dicts and lists).

The ``'last_changeset'`` member holds the changeset ID of the most recent changeset in which that
``<section>`` was modified.
'''

from lxml import etree

from lychee.converters.outbound import vcs
from lychee import document
from lychee import exceptions
from lychee.logs import OUTBOUND_LOG as log
from lychee.namespaces import mei, xml
from lychee.signals import outbound


# translatable strings
# ---------------------
# the 'label' for a <section> that doesn't have @label set
_UNNAMED_SECTION_LABEL = '(unnamed)'
# warning message for invalid <persName>
_MISSING_PERS_NAME_DATA = '<persName> is missing required child elements'
# log.warn() when prepare_headers() can't convert some elements
_MISSING_HEADER_DATA = '{}: Some MEI header data is not exported.'.format(__name__)
# warning message for invalid <titleStmt>
_MISSING_TITLE_DATA = '<titleStmt> is missing required child elements'


# non-translatable constants
KNOWN_PERSNAME_TYPES = ('full', 'family', 'given', 'other')  # defined in Lychee-MEI
KNOWN_TITLE_TYPES = ('main', 'subordinate', 'abbreviated', 'alternative')  # defined in Lychee-MEI


def convert(repo_dir, **kwargs):
    '''
    Prepare document metadata in a useful format for clients.

    :param str repo_dir: The absolute pathname to the repository for which to produce data.
    :returns: Information from the internal LMEI document in the format described above.
    :rtype: dict
    :raises: :exc:`lychee.exceptions.OutboundConversionError` when there is a forseeable error.
    '''
    try:
        doc = document.Document(repo_dir)
    except exceptions.HeaderNotFoundError:
        raise OutboundConversionError('{} failed initializing a Document object; stopping conversion'.format(__name__))
    else:
        post = {'headers': prepare_headers(doc)}
        try:
            post['sections'] = prepare_sections(doc, repo_dir)
        except exceptions.SectionNotFoundError:
            raise OutboundConversionError('{} failed to load a <section>; stopping conversion'.format(__name__))
        else:
            return post


def format_person(elem):
    '''
    Given a ``<persName>`` :class:`Element`, prepare it for output as a dictionary.

    :param elem: A ``<persName>`` element to convert.
    :type elem: :class:`lxml.etree._Element`
    :returns: The converted stuff or ``None``.
    :rtype: dict or NoneType

    This function also accepts ``None`` to help simplify functions that call it. The only time
    ``None`` is returned is when ``elem`` is ``None`` to begin with.
    '''
    post = {}

    if elem is None:
        post = None

    elif elem.get('nymref') is not None:
        nymref = elem.get('nymref')
        if nymref.startswith('#'):
            nymref = nymref[1:]
        post = {'id': nymref}

    else:
        if elem.get(xml.ID) is not None:
            post['id'] = elem.get(xml.ID)
        for person in elem.findall('./{}'.format(mei.PERS_NAME)):
            pers_type = person.get('type')
            if pers_type in KNOWN_PERSNAME_TYPES:
                post[pers_type] = person.text

        if len(post) < 2:
            raise exceptions.LycheeMEIWarning(_MISSING_PERS_NAME_DATA)

    return post


def format_title_stmt(elem):
    '''
    Given a ``<titleStmt>`` :class:`Element`, prepare it for output as a dictionary.

    :param elem: A ``<titleStmt>`` element to convert.
    :type elem: :class:`lxml.etree._Element`
    :returns: The converted stuff or ``None``.
    :rtype: dict or NoneType

    This function also accepts ``None`` to help simplify functions that call it. The only time
    ``None`` is returned is when ``elem`` is ``None`` to begin with.
    '''
    post = {}

    if elem is None:
        post = None

    else:
        for title in elem.findall('./{}'.format(mei.TITLE)):
            title_type = title.get('type')
            if title_type in KNOWN_TITLE_TYPES:
                post[title_type] = title.text

        if len(post) == 0:
            raise exceptions.LycheeMEIWarning(_MISSING_TITLE_DATA)

    return post


def prepare_headers(doc):
    '''
    Given a :class:`Document`, prepare the "headers" portion of this module's output.

    :param doc: The :class:`Document` from which to extract MEI header data.
    :type doc: :class:`lychee.document.Document`
    :returns: A dictionary with relevant header data.
    :rtype: dict

    This function returns the "headers" dictionary described at the top of
    :mod:`~lychee.converters.document_outbound`.
    '''

    fileDesc = {}

    title_stmt = doc.get_from_head('titleStmt')
    if title_stmt:
        with log.debug('convert <titleStmt>') as action:
            try:
                fileDesc['titleStmt'] = format_title_stmt(title_stmt[0])
            except exceptions.LycheeMEIWarning:
                action.failure(_MISSING_HEADER_DATA)
                fileDesc['titleStmt'] = {}

    # TODO: this should be in a function
    respStmt = []
    respStmtElem = doc.get_from_head('respStmt')
    if respStmtElem:
        respStmtElem = respStmtElem[0]
        for elem in respStmtElem:
            with log.debug('convert <respStmt> subelement') as action:
                if mei.NAME == elem.tag:
                    # TODO: this may be insufficient in the long term
                    respStmt.append({'full': elem.text})
                elif mei.PERS_NAME == elem.tag:
                    try:
                        respStmt.append(format_person(elem))
                    except exceptions.LycheeMEIWarning:
                        action.failure(_MISSING_HEADER_DATA)
                else:
                    action.failure('Unexpected element found in <respStmt>: {tag_name}', tag_name=elem.tag)

        fileDesc['respStmt'] = respStmt

    # TODO: this should be in a function
    roles = ('arranger', 'author', 'composer', 'editor', 'funder', 'librettist', 'lyricist', 'sponsor')  # TODO: this should be module-level
    for role in roles:
        with log.debug('convert {role} in header', role=role):
            person = doc.get_from_head(role)
            if person:
                # TODO: is it enough to take only the first?
                person = person[0].find('./{}'.format(mei.PERS_NAME))
                try:
                    fileDesc[role] = format_person(person)
                except exceptions.LycheeMEIWarning:
                    action.failure(_MISSING_HEADER_DATA)
            else:
                action.success('no {role} in this score')

    pubStmt = {'unpub': 'This is an unpublished Lychee-MEI document.'}
    fileDesc['pubStmt'] = pubStmt

    return {'fileDesc': fileDesc}


def parse_staffGrp(sect_id, staffGrp):
    '''
    '''
    post = []

    for elem in staffGrp:
        with log.debug('convert element in <scoreDef>') as action:
            if mei.STAFF_GRP == elem.tag:
                post.append(parse_staffGrp(sect_id, elem))
            elif mei.STAFF_DEF == elem.tag:
                post.append({'n': elem.get('n'), 'label': elem.get('label')})
            else:
                action.failure(
                    'Section {sect_id} has unexpected <{tag_name}> in its <scoreDef>',
                    sect_id=sect_id,
                    tag_name=elem.tag)

    return post


def find_last_changeset(section_id, revlog):
    '''
    Find the hash of the most changeset in which a file was modified.

    :param str section_id: The @xml:id of a ``<section>``.
    :param dict revlog: The outpuf of :func:`vcs.convert_helper`
    :returns: The hash of the that file's last changeset.
    :rtype: str

    If the file is not found in a changeset, an empty string is returned.
    '''
    for cset in reversed(revlog['history']):
        if section_id in revlog['changesets'][cset]['files']:
            return cset

    return ''


def prepare_sections_inner(doc, section_ids, vcs_data):
    '''
    Helper function for :func:`prepare_sections` that can be called recursively when the hierarchy
    of ``<section>`` elements is not flat.

    :param doc: The :class:`Document` from which to extract MEI header data.
    :type doc: :class:`lychee.document.Document`
    :param section_ids: The @xml:id attributes of the ``<section>`` elements, in score order.
    :param vcs_data: The output of :func:`lychee.converters.vcs.convert_helper`.
    :type vcs_data: dict
    :type section_ids: list of str
    :returns: A dictionary with relevant header data.
    :rtype: dict

    .. note:: Do not call this function directly; use :func:`prepare_sections`.
    '''
    post = {'score_order': []}

    for each_id in section_ids:
        post['score_order'].append(each_id)
        section = doc.get_section(each_id)

        sect_dict = {'label': section.get('label', _UNNAMED_SECTION_LABEL)}

        staffGrp = section.find('./{}/{}'.format(mei.SCORE_DEF, mei.STAFF_GRP))
        if staffGrp is None:
            # this <section> contains other <section>s
            ids = [e.get('target')[:-4] for e in section.findall('./{}'.format(mei.SECTION))]
            sect_dict['sections'] = prepare_sections_inner(doc, ids, vcs_data)
        else:
            sect_dict['staffGrp'] = parse_staffGrp(each_id, staffGrp)

        sect_dict['last_changeset'] = find_last_changeset(each_id, vcs_data)

        post[each_id] = sect_dict

    return post


def prepare_sections(doc, repo_dir):
    '''
    Given a :class:`Document`, prepare the "sections" portion of this module's output.

    :param doc: The :class:`Document` from which to extract MEI header data.
    :type doc: :class:`lychee.document.Document`
    :param str repo_dir: The absolute pathname to the repository for which to produce data.
    :returns: A dictionary with relevant header data.
    :rtype: dict

    This function returns the "sections" dictionary described at the top of
    :mod:`~lychee.converters.document_outbound`.
    '''
    section_ids = doc.get_section_ids()
    vcs_data = vcs.convert_helper(repo_dir)
    return prepare_sections_inner(doc, section_ids, vcs_data)
