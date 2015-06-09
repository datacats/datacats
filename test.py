from docker.client import Client
from docker.utils import kwargs_from_env

kwargs = kwargs_from_env()

kwargs['tls'].verify = False

client = Client(**kwargs)
print client.version()
