#!/usr/bin/env python

from setuptools import setup
import sys

install_requires=[
    'setuptools',
    'docopt',
]

setup(
    name='datacats',
    version='0.1',
    description='The easiest way to develop and deploy CKAN cross-platform.',
    license='AGPL3',
    author='Boxkite',
    author_email='contact@boxkite.ca',
    url='https://github.com/dcats/datacats',
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
        """
    )

