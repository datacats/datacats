#!/bin/bash

source /usr/lib/ckan/bin/activate
cd /project/datapusher
python datapusher/main.py deployment/datapusher_settings.py