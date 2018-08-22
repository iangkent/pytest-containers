Images
======
.. py:module:: pytest_containers

The ``image`` fixture returns an instance `docker.models.images.Image <https://docker-py.readthedocs.io/en/stable/images.html>`_.

.. autofunction:: image()

**Example**

.. code-block:: python

  def test_image_size(image):
    expected_max_image_size = 250000000
    assert int(image.attrs['VirtualSize']) < expected_max_image_size
