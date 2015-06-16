#!/bin/bash
sed "/^ckan.plugins = / s/$/ $1/" /project/development.ini > /project/development.ini
