# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

import time
import socket

from datacats.docker import inspect_container

class ServiceTimeout(Exception):
    pass

RETRY_DELAY_SECONDS = 0.1
READ_TIMEOUT_SECONDS = 0.1

def wait_for_service_available(container, host, port, timeout):
    """
    Wait up to timeout seconds for service at host:port
    to start.

    Returns True if service becomes available, False if the
    container stops or raises ServiceTimeout if timeout is
    reached.
    """
    start = time.time()
    remaining = timeout
    while True:
        remaining = start + timeout - time.time()
        if remaining < 0:
            raise ServiceTimeout
        s = socket.socket(socket.AF_INET)
        s.settimeout(READ_TIMEOUT_SECONDS)
        try:
            s.connect((host, port))
            s.recv(1)
        except socket.timeout:
            return True
        except socket.error:
            pass
        finally:
            s.close()
        if not inspect_container(container)['State']['Running']:
            return False

        remaining = start + timeout - time.time()
        delay = max(0, min(RETRY_DELAY_SECONDS, remaining))
        time.sleep(delay)
    raise ServiceTimeout
