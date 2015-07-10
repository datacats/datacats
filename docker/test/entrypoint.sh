#!/bin/bash
service docker start
while ! docker ps > /dev/null 2>&1; do 
    sleep 0.01
done
export HOME=~datacats/
cd /datacats
python setup.py develop
echo 'source /home/datacats/venv/bin/activate' > /home/datacats/.bash_profile
sudo -u datacats "$@"
