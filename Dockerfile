FROM python:3.6-alpine as base

LABEL maintainer=cenx.com

ENV DOCKER_VERSION=18.06.0-ce
RUN wget -qO- https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_VERSION}.tgz | tar -xz docker/docker && \
   mv docker/docker /usr/local/bin/ && \
   rmdir docker

ENV KUBERNETES_VERSION=v1.10.3
#ENV KUBERNETES_VERSION=v1.11.1
RUN wget -q -O /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/${KUBERNETES_VERSION}/bin/linux/amd64/kubectl && \
    chmod +x /usr/local/bin/kubectl

FROM base as builder

# need these dependency in build stage as netifaces compiles native code
RUN apk add --no-cache build-base linux-headers
RUN pip --no-cache-dir install netifaces==0.10.7

#COPY --from=builder /install /usr
#COPY --from=builder /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages
#COPY --from=builder /usr/local/bin/pytest /usr/local/bin/pytest
#COPY --from=builder /usr/local/bin/docker-compose /usr/local/bin/docker-compose
#COPY --from=builder /usr/local/bin/maestro /usr/local/bin/maestro

COPY requirements.txt /usr/src
RUN pip --no-cache-dir install -r /usr/src/requirements.txt
#RUN pip install --install-option="--prefix=/install" -r /usr/src/requirements.txt

# unable to install maestro-ng as old docker-py package is not compatible with new docker package
# may need to put maestro-ng and dependencies into isolate virtualenv
#RUN apk add --no-cache git
#RUN pip install git+https://github.com/cenx-cf/maestro-ng.git
#RUN pip install git+https://github.com/cenx-cf/docker-py.git@f/1815-backport-to-1.10.6
#RUN pip install git+git://github.com/signalfx/maestro-ng

WORKDIR /usr/src
COPY . /usr/src
#RUN python setup.py sdist bdist_wheel
#RUN pip install dist/pytest_containers-0.1.0-py3-none-any.whl
RUN pip install .

FROM base

# copy only dependencies required to run package
COPY --from=builder /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

ENTRYPOINT ["/usr/local/bin/pytest"]