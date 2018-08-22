import logging
import os
import time
import random
import re

import pytest

import docker

from . import dockerx

log = logging.getLogger(__name__)


def pytest_addoption(parser):
    group = parser.getgroup('containers')
    group.addoption(
        '--foo',
        action='store',
        dest='dest_foo',
        default='2018',
        help='Set the value for the fixture "bar".'
    )

    parser.addini('HELLO', 'Dummy pytest.ini setting')


@pytest.fixture
def bar(request):
    return request.config.option.dest_foo


@pytest.fixture(scope='session')
def docker_client():
    """Return session scoped docker client used to communicate with docker daemon via api or cli.

    Example:
        >>> def test_docker_version(docker_client):
        >>>     result = docker_client.version()
        >>>     assert 'GoVersion' in result
        >>>     assert 'Version' in ressult

    """
    client = dockerx.from_env()
    yield client
    client.close()

# Fixture parametrization helps to write exhaustive functional tests for components
# which themselves can be configured in multiple ways


@pytest.fixture(scope='module')
def docker_registry(request):
    """Return docker registry.
    """
    return os.getenv('DOCKER_REGISTRY', '')


@pytest.fixture(scope='module')
def service_name(request):
    """Return name of service under test.
    """
    service_name = getattr(request.module, 'service_name', 'python-hello')
    # service_name = getattr(request.module, 'service_name')
    # exception AttributeError
    # pytest.fail('module variable not defined: {}'.format(request.module))
    return service_name


def random_name(name = None):
    name = '' if name == None else '_' + name
    return u'pytest{0}_{1:x}'.format(name, random.getrandbits(64))


@pytest.fixture(scope='module')
def image(request, docker_client, docker_registry, service_name):
    """Return image under test.
    """
    docker_image_name = service_name if service_name != 'python-hello' else 'google/python-hello'
    docker_image_tag = os.getenv('DOCKER_IMAGE_TAG', 'latest')
    docker_image_repo_tag ='{}{}{}:{}'.format(docker_registry, '/' if docker_registry != '' else '', docker_image_name, docker_image_tag)
    try:
        image = docker_client.images.get(docker_image_repo_tag)
    except docker.errors.ImageNotFound:
        image = docker_client.images.pull(docker_image_repo_tag)
    return image


@pytest.fixture(scope='session', params=[None, "swarm", "kubernetes", "compose", "maestro"])
def orchestrator(request):
    """Return container orchestrator used during test session.
    """
    log.info('orchestrator={}'.format(request.param))
    yield 'orchestrator={}'.format(request.param)
    log.info('orchestrator={}'.format(request.param))


@pytest.fixture(scope='session')
def swarm(request, docker_client):
    """Setup Docker Swarm used during test session.
    """
    swarm_preexist = False
    try:
        log.info('docker swarm init')
        if docker_client.swarm.init():
            log.info('Swarm initialized: current node is now a manager.')
    except docker.errors.APIError as err:
        log.info(err.explanation)
        swarm_preexist = True
    swarm = True
    yield swarm
    if swarm_preexist is not True:
        log.info('docker swarm leave --force')
        docker_client.swarm.leave(force=True)
        log.info('Node left the swarm.')


@pytest.fixture(scope='session', params=["none", "named"])
def secret(request):
    """ Return docker secret.
    """
    log.debug('docker create secret {}'.format(request.param))
    yield 'secret={}'.format(request.param)
    log.debug('docker rm secret {}'.format(request.param))


def idfn(fixture_value):
    return 'hander={}'.format(fixture_value)


# log = [console, file]
@pytest.fixture(scope='session', params=['none', "console", "file"], ids=idfn)
def log_handler(request):
    log.debug('handler={}'.format(request.param))
    yield 'handler={}'.format(request.param)
    log.debug('handler={}'.format(request.param))


@pytest.fixture(scope='class')
def data_container(docker_client, image, service_name):
    """Return docker volume container.
    """
    log.info('setup data container')
    data_container_name = random_name(service_name + '_data')
    command = 'sleep 30'
    labels = ['pytest_fixture']
    log.info('docker container run -d --name {} --label {} {} {}'.format(data_container_name, labels[0], image.attrs['RepoTags'][0], command))
    container = docker_client.containers.run(image=image, name=data_container_name, labels=labels, command=command, detach=True)
    log.info('data container id = {}'.format(container.short_id))
    yield container
    log.info('teardown data container')
    log.info('docker container rm --volumes --force {}'.format(container.id))
    container.remove(v=True, force=True)


