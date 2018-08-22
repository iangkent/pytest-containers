import json
import yaml
from docker import utils


class StackApiMixin(object):

    def stacks(self, filters=None):
        """
        List stacks. Similar to the ``docker stack ls`` command.
        """
        result = self.dispatch(['stack', 'ls', '--format', '{{json .}}'], returncode=0)
        string_list = result.stdout.split('\n')
        dict_list = []
        for item in string_list:
            if item is not '':
                dict = json.loads(item)
                dict_list.append(dict)
        dict = {'Stacks': dict_list}
        return dict

    def deploy_stack(self, name, compose_file, **kwargs):
        result = self.dispatch(['stack', 'deploy', '--compose-file', compose_file, name], returncode=0)
        resp = {'Name': name}
        return resp

    #@utils.check_resource('stack')
    def remove_stack(self, name):
        self.dispatch(['stack', 'rm', name], returncode=0)
        return

    def services(self):
        pass

    def tasks(self):
        """
        List the tasks in the stack.
        """
        pass