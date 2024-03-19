ARG PY_VERSION=3.10
ARG REPOSITORY=asm2vec-pytorch
ARG RADARE2_VERSION=5.8.8

# build stage
FROM --platform=linux/amd64 python:${PY_VERSION}-slim AS builder
ARG REPOSITORY

# install PDM
RUN apt-get update && apt-get install -y --no-install-recommends \
    unixodbc-dev \
    unixodbc \
    libpq-dev \
    git \
    gcc
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY . /${REPOSITORY}

# install dependencies and project into the local packages directory
WORKDIR /${REPOSITORY}
RUN mkdir __pypackages__ && pdm install --skip=:post --no-editable


# run stage
FROM --platform=linux/amd64 python:${PY_VERSION}-slim
ARG PY_VERSION
ARG REPOSITORY
ARG RADARE2_VERSION

# Install radare2
RUN apt-get update && apt-get install -y --no-install-recommends unixodbc unixodbc-dev curl unzip wget && \
    wget -O /tmp/radare2_${RADARE2_VERSION}_amd64.deb https://github.com/radareorg/radare2/releases/download/${RADARE2_VERSION}/radare2_${RADARE2_VERSION}_amd64.deb && \
    dpkg -i /tmp/radare2_${RADARE2_VERSION}_amd64.deb && \
    r2pm init && \
    r2pm update && \
    rm /tmp/radare2_${RADARE2_VERSION}_amd64.deb

# retrieve packages from build stage
ENV PYTHONPATH=/${REPOSITORY}/pkgs
COPY --from=builder /${REPOSITORY}/__pypackages__/${PY_VERSION}/lib /${REPOSITORY}/pkgs

# retrieve executables
COPY --from=builder /${REPOSITORY}/__pypackages__/${PY_VERSION}/bin/* /bin/

CMD ["/bin/sh"]
