from os import path

SCRIPTS_DIR = path.dirname(path.abspath(__file__)) + '/scripts'


def get_script_path(script):
    """
    Gets the path to a shell script.

    :param script: The relative name of the shell script to get (i.e. web.sh)
    """
    return path.join(SCRIPTS_DIR, script)
