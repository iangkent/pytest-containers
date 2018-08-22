import subprocess
from collections import namedtuple
from docker.constants import (DEFAULT_TIMEOUT_SECONDS)
from ..api.stack import StackApiMixin


ProcessResult = namedtuple('ProcessResult', 'stdout stderr')


def start_process(base_dir, options):
    proc = subprocess.Popen(
        ['docker'] + options,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=base_dir)
    print("Running process: %s" % proc.pid)
    return proc


def wait_on_process(proc, returncode=0):
    stdout, stderr = proc.communicate()
    if proc.returncode != returncode:
        print("Stderr: {}".format(stderr))
        print("Stdout: {}".format(stdout))
        assert proc.returncode == returncode
    return ProcessResult(stdout.decode('utf-8'), stderr.decode('utf-8'))


class CLIClient(StackApiMixin):
    """
    A low-level client for the Docker Engine CLI.

    Args:
        base_dir (str): path to base directory.

    Example:
        >>> import client
        >>> client = client.CLIClient(base_dir='')
        >>> client.version()
    """
    def __init__(self, timeout=DEFAULT_TIMEOUT_SECONDS):
        self.timeout = timeout
        self.base_dir = 'fixtures'

    def dispatch(self, options, project_options=None, returncode=0):
        project_options = project_options or []
        proc = start_process(self.base_dir, project_options + options)
        return wait_on_process(proc, returncode=returncode)

    def version(self):
        """
        Returns version information from the server. Similar to the ``docker version`` command.
        Returns:
            (dict): The server version information.
        """
        result = self.dispatch(['version', '--format', '{{json .}}'], returncode=0)
        return result.stdout
