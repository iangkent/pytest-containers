#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='pytest-containers',
    # version must be same across python packag and container image
    # https://github.com/docker/compose/blob/master/setup.py
    version='0.1.0',
    author='Ian Kent',
    author_email='iangkent@gmail.com',
    maintainer='Ian Kent',
    maintainer_email='iangkent@gmail.com',
    license='Apache Software License 2.0',
    url='https://github.com/iangkent/pytest-containers',
    description='A pytest plugin for docker and kubernetes fixtures.',
    long_description=read('README.md'),
    #py_modules=['pytest_containers'],
    #packages=['pytest_containers', 'pytest_containers.dockerx'],
    packages=find_packages(exclude=['tests.*', 'tests']),
    python_requires='>=3.6',
    install_requires=required,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
    ],
    keywords=[
        'docker',
        'docker-compose',
        'kubernetes',
        'maestro-ng',
        'pytest',
    ],
    entry_points={
        'pytest11': [
            'containers = pytest_containers',
        ],
    },
)