@pytest.fixture(scope='class', params=['bind', 'anonymous', 'named', 'container'])
def volumes(request, docker_client, service_name, image):
    """Return docker volume based on parameter.

    Parameters:
        bind: volume lives on the Docker host's filesystem and can be accessed from within the container
        anonymous: volume is created and handled by docker engine
        named: volume is created and handled by docker engine using name provided
        container: volume shared from data container
    """
    log.info('setup volumes')
    volumes = []
    # discover volume target paths by inspecting image
    image_volumes = image.attrs['Config']['Volumes'] or []
    for image_volume in image_volumes:
        volumes.append({'type': request.param, 'source': '', 'target': image_volume})
    if request.param == 'named':
        for volume in volumes:
            volume['source'] = random_name(service_name + '_' + os.path.basename(volume['target']))
            labels = ['pytest_fixture']
            log.info('docker volume create --label {} {}'.format(labels, volume['source']))
            docker_client.volumes.create(name=volume['source'], driver='local', labels=labels)
    elif request.param == 'bind':
        tmpdir_factory = request.getfixturevalue('tmpdir_factory')
        name = request.node.name
        name = re.sub(r"[\W]", "_", name)
        tmpdir = tmpdir_factory.mktemp(basename=name, numbered=True)
        for volume in volumes:
            datadir = tmpdir.mkdir(service_name + '_' + os.path.basename(volume['target']))
            log.info('mkdir {}'.format(datadir))
            volume['source'] = datadir
    elif request.param == 'container':
        data_container = request.getfixturevalue('data_container')
        for volume in volumes:
            volume['source'] = '{}'.format(data_container.id)
    else:
        log.info('anonymous volume will be created with docker container')
    yield volumes
    log.info('teardown volumes')
    if request.param == 'named':
        # named volumes are not automatically removed by docker
        for volume in volumes:
            log.info('docker volume rm {}'.format(volume['source']))
            volume = docker_client.volumes.get(volume['source'])
            volume.remove()
    elif request.param == 'anonymous':
        log.info('anonymous volumes will be removed with container')


@pytest.fixture(scope='class', params=['host', 'default', 'bridge', 'overlay'])
def network(request, docker_client, service_name):
    """Return docker network based on parameter.

    Parameters:
        host: uses the host’s networking directly
        default: default bridge type network
        bridge: software bridge which allows containers connected to the same bridge network to communicate
        overlay: creates a distributed network among multiple Docker daemon hosts

    Examples:
        >>> def test_docker_network(network):
        >>>     assert network is not None

        >>> @pytest.mark.parametrize(argnames=('network'),
        >>>                          argvalues=[('default'), ('overlay')],
        >>>                          indirect=['network'])
        >>> def test_docker_network(network):
        >>>    assert network is not None

    """
    log.info('setup network')
    network_name = random_name(service_name)
    if request.param not in ['host', 'default']:
        labels = {'pytest_fixture': ''}
        log.info('docker network create --label {} --driver {} --attachable {}'.format(labels, request.param, network_name))
        network = docker_client.networks.create(name=network_name, driver=request.param, labels=labels, attachable=True)
        network_start_period = 5
        log.info('waiting {} seconds for network creation to complete'.format(network_start_period))
        time.sleep(network_start_period)
    else:
        network_name = request.param if request.param != 'default' else 'bridge'
        log.info('docker network ls --filter type=builtin --filter name={}'.format(network_name))
        networks = docker_client.networks.list(names=[network_name])
        for possible_network in networks:
            if possible_network.name == network_name:
                network = possible_network
                break
    log.info('network id = {}'.format(network.short_id))
    yield network
    log.info('teardown network')
    if network.name in ['host', 'bridge']:
        log.info('no need to remove builtin network named "{}"'.format(network.name))
    else:
        log.info('docker network rm {}'.format(network.name))
        network.remove()


@pytest.fixture(scope='class')
def environment(request):
    """ Return environment variable dict.
    """
    environment = {}
    yield environment


@pytest.fixture(scope='module')
def container_factory(docker_client):
    """ Return factory used to make container fixtures.
    """
    log.info('setup container factory')
    created_containers = []
    def _container_factory(image=image, service_name=None, network=None, volumes=None, environment=None):
        container_name = random_name(service_name)
        # https://forums.docker.com/t/docker-for-mac-does-not-add-docker-hostname-to-etc-hosts/8620/8
        hostname = 'localhost' if network.name == 'host' else None
        volumes_option = ''
        volumes_dict = {}
        volumes_from = []
        for volume in volumes:
            if volume['type'] in ['bind', 'named']:
                volumes_option += '-v {}:{} '.format(volume['source'], volume['target'])
                volumes_dict[volume['source']] = {'bind': volume['target']}
            elif volume['type'] == 'container':
                volumes_option += '--volumes-from {} '.format(volume['source'])
                volumes_from.append(volume['source'])
        environment_option = ''
        for key, value in environment.items() :
            environment_option += '-e {}={} '.format(key, value)
        labels = ['pytest_fixture']
        log.info('docker container run -d --name {} --label {} {}{} {} {} {}'.format(
            container_name, labels[0],
            '' if network.name == 'bridge' else ' --network ' + network.name,
            '' if hostname == None else ' --hostname ' + hostname,
            volumes_option, environment_option, image.attrs['RepoTags'][0]))
        container = docker_client.containers.run(
            image=image, name=container_name,
            network=network.name, hostname=hostname,
            volumes=volumes_dict, volumes_from=volumes_from,
            environment=environment, labels=labels, detach=True)
        # need to use low level api as network alias is not supported in high level api
        # https://github.com/docker/docker-py/issues/982
        #ccontainer = docker_client.api.create_container(
        #    image=image, name=container_name,
        #    network=network.name, hostname=hostname,
        #    networking_config=client.create_networking_config(
        #        endpoints_config={network.name: docker_client.api.create_endpoint_config(aliases=['foo', 'bar'])},
        #    volumes=volumes_dict, volumes_from=volumes_from,
        #    environment=environment, detach=True)
        log.info('container id = {}'.format(container.short_id))
        try:
            health_start_period = int(image.attrs['ContainerConfig']['Healthcheck']['StartPeriod'] / 1000000000)
        except KeyError:
            health_start_period = 1
        log.info("waiting {} seconds for service to start".format(health_start_period))
        time.sleep(health_start_period)
        created_containers.append(container)
        return container
    yield _container_factory
    log.info('teardown container factory')
    for container in created_containers:
        if len(docker_client.containers.list(filters={'id': container.id})) > 0:
            log.info('docker container rm --volumes --force {}'.format(container.name))
            container.remove(v=True, force=True)


