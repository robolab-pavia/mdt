#!/usr/bin/env python

from setuptools import setup

exec(open('mdt/version.py').read())
setup(
    name='mdt-viewer',
    version=__version__
)
