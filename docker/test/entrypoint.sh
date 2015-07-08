#!/bin/bash
service docker start
while ! docker ps > /dev/null 2>&1; do 
    sleep 0.01
done
export HOME=~datacats/
source /home/datacats/venv/bin/activate
cd /datacats
python setup.py develop
sudo -u datacats "$@"
