#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/workflow.py
# Purpose:                Control the workflow progression through an "action."
#
# Copyright (C) 2015 Christopher Antila
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
Control the workflow progression through an "action."
'''


import lychee
from lychee import converters
from lychee.signals import inbound, document, vcs, outbound


class WorkflowManager(object):
    '''
    It manages the workflow.
    '''

    # statusses
    _PRESTART = 0
    _INBOUND_PRECONVERSION = 1
    _INBOUND_CONVERSION_STARTED = 2
    _INBOUND_CONVERSION_FINISHED = 3
    _INBOUND_CONVERSION_ERROR = 4
    _INBOUND_PREVIEWS = 5
    _INBOUND_VIEWS_STARTED = 6
    _INBOUND_VIEWS_FINISHED = 7
    _INBOUND_VIEWS_ERROR = 8
    _DOCUMENT_PRESTART = 100
    _DOCUMENT_STARTED = 101
    _DOCUMENT_FINISHED = 102
    _DOCUMENT_ERROR = 103
    _VCS_PRESTART = 300
    _VCS_STARTED = 301
    _VCS_FINISHED = 302
    _VCS_ERROR = 303
    _OUTBOUND_PRESTART = 200
    _OUTBOUND_VIEWS_STARTED = 202
    _OUTBOUND_VIEWS_FINISHED = 203
    _OUTBOUND_VIEWS_ERROR = 204
    _OUTBOUND_CONVERSIONS_STARTED = 205
    _OUTBOUND_CONVERSIONS_FINISHED = 206
    _OUTBOUND_CONVERSIONS_ERROR = 207
    _OUTBOUND_FINISHING = 208

    # connections
    # NB: they'll be connected as SIGNAL.connect(self.whatever)
    _CONNECTIONS = ((inbound.CONVERSION_STARTED, '_inbound_conversion_started'),
                    (inbound.CONVERSION_FINISH, '_inbound_conversion_finish'),
                    (inbound.CONVERSION_FINISHED, '_inbound_conversion_finished'),
                    (inbound.CONVERSION_ERROR, '_inbound_conversion_error'),
                    (inbound.VIEWS_STARTED, '_inbound_views_started'),
                    (inbound.VIEWS_FINISH, '_inbound_views_finish'),
                    (inbound.VIEWS_FINISHED, '_inbound_views_finished'),
                    (inbound.VIEWS_ERROR, '_inbound_views_error'),
                    (document.STARTED, '_document_started'),
                    (document.FINISH, '_document_finish'),
                    (document.FINISHED, '_document_finished'),
                    (document.ERROR, '_document_error'),
                    (vcs.STARTED, '_vcs_started'),
                    (vcs.FINISH, '_vcs_finish'),
                    (vcs.FINISHED, '_vcs_finished'),
                    (vcs.ERROR, '_vcs_error'),
                    (outbound.VIEWS_STARTED, '_outbound_views_started'),
                    (outbound.VIEWS_FINISH, '_outbound_views_finish'),
                    (outbound.VIEWS_FINISHED, '_outbound_views_finished'),
                    (outbound.VIEWS_ERROR, '_outbound_views_error'),
                    (outbound.CONVERSION_STARTED, '_outbound_conversion_started'),
                    (outbound.CONVERSION_FINISH, '_outbound_conversion_finish'),
                    (outbound.CONVERSION_FINISHED, '_outbound_conversion_finished'),
                    (outbound.CONVERSION_ERROR, '_outbound_conversion_error'),
                   )

    def __init__(self, dtype, doc, **kwargs):
        self._status = WorkflowManager._PRESTART

        # set instance settings
        # inbound data type
        self._i_dtype = dtype.lower()
        # inbound document
        self._i_doc = doc  #.lower()
        # inbound document after conversion
        self._converted = None
        # inbound information from the "views" module
        self._i_views = None

        # list of output "dtype" required
        self._o_dtypes = []
        # mapping from dtype to its outbound views_info
        self._o_views_info = {}
        # mapping from dtype to its outbound converted form
        self._o_converted = {}
        # dtype of the currently running outbound converter
        self._o_running_converter = None

        for signal, slot in WorkflowManager._CONNECTIONS:
            signal.connect(getattr(self, slot))

    def end(self):
        '''
        Disconnect all signals from this :class:`WorkflowManager` so it can be deleted. Does not
        attempt to ensure running processes are allowed to finish.
        '''
        for signal, slot in WorkflowManager._CONNECTIONS:
            signal.disconnect(getattr(self, slot))
        self._flush_inbound_converters()
        self._flush_outbound_converters()

    def run(self):
        '''
        Runs the "action" as required.
        '''
        try:
            self._run()
        finally:
            self.end()

    def _run(self):
        '''
        Actually does what :meth:`run` says it does. The other method is intended as a wrapper for
        this method, to ensure that :meth:`end` is always run, regardless of how this method exits.
        '''
        next_step = '(WorkflowManager continues to the next step)\n------------------------------------------\n'

        # Inbound -------------------------------------------------------------
        if self._status is not WorkflowManager._PRESTART:
            lychee.log('ERROR starting the action')
            return

        self._status = WorkflowManager._INBOUND_PRECONVERSION
        self._choose_inbound_converter()
        inbound.CONVERSION_START.emit(document=self._i_doc)

        if self._status is not WorkflowManager._INBOUND_CONVERSION_FINISHED:
            if self._status is not WorkflowManager._INBOUND_CONVERSION_ERROR:
                lychee.log('ERROR during inbound conversion')
            return
        lychee.log(next_step)

        self._status = WorkflowManager._INBOUND_PREVIEWS
        self._choose_inbound_views()
        inbound.VIEWS_START.emit(dtype=self._i_dtype, doc=self._i_doc, converted=self._converted)

        if self._status is not WorkflowManager._INBOUND_VIEWS_FINISHED:
            lychee.log('ERROR during inbound views processing')
            return
        lychee.log(next_step)

        # Document ------------------------------------------------------------
        self._status = WorkflowManager._DOCUMENT_PRESTART
        document.START.emit(converted=self._converted)

        if self._status is not WorkflowManager._DOCUMENT_FINISHED:
            if self._status is not WorkflowManager._DOCUMENT_ERROR:
                lychee.log('ERROR during "document" step')
            return
        lychee.log(next_step)

        # VCS -----------------------------------------------------------------
        self._status = WorkflowManager._VCS_PRESTART
        vcs.START.emit(pathnames=self._modified_pathnames)

        if self._status is not WorkflowManager._VCS_FINISHED:
            if self._status is not WorkflowManager._VCS_ERROR:
                lychee.log('ERROR during "vcs" step')
            return
        lychee.log(next_step)

        # Outbound ------------------------------------------------------------
        self._status = WorkflowManager._OUTBOUND_PRESTART

        # determine which formats are required
        self._o_dtypes = lychee.the_registrar.get_registered_formats()
        lychee.log('Currently registered outbound dtypes: {}'.format(self._o_dtypes))

        # do the views processing
        successful_dtypes = []
        for each_dtype in self._o_dtypes:
            outbound.VIEWS_START.emit(dtype=each_dtype)
            if self._status is WorkflowManager._OUTBOUND_VIEWS_ERROR:
                self._status = WorkflowManager._OUTBOUND_VIEWS_STARTED
                continue
            elif each_dtype not in self._o_views_info:
                lychee.log('ERROR: {} did not return outbound views info'.format(each_dtype))
                continue
            else:
                successful_dtypes.append(each_dtype)

        # see if everything worked
        if self._status is WorkflowManager._OUTBOUND_VIEWS_ERROR:
            # can't happen?
            pass
        if len(successful_dtypes) != len(self._o_dtypes):
            if 0 == len(successful_dtypes):
                outbound.VIEWS_ERROR.emit(msg='No registered outbound dtypes passed through views processing')
            else:
                lychee.log('ERROR: some registered outbound dtypes failed views processing')
                self._o_dtypes = successful_dtypes
        else:
            outbound.VIEWS_FINISHED.emit()

        if self._status is WorkflowManager._OUTBOUND_VIEWS_ERROR:
            return
        lychee.log(next_step)

        # do the outbound conversion
        successful_dtypes = []
        for each_dtype in self._o_dtypes:
            self._choose_outbound_converter(each_dtype)
            self._o_running_converter = each_dtype
            outbound.CONVERSION_START.emit(views_info=self._o_views_info[each_dtype],
                                           document=self._converted)
            if self._status is WorkflowManager._OUTBOUND_CONVERSIONS_ERROR:
                self._status = WorkflowManager._OUTBOUND_CONVERSIONS_STARTED
                continue
            else:
                successful_dtypes.append(each_dtype)

        # see if everything worked
        if self._status is WorkflowManager._OUTBOUND_CONVERSIONS_ERROR:
            # can't happen?
            pass
        if len(successful_dtypes) != len(self._o_dtypes):
            if 0 == len(successful_dtypes):
                outbound.CONVERSION_ERROR.emit(msg='No outbound converters succeeded')
            else:
                lychee.log('ERROR: some registered outbound dtypes failed conversion')
                self._o_dtypes = successful_dtypes

        # emit one signal per things returned
        for each_dtype in successful_dtypes:
            outbound.CONVERSION_FINISHED.emit(dtype=each_dtype,
                                              placement=self._o_views_info[each_dtype],
                                              document=self._o_converted[each_dtype])

    # ----

    def _flush_inbound_converters(self):
        '''
        Clear any inbound converters that may be connected.
        '''
        for each_converter in converters.INBOUND_CONVERTERS.values():
            inbound.CONVERSION_START.disconnect(each_converter)

    def _flush_outbound_converters(self):
        '''
        Clear any outbound converters that may be connected.
        '''
        for each_converter in converters.OUTBOUND_CONVERTERS.values():
            outbound.CONVERSION_START.disconnect(each_converter)

    def _choose_inbound_converter(self):
        '''
        Choose an inbound converter based on self._i_dtype.
        '''
        if self._i_dtype:
            if self._i_dtype in converters.INBOUND_CONVERTERS:
                inbound.CONVERSION_START.connect(converters.INBOUND_CONVERTERS[self._i_dtype])
            else:
                inbound.CONVERSION_ERROR.emit(msg='Invalid "dtype"')
        else:
            inbound.CONVERSION_ERROR.emit(msg='Missing "dtype"')

    def _choose_inbound_views(self):
        '''
        Choose an inbound views function based on ??? and the conversion result.
        '''
        pass

    def _choose_outbound_converter(self, dtype):
        '''
        Choose an outbound converter based on the "dtype" argument. This should be called once for
        every outbound converter format required.
        '''
        self._flush_outbound_converters()
        if dtype in converters.OUTBOUND_CONVERTERS:
            outbound.CONVERSION_START.connect(converters.OUTBOUND_CONVERTERS[dtype])
        else:
            outbound.CONVERSION_ERROR.emit(msg='Invalid "dtype" ({})'.format(dtype))

    # ----

    def _inbound_conversion_started(self, **kwargs):
        lychee.log('inbound conversion started')
        lychee.log('inbound conversion started')
        self._status = WorkflowManager._INBOUND_CONVERSION_STARTED

    def _inbound_conversion_finish(self, converted, **kwargs):
        lychee.log('inbound conversion finishing')
        if self._status is WorkflowManager._INBOUND_CONVERSION_STARTED:
            if converted is None:
                inbound.CONVERSION_ERROR.emit(msg='Inbound converter did not return L-MEI document')
            else:
                lychee.log('\t(we got "{}")'.format(converted))
                self._converted = converted
                self._status = WorkflowManager._INBOUND_CONVERSION_FINISHED
        else:
            lychee.log('ERROR during inbound conversion')
        inbound.CONVERSION_FINISHED.emit()

    def _inbound_conversion_finished(self, **kwargs):
        '''
        Called when inbound.CONVERSION_FINISHED is emitted, for logging and debugging.
        '''
        lychee.log('inbound conversion finished')

    def _inbound_conversion_error(self, **kwargs):
        self._status = WorkflowManager._INBOUND_CONVERSION_ERROR
        if 'msg' in kwargs:
            lychee.log(kwargs['msg'])
        else:
            lychee.log('ERROR during inbound conversion')

    def _inbound_views_started(self, **kwargs):
        lychee.log('inbound views started')
        self._status = WorkflowManager._INBOUND_VIEWS_STARTED

    def _inbound_views_finish(self, views_info, **kwargs):
        lychee.log('inbound views finishing'.format(kwargs))
        if self._status is WorkflowManager._INBOUND_VIEWS_STARTED:
            if views_info is None:
                inbound.VIEWS_ERROR.emit(msg='Inbound views processing did not return views_info')
            else:
                lychee.log('\t(we got "{}")'.format(views_info))
                self._i_views = views_info
                self._status = WorkflowManager._INBOUND_VIEWS_FINISHED
        else:
            lychee.log('ERROR during inbound views processing')
        inbound.VIEWS_FINISHED.emit()

    def _inbound_views_finished(self, **kwargs):
        '''
        Called when inbound.VIEWS_FINISHED is emitted, for logging and debugging.
        '''
        lychee.log('inbound views finished')

    def _inbound_views_error(self, **kwargs):
        self._status = WorkflowManager._INBOUND_VIEWS_ERROR
        if 'msg' in kwargs:
            lychee.log(kwargs['msg'])
        else:
            lychee.log('ERROR during inbound views processing')

    # ----

    def _document_started(self, **kwargs):
        lychee.log('document started')
        self._status = WorkflowManager._DOCUMENT_STARTED

    def _document_finish(self, pathnames, **kwargs):
        lychee.log('document finishing; modified {}'.format(pathnames))
        if self._status is WorkflowManager._DOCUMENT_STARTED:
            if 5 is None:  # TODO: put in the appropriate arg here
                document.ERROR.emit(msg='Document processing did not return views_info')
            else:
                self._modified_pathnames = pathnames
                self._status = WorkflowManager._DOCUMENT_FINISHED
        else:
            lychee.log('ERROR during document processing')
        document.FINISHED.emit()

    def _document_finished(self, **kwargs):
        '''
        Called when document.FINISHED is emitted, for logging and debugging.
        '''
        lychee.log('document processing finished')

    def _document_error(self, **kwargs):
        self._status = WorkflowManager._DOCUMENT_ERROR
        if 'msg' in kwargs:
            lychee.log(kwargs['msg'])
        else:
            lychee.log('ERROR during document processing')

    # ----

    def _vcs_started(self, **kwargs):
        lychee.log('vcs started')
        self._status = WorkflowManager._VCS_STARTED

    def _vcs_finish(self, **kwargs):
        lychee.log('vcs finishing'.format(kwargs))
        if self._status is WorkflowManager._VCS_STARTED:
            if 5 is None:  # TODO: put in the appropriate arg here
                vcs.ERROR.emit(msg='Document processing did not return views_info')
            else:
                self._status = WorkflowManager._VCS_FINISHED
        else:
            lychee.log('ERROR during vcs processing')
        vcs.FINISHED.emit()

    def _vcs_finished(self, **kwargs):
        '''
        Called when vcs.FINISHED is emitted, for logging and debugging.
        '''
        lychee.log('vcs processing finished')

    def _vcs_error(self, **kwargs):
        self._status = WorkflowManager._VCS_ERROR
        if 'msg' in kwargs:
            lychee.log(kwargs['msg'])
        else:
            lychee.log('ERROR during vcs processing')

    # ----

    def _outbound_views_started(self, **kwargs):
        lychee.log('outbound views started')
        self._status = WorkflowManager._OUTBOUND_VIEWS_STARTED

    def _outbound_views_finish(self, dtype, views_info, **kwargs):
        '''
        Slot for outbound.VIEWS_FINISH
        '''
        lychee.log('outbound views finishing'.format(kwargs))
        if self._status is WorkflowManager._OUTBOUND_VIEWS_STARTED:
            self._o_views_info[dtype] = views_info
            self._status = WorkflowManager._OUTBOUND_VIEWS_FINISHED
        else:
            lychee.log('ERROR during outbound views processing')

    def _outbound_views_finished(self, **kwargs):
        '''
        Called when outbound.VIEWS_FINISHED is emitted, for logging and debugging.
        '''
        lychee.log('outbound views finished')

    def _outbound_views_error(self, **kwargs):
        self._status = WorkflowManager._OUTBOUND_VIEWS_ERROR
        if 'msg' in kwargs:
            lychee.log(kwargs['msg'])
        else:
            lychee.log('ERROR during outbound views processing')

    def _outbound_conversion_started(self, **kwargs):
        lychee.log('outbound conversion started')
        self._status = WorkflowManager._OUTBOUND_CONVERSIONS_STARTED

    def _outbound_conversion_finish(self, converted, **kwargs):
        lychee.log('outbound conversion finishing')
        if self._status is WorkflowManager._OUTBOUND_CONVERSIONS_STARTED:
            if converted is None:
                outbound.CONVERSION_ERROR.emit(msg='Outbound converter did not return a document')
            else:
                lychee.log('\t(we got "{}")'.format(converted))
                self._o_converted[self._o_running_converter] = converted
                self._status = WorkflowManager._OUTBOUND_CONVERSIONS_FINISHED
        else:
            lychee.log('ERROR during outbound conversion')

    def _outbound_conversion_finished(self, dtype, placement, document, **kwargs):
        '''
        Called when outbound.CONVERSION_FINISHED is emitted, for logging and debugging.
        '''
        lychee.log('outbound conversion finished\n\tdtype: {}\n\tplacement: {}\n\tdocument: {}\n'.format(dtype, placement, document))

    def _outbound_conversion_error(self, **kwargs):
        self._status = WorkflowManager._OUTBOUND_CONVERSIONS_ERROR
        if 'msg' in kwargs:
            lychee.log(kwargs['msg'])
        else:
            lychee.log('ERROR during outbound conversion')
