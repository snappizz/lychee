#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/vcs.py
# Purpose:                Signals for the "vcs" step.
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
Signals for the "vcs" step.
'''

from . import signal


START = signal.Signal(args=['pathnames'], name='vcs.START')
'''
Emitted by the :class:`WorkflowManager` to begin the "vcs" stage.

:kwarg pathnames: A list of pathnames that were modified in the most recent write-to-disk.
:type pathnames: list of str
'''


VCS_DISABLED = signal.Signal(name='vcs.VCS_DISABLED')
'''
Emitted when the VCS system has been disabled by configuration. This should be followed immediately
by the :const:`FINISHED` signal.
'''


INIT = signal.Signal(name='vcs.INIT', args=['repodir'])
'''
This signal is emitted to cause a repository initialization. Such initialization may consist either
of creating a new, empty local repository, of cloning a remote repository, or otherwise initializing
an existing repository.

.. note:: This signal is emitted before every :const:`ADD` and :const:`COMMIT`, so VCS implementation
    modules (1) can and should use this signal to perform any initialization, rather than doing it
    on Lychee startup; and (2) must not cause any harm when this signal is emitted with a repository
    that is already initialized.

:kwarg repodir: The directory to the repository that will be initialized.
:type repodir: str
'''


ADD = signal.Signal(name='vcs.ADD', args=['pathnames'])
'''
This signal is emitted to cause files to be added to the VCS.

:kwarg pathnames: The pathnames modified for this commit.
:type pathnames: list of str
'''


COMMIT = signal.Signal(name='vcs.COMMIT', args=['message'])
'''
This signal is emitted to cause a new commit.

:kwarg message: An optional commit message.
:type message: str
'''


FINISHED = signal.Signal(name='vcs.FINISHED')
'''
This signal is emitted by the :class:`WorkflowManager` once it gains control flow after the "vcs"
step has finished.
'''


ERROR = signal.Signal(name='vcs.ERROR')
'''
This signal is emitted when an error occurs during the "vcs" stage.
'''
