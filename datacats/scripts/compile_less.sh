#!/bin/bash


lessc /project/target/ckan/ckan/public/base/less/main.less \
> /project/target/ckan/ckan/public/base/css/main.debug.css

#TODO: We should actually minify
lessc /project/target/ckan/ckan/public/base/vendor/bootstrap/less/bootstrap.less\
 > /project/target/ckan/ckan/public/css/bootstrap.min.css

cp /project/target/ckan/ckan/public/base/css/main.debug.css /project/target/ckan/ckan/public/base/css/main.css