@pytest.fixture(scope='class')
def container(docker_client, container_factory, image, service_name, network, volumes, environment):
    """ Return class scoped container fixture.

    Example:
        >>> def test_container(container):
        >>>     assert container.status == 'running

    """
    log.info('setup container')
    container = container_factory(image=image, service_name=service_name, volumes=volumes, network=network, environment=environment)
    yield container
    log.info('teardown container')
    log.info('docker container rm --volumes --force {}'.format(container.name))
    container.remove(v=True, force=True)


@pytest.fixture(scope='module')
def client_container_factory(docker_client):
    """ Return factory used to make client container fixtures.
    """
    log.info('setup client container factory')
    created_client_containers = []
    def _client_container_factory(container=None, image=None):
        command = 'top'
        image = container.image if image is None else image
        container.reload()
        # discover service container's network
        network_mode = container.attrs['HostConfig']['NetworkMode']
        network_id = container.attrs['NetworkSettings']['Networks'][network_mode]['NetworkID']
        network = docker_client.networks.get(network_id)
        client_container_name = random_name(container.name + '_client')
        links = {container.name: container.name} if network.name == 'bridge' else {}
        extra_hosts = {container.name: '127.0.0.1'} if network.name == 'host' else {}
        labels = ['pytest_fixture']
        log.info('docker container run -d --name {} --label {}'
            '{} {} {} {} {}'.format(
                client_container_name, labels[0],
                '' if links == {} else ' --link {}'.format(links),
                '' if network.name == 'bridge' else ' --network ' + network.name,
                '' if extra_hosts == {} else ' --add-host {}'.format(extra_hosts),
                image.attrs['RepoTags'][0], command))
        client_container = docker_client.containers.run(image=image, name=client_container_name,
                                                        network=network.name, links=links,
                                                        extra_hosts=extra_hosts,
                                                        command=command, labels=labels, detach=True)
        log.info('client container id = {}'.format(client_container.short_id))
        created_client_containers.append(client_container)
        return client_container
    yield _client_container_factory
    log.info('teardown client container factory {}'.format(_client_container_factory))
    for client_container in created_client_containers:
        if len(docker_client.containers.list(filters={'id': client_container.id})) > 0:
            log.info('docker container rm --volumes --force {}'.format(client_container.name))
            client_container.remove(v=True, force=True)


@pytest.fixture(scope='class')
def client_container(client_container_factory, container):
    """ Return class scoped client container fixture.
    """
    log.info('setup client container')
    client_container = client_container_factory(container=container)
    yield client_container
    log.info('teardown client container')
    log.info('docker container rm --volumes --force {}'.format(client_container.name))
    client_container.remove(v=True, force=True)

@pytest.fixture(scope='class', params=[1])
def service(request, docker_client, swarm, image, network, volumes, environment):
    # TODO namespace the service using random name
    service_name_random = random_name(service_name)
    replicas = request.param
    image_name = image.attrs['RepoTags'][0]
    log.info('docker service create --name {} --detach=true '
             '--network {} --replicas {} --constraint "node.role == manager" {}'.format(service_name_random, network.name,
                                                                                      replicas, image_name))
    service_mode = docker.types.ServiceMode(mode='replicated', replicas=replicas)
    service = docker_client.services.create(image=image_name, name=service_name_random,
                                            networks=[network.name],
                                            mode=service_mode,
                                            constraints=['node.role == manager'])
    log.info('service id = {}'.format(service.id))
    health_start_period = int(image.attrs['ContainerConfig']['Healthcheck']['StartPeriod'] / 1000000000)
    log.info("waiting {} seconds for service to start".format(health_start_period))
    time.sleep(health_start_period)
    yield service
    # container = docker_client.containers.get(service.tasks()[0]['Status']['ContainerStatus']['ContainerID'])
    # mounts = container.attrs['Mounts']
    log.info('docker service rm {}'.format(service.name))
    service.remove()
    # TODO confirm that docker swarm will prune service volumes
    # for mount in mounts:
    #    log.info('docker volume rm {}'.format(mount['Name']))
    #    volume = docker_client.volumes.get(mount['Name'])
    #    volume.remove()