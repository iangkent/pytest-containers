
define HELP

This Makefile contains build and test commands for the project.

Usage:

make help          - Show this message
make clean         - Remove generated files
make build         - Build container images
make test          - Run tests
make shell         - Run shell in container for interactive development
make push          - Push container image to remote registry
endef

export HELP

.PHONY: help clean build shell test ci push

help:
	@echo "$$HELP"

#export DOCKER_IMAGE_TAG := $(shell git rev-parse --short HEAD)
#export DOCKER_IMAGE_TAG := $(shell docker run --rm -v $${PWD}:/usr/src  -w /usr/src python:3.6-alpine /usr/local/bin/python setup.py --version)
export DOCKER_IMAGE_TAG := $(shell grep "version=" setup.py|cut -f 1 -d ','|cut -f 2 -d '='|tr -d "'")

clean:
	rm -rf build dist *.egg-info
	rm -f ./*.pyc
	rm -f ./**/*.pyc
	rm -rf ./**/__pycache__
	#find . -name __pycache__ -delete
	rm -rf ./**/.cache
	rm -rf ./**/**/.pytest_cache
	rm -rf .pytest_cache
	rm -rf ./target
	rm -rf ./docs/_build
	#docker-compose down --volumes
	-docker container rm -v --force `docker container ps -aq --filter label=pytest_fixture` 2>/dev/null
	-docker volume rm `docker volume ls -q --filter label=pytest_fixture` 2>/dev/null
	-docker image rm pytest-containers:$(DOCKER_IMAGE_TAG)

prune: clean
	docker system prune --all --volumes --force

build:
	docker-compose build

.PHONY: docs
docs:
#docs: build
	docker-compose run --rm docs

shell: build
	docker-compose run --rm shell

python: build
	docker-compose run --rm python

test: build
	docker-compose run --rm test

testfast: build
	docker-compose run --rm test tests/test_containers.py::test_docker_client_container[default-anonymous]

push: test
	# push plugin to Test PyPI
	# python setup.py register
	# pip install twine
	# twine upload --username iangkent --repository-url https://test.pypi.org/legacy/ dist/*
	# test pull package from Test PyPI
	# pip install --index-url https://test.pypi.org/simple/ pytest_containers
	# push plugin to PyPI
	# twine upload --username iangkent dist/*
	# test pull package from PyPI
	# pip install pytest_containers
	# test pull package
	# push image to docker registry
	docker-compose push