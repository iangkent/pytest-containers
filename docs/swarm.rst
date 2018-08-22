Swarm
=====
.. py:module:: pytest_containers

To use any swarm methods, you first need to make the Engine part of a swarm. This can be done by either initializing a new swarm with init().

The ``swarm`` fixture returns an instance `docker.models.swarm.Swarm <https://docker-py.readthedocs.io/en/stable/swarm.html>`_.

.. autofunction:: swarm()

**Example**

.. code-block:: python

  @pytest.mark.usefixtures("swarm")
  def test_service(service):
    ...