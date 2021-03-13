#!/usr/bin/env python
"""
Lyrebird Voice Changer
Simple and powerful voice changer for Linux, written in GTK 3
(c) Charlotte 2020
"""

import sys
import re
from setuptools import setup

version_regex = r'__version__ = ["\']([^"\']*)["\']'
with open('app/__init__.py', 'r') as f:
    text = f.read()
    match = re.search(version_regex, text)

    if match:
        VERSION = match.group(1)
    else:
        raise RuntimeError("No version number found!")

with open("requirements.txt") as f:
    required = [l for l in f.read().splitlines() if not l.startswith("#")]

extra_options = dict(
    name = 'Lyrebird',
    version=VERSION,
    author = 'Charlotte',
#    author_email = '',
    url = 'https://github.com/charpointer/lyrebird',
    description = 'Simple and powerful voice changer for Linux, written in GTK 3',
    download_url = 'https://github.com/charpointer/lyrebird/releases',
    license = 'MIT License',
    install_requires=required,
    entry_points = {
        'console_scripts': [
            'lyrebird = app.__main__:main']},
    packages = ['app',
                'app.core'],
)

setup(**extra_options)
