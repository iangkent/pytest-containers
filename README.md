# pytest-containers

[![PyPI Version](https://img.shields.io/pypi/v/pytest-containers.svg)](https://pypi.org/project/pytest-containers)
[![Python Versions](https://img.shields.io/pypi/pyversions/pytest-containers.svg)](https://pypi.org/project/pytest-containers)
[![Build Status](https://travis-ci.org/iangkent/pytest-containers.svg?branch=master)](https://travis-ci.org/iangkent/pytest-containers)

A [pytest](https://docs.pytest.org/) plugin for docker and kubernetes fixtures. The plugin provides a framework for testing docker container images.

This plugin enables you to test code run in containers that relies on docker resources (container, volume, secret, network, ....).
It allows you to specify fixtures for docker resources.

The main interface provided by this plugin is a set of fixtures and 'fixture factories'.

## Features

* orchestrate fixtures using [docker compose](https://docs.docker.com/compose/)
* orchestrate fixtures using [docker swarm](https://docs.docker.com/engine/swarm/)
* orchestrate fixtures using [kubernetes](https://kubernetes.io)
* orchestrate fixtures using [maestro-ng](https://github.com/signalfx/maestro-ng)
* orchestrate fixtures using low level docker and kubernetes interfaces

## Requirements

* [docker](https://docs.docker.com/engine/installation/) (Tested on 18.06)
* Python (Tested on 3.6)
* [pytest](https://github.com/pytest-dev/pytest) (Tested on 3.6.4)
* [docker-py](https://github.com/docker/docker-py) (Tested on 3.5.0)
* [docker-compose](https://docs.docker.com/compose/) (Tested on 1.22.0)
* [maestro-ng](https://github.com/signalfx/maestro-ng) (Tested on 0.5.4)
* [kubernetes](https://kubernetes.io/docs/setup/) (Tested on 1.10.3)

## Installation

You can install "pytest-containers" via _pip_ from _PyPI_:

```bash
pip install pytest-containers
```

Or include it as a dependency on `setup.py` or a `requirements.txt` file, whatever you prefer.

<!-- conftest.py pytest_plugins = [‘pytest_containers’] -->

## Usage

The following tests demonstrate how to use the fixtures provided by this plugin.

```python
# test_container.py
def test_is_healthy(container):
    assert container.status == 'running'
...
```

### Fixtures

#### docker_client

The docker_client fixture returns an instance of the [official docker client](https://docker-py.readthedocs.io/en/stable/client.html).

```python
def test_docker_version(docker_client):
    res = docker_client.version() 
    assert 'GoVersion' in res
    assert 'Version' in res
```

#### container

The container fixture returns an instance of [Container](https://docker-py.readthedocs.io/en/stable/containers.html#container-objects).

```python
def test_container(container):
    assert container.status == 'running'
```

#### client_container

The client container fixture returns an instance of [Container](https://docker-py.readthedocs.io/en/stable/containers.html#container-objects) connected to another container.

```python
def test_client_container(container, client_container):
    assert container.status == 'running'
    assert client_container.status == 'running'
```

#### network

The container fixuture returns an instance of [Network](https://docker-py.readthedocs.io/en/stable/networks.html#network-objects).

```python
def test_default_network(network):
    assert network.name == 'bridge'
    assert network.attrs['Options']['com.docker.network.bridge.default_bridge' == 'true'
```

#### image

The container fixuture returns an instance of [Image](https://docker-py.readthedocs.io/en/stable/images.html#image-objects).

```python
def test_image(image):
    assert image is not None
```

[Read the full documentation](https://pytest-containers.readthedocs.io) to see everything you can do.

## Contributing

Contributions are very welcome. Tests can be run with `tox`, please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [Apache Software License 2.0](http://www.apache.org/licenses/LICENSE-2.0) license, "pytest-containers" is free and open source software

## Issues

If you encounter any problems, please `file an issue` along with a detailed description.

* [file an issue](https://github.com/iangkent/pytest-containers/issues)
* [pytest](https://github.com/pytest-dev/pytest)
* [tox](https://tox.readthedocs.io/en/latest/)
* [pip](https://pypi.org/project/pip/)
* [PyPI](https://pypi.org/project)

## Similar Projects

* [pytest docker plugins](https://pypi.org/search/?q=docker&c=Framework+%3A%3A+Pytest)
* [pytest-docker-compose](https://github.com/centralityai/pytest-docker-compose)
* [pytest-docker](https://github.com/AndreLouisCaron/pytest-docker)
* [lovely-pytest-docker](https://github.com/lovelysystems/lovely-pytest-docker)
* [pytest-docker-db](https://github.com/kprestel/pytest-docker-db)
* [pytest-docker-fixtures](https://github.com/guillotinaweb/pytest-docker-fixtures)
* [pytest-docker-tools](https://pypi.org/project/pytest-docker-tools/)
* [pytest-mysql](https://pypi.org/project/pytest-mysql/)
* [pytest-postgres](https://github.com/clayman74/pytest-postgres)
* [dockerintegration](https://github.com/ShaneDrury/dockerintegration)
* [docker-services](https://github.com/dmonroy/docker-services)