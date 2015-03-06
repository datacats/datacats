#!/usr/bin/env python

# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from setuptools import setup
from setuptools.command.install import install
import sys

class DataCatsInstall(install):
    def run(self):
        install.run(self)
        from datacats.cli.pull import pull
        print 'Downloading images. This may take a few minutes.'
        pull({})

install_requires=[
    'setuptools',
    'docopt',
    'docker-py',
    'requests',
]

setup(
    name='datacats',
    version='0.1',
    description='Developer tools for CKAN data catalogs built on Docker',
    license='AGPL3',
    author='Boxkite',
    author_email='contact@boxkite.ca',
    url='https://github.com/boxkite/datacats',
    packages=[
        'datacats',
        'datacats.tests',
        'datacats.cli',
        ],
    install_requires=install_requires,
    test_suite='datacats.tests',
    zip_safe=False,
    entry_points = """
        [console_scripts]
        datacats=datacats.cli.main:main
        """,
    cmdclass={'install': DataCatsInstall},
    )

