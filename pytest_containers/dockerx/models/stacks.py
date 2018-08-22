from docker.models.resource import Collection, Model
from docker import errors


class Stack(Model):
    """
    A Docker stack.
    """
    id_attribute = 'Name'

    @property
    def name(self):
        """
        The name of the stack.
        """
        if self.attrs.get('Name') is not None:
            return self.attrs['Name'].lstrip('/')
            
    @property
    def compose_file(self):
        """
        The compose file of the stack.
        """
        return 'compose.yml'

    @property
    def services(self):
        """
        The services in the stack, as a list of
        :py:class:`~docker.models.services.Service` objects.
        """
        # docker stack services webapp
        # docker service ls --filter label=com.docker.stack.namespace=self.name
        filters = {}
        filters['label'] = 'com.docker.stack.namespace={}'.format(self.name)
        services = self.client.services.list(filters=filters)
        return services

    @property
    def tasks(self):
        """
        The tasks in the stack, as a list of
        :py:class:`~docker.models.tasks.Task` objects.
        """
        # docker stack ps self.name
        filters = {}
        filters['label'] = 'com.docker.stack.namespace={}'.format(self.name)
        tasks = self.client.api.tasks(filters=filters)
        return tasks
                
    def remove(self, **kwargs):
        """
        Remove this stack. Similar to the ``docker stack rm`` command.
        """
        return self.client.cli.remove_stack(self.name, **kwargs)
    

class StackCollection(Collection):
    """
    Stacks on the Docker server.
    """
    model = Stack

    def deploy(self, name, compose_file='compose.yml', **kwargs):
        """
        Deploy a stack. Similar to ``docker stack deploy``.

        Args:
            name (str): The name for this stack.
            compose_file (str): Path to a Compose file.
            prune (bool): Prune services that are no longer referenced.
            resolve_image (str): Query the registry to resolve image digest and supported platforms ("always"|"changed"|"never")
                                 (default "always")
            with_registry_auth (bool): Send registry authentication details to Swarm agents.
        Returns:
            A :py:class:`Stack` object.
        """
        resp = self.client.cli.deploy_stack(name=name, compose_file=compose_file, **kwargs)
        return self.prepare_model(resp)
    
    def get(self, stack_name):
        """
        Get a stack by name.

        Args:
            stack_name (str): Stack name.

        Returns:
            A :py:class:`Stack` object.
        Raises:
            :py:class:`docker.errors.NotFound`
                If the stack does not exist.
        """
        stacks = self.list()
        stack = next((x for x in stacks if x.name == stack_name), None)
        if stack is None:
            raise errors.NotFound('stack {} not found'.format(stack_name))
        return stack
    
    def list(self, **kwargs):
        """
        List stacks. Similar to the ``docker stack ls`` command.

        Args:
            names (:py:class:`list`): List of names to filter by.

        Returns:
            (list of :py:class:`Stack`) The stacks on the cluster.
        """
        resp = self.client.cli.stacks(**kwargs)
        stacks = [self.prepare_model(item) for item in resp['Stacks']]
        return stacks
