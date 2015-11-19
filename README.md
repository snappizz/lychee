# Lychee

*Lychee* is an MEI document manager.

## License

*Lychee* is copyrighted according to the terms of the GNU GPLv3+. A copy of the license is held in
the file called "LICENSE."

## Python 2 and 3; CPython and PyPy

For the nCoda prototype, with a targeted launch in September 2016, we're targeting the PyPy 4.0
series as our runtime environment. This is a Python 2 environment. We will not hold ourselves to
compatibility with CPython or Python 3, but we should attempt to write portable code when possible.

You can download Pypy from http://pypy.org/download.html.

Lychee will primarily target Python 3 for the first nCoda milestone after a Python 3.3 compatible
PyPy interpreter becomes available.

## Install for Development

These instructions will produce a virtualenv for use with Lychee only. If you plan to use Lychee
with the *Fujian* PyPy server and *Julius*, you must also follow the instructions below in the
"Install with Fujian" section. You can install *Fujian* at any time; it simply adds packages to the
virtualenv.

1. Set up a virtualenv and activate it.
    1. ``virtualenv -p /path/to/pypy /path/to/virtualenv``
    1. ``source /path/to/virtualenv/bin/activate``
1. Update the default ``pip`` and ``setuptools``, which otherwise may not be capable of installing
   the dependencies: ``pip install -U pip setuptools``.
1. Temporarily comment the repository-based dependencies (Abjad and Lychee) in "pip_freeze_pypy40".
1. Run ``pip install -r pip_freeze_pypy40`` to install the dependencies.
1. Install Abjad.
   1. Check https://pypi.python.org/pypi/Abjad to see if Abjad 2.17 has been released. If so, run
      ``pip install Abjad`` to install it.
   1. Otherwise clone the Abjad repository (*not* into the ``lychee`` directory) from
      https://github.com/Abjad/abjad, checkout commit 7e3af7f66, then install it by running
      ``pip install -e .`` in the abjad directory.
1. Then install Lychee by running ``pip install -e .`` in the Lychee directory.
1. Finally, run ``py.test`` in the Lychee directory to run the automated test suite, and make
   sure that nothing is broken *before* you even start developing!

## Install with Fujian

These instructions will produce a virtualenv for use with Lychee and *Fujian* together, which may
be used as a back-end for the *Julius* nCoda user interface.

1. Set up a Lychee virtualenv by following the steps in the "Install for Development" section.
1. Clone *Fujian* (*not* into the Lychee directory) from git@jameson.adjectivenoun.ca:ncoda/fujian.git
1. Checkout the "ncoda" branch: ``git checkout ncoda``. This branch has a minor change that allows
   Lychee to run, which should not be pushed to GitHub. (If we do accidentally push it to GitHub,
   it's not a problem, just useless to everyone not using *Fujian* with nCoda).
1. Run ``pip install "tornado<5"`` (with the double quote marks) to install *Tornado*.
1. Run ``pip install -e .`` in the ``fujian`` directory to install *Fujian*.

## Run with Fujian

Start the Lychee/*Fujian* monstrosity by activating the virtualenv and running ``python -m fujian``
from any directory.

## Install for Deployment

Don't. It's not ready yet!
