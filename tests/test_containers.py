# -*- coding: utf-8 -*-
import pytest

def test_bar_fixture(testdir):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makepyfile("""
        def test_sth(bar):
            assert bar == "europython2015"
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--foo=europython2015',
        '-v'
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_sth PASSED*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'containers:',
        '*--foo=DEST_FOO*Set the value for the fixture "bar".',
    ])


def test_hello_ini_setting(testdir):
    testdir.makeini("""
        [pytest]
        HELLO = world
    """)

    testdir.makepyfile("""
        import pytest

        @pytest.fixture
        def hello(request):
            return request.config.getini('HELLO')

        def test_hello_world(hello):
            assert hello == 'world'
    """)

    result = testdir.runpytest('-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_hello_world PASSED*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0

def test_docker_client_fixture(testdir):
    testdir.makepyfile(
        """
        import pytest
        from pytest_containers import docker_client

        def docker_client(docker_client):
            assert docker_client is not None
    """)
    result = testdir.runpytest('-v')
    assert result.ret == 0

def test_docker_container(container):
    assert container is not None
    container.reload()
    assert container.status == 'running'

def test_docker_client_container(container, client_container):
    assert container is not None
    assert client_container is not None
    assert container.status == 'running'
    client_container.reload()
    assert client_container.status == 'running'


@pytest.mark.parametrize(argnames=('network'),
                         argvalues=[('default'), ('overlay')],
                         indirect=['network'])
def test_docker_network(network):
    assert network is not None

