from __future__ import absolute_import

from os import environ

from docker import Client

docker_host = environ.get('DOCKER_HOST', 'unix://var/run/docker.sock')
docker = Client(base_url=docker_host)
