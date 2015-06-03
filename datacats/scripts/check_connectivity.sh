#!/bin/bash
wget -q --spider https://pypi.python.org/simple || { echo "Couldn't connect to PyPi. Is your DNS configured correctly?"; exit 1; }
