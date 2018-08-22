import docker
from .cli.client import CLIClient
from .models.stacks import StackCollection
                                                                                
    
class DockerClient(docker.DockerClient):
    """
    A client for communicating with a Docker server via API or CLI.
    This is an extension to docker-py to support stack objects
    """
    
    def __init__(self, *args, **kwargs):
        super(DockerClient, self).__init__(*args, **kwargs)
        self.cli = CLIClient()

    @property
    def stacks(self):
        """
        An object for managing stacks on the cluster. See the
        :doc:`stacks documentation <stacks>` for full details.
        """
        return StackCollection(client=self)
    

from_env = DockerClient.from_env
                
