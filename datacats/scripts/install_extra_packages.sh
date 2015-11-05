#!/bin/bash

source /usr/lib/ckan/bin/activate
pip install ckanapi
pip install -e git+https://github.com/ckan/ckan-service-provider#egg=ckanserviceprovider
