#!/usr/bin/env python

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
        """,
    cmdclass={'install': DataCatsInstall},
    )

