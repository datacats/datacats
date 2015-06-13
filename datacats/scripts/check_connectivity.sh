#!/bin/bash
wget -q --spider https://pypi.python.org/simple || {
echo $"Couldn't connect to PyPi. Is your DNS configured correctly?";
echo;
echo "If you're using boot2docker, try restarting the VM:";
echo "boot2docker down";
echo "boot2docker up"; exit 1; }
