# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from datacats import docker

def volume_containers_exist(container_names):
    """
    Return True if we're not running boot2docker or if all container_names
    are present
    """
    # We don't use data only containers on non-boot2docker
    if not docker.is_boot2docker():
        return True

    # Inspect returns None if the container doesn't exist.
    return all(docker.inspect_container(x) for x in container_names)
