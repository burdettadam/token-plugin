FROM python:3.8-slim-buster as indy

#ARG u_id=1000
#ARG u_name=user


#===========================================indy-node===========================================
# addopted from https://github.com/hyperledger/indy-node/blob/master/docs/source/setup-dev.md

# Installing libsodium...
#RUN apt-get update && apt-get install -y libsodium-dev

# manual libsodium18 install example
#WORKDIR /root
#RUN cd /usr/lib/x86_64-linux-gnu \
#    && ln -s libssl.so.1.0.0 libssl.so.10 \
#    && ln -s libcrypto.so.1.0.0 libcrypto.so.10 \
#    && curl -fsSL https://github.com/jedisct1/libsodium/archive/1.0.18.tar.gz | tar -xz \
#    && cd libsodium-1.0.18 \
#    && ./autogen.sh \
#    && ./configure \
#    && make install \
#    && cd .. \  
#    && rm -rf libsodium-1.0.18 \
#    && curl https://sh.rustup.rs -sSf | sh -s -- -y

#===========================================ursa===========================================

WORKDIR /home/
# TODO: use github tag for ursa
#=======ursa-builder=======
FROM rust:latest as ursa-builder
WORKDIR /usr/src/
RUN git clone https://github.com/hyperledger/ursa.git 
WORKDIR /usr/src/ursa/libursa

RUN  cargo build --release
#=======ursa-builder=======

FROM indy as indy-ursa
COPY --from=ursa-builder /usr/src/ursa/target/release/libursa.so /usr/lib/

#===========================================ursa===========================================
#===========================================indy===========================================

WORKDIR /home/
# TODO: use github tag for libindy
#=======libindy-builder=======
FROM rust:latest as libindy-builder
# addopted from https://github.com/hyperledger/indy-sdk/blob/master/docs/build-guides/ubuntu-build.md
WORKDIR /usr/src/
RUN git clone https://github.com/hyperledger/indy-sdk.git
WORKDIR /usr/src/indy-sdk/libindy
RUN apt-get update && apt-get install -y libsodium-dev
RUN apt-get update && apt-get install -y libzmq3-dev

RUN  cargo build --release
#=======libindy-builder=======

FROM libindy-builder as libindy-ursa
COPY --from=libindy-builder /usr/src/indy-sdk/libindy/target/release/libindy.so /usr/lib/
#===========================================indy===========================================

#===========================================rocksdb===========================================
# TODO: make this a separate image and copy libs into token dev container.
# refer to make static_lib command. 
# based on Rocksdb install.md:
#
# Install git and make
# Upgrade your gcc to version at least 4.7 to get C++11 support.
RUN apt-get update && apt-get install -y git make build-essential
RUN apt-get update && apt-get install -y cmake
# Install gflags
RUN apt-get update && apt-get install -y libgflags-dev
# Install snappy
RUN apt-get update && apt-get install -y libsnappy-dev
# Install zlib
RUN apt-get update && apt-get install -y zlib1g-dev
# Install bzip2
RUN apt-get update && apt-get install -y libbz2-dev
WORKDIR /home/
# Clone rocksdb #TODO: figure out if we need to clone a particular release
RUN git clone https://github.com/facebook/rocksdb.git 
WORKDIR /home/rocksdb
#RUN mkdir build 
#WORKDIR /home/rocksdb/build
#RUN cmake ..
#https://github.com/twmht/python-rocksdb/issues/22#issuecomment-464369559
RUN make shared_lib
RUN make install-shared INSTALL_PATH=/usr
#RUN make
WORKDIR /home/rocksdb
#RUN export CPLUS_INCLUDE_PATH=${CPLUS_INCLUDE_PATH}${CPLUS_INCLUDE_PATH:+:}`pwd`/include/
#RUN export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}${LD_LIBRARY_PATH:+:}`pwd`/build/
#RUN export LIBRARY_PATH=${LIBRARY_PATH}${LIBRARY_PATH:+:}`pwd`/build/
#RUN make install-shared INSTALL_PATH=/usr
#RUN mkdir -p /usr/local/include/rocksdb/
#RUN cp -r ./include/* /usr/local/include/
#RUN pip install git+git://github.com/twmht/python-rocksdb.git#egg=python-rocksdb
#===========================================rocksdb===========================================

#===========================================indy-node===========================================
# TODO: use version tags for indy-node/plenum
RUN apt-get update && apt-get install -y \
    software-properties-common
RUN apt-get install -y \
     python3 \
     python3-dev \
     python3-pip \ 
     liblz4-dev \
     cython3

#RUN && apt-get install -y --no-install-recommends apt-utils \
    #&& apt-get install gcc make g++ libgflags-dev libsnappy-dev zlib1g-dev libbz2-dev liblz4-dev libzstd-dev -y

RUN pip3 install python-rocksdb

# remove the dependencies necessary to compile:
#RUN yes Y | apt-get remove --purge git libgflags-dev libsnappy-dev zlib1g-dev libbz2-dev liblz4-dev libzstd-dev
#RUN yes Y | apt-get remove --purge liblz4-dev libzstd-dev

WORKDIR /home
RUN git clone https://github.com/hyperledger/indy-node.git
RUN git clone https://github.com/hyperledger/indy-plenum.git
WORKDIR /home/indy-plenum/
RUN pip3 install -e .[tests]
WORKDIR /home/indy-node/
RUN pip3 install -e .[tests]
#RUN pip3 install boto3 ansible testinfra paramiko
WORKDIR /home/indy-node/indy_node
RUN pytest .

WORKDIR /home/indy-plenum/
RUN pytest .

#RUN add-apt-repository "deb https://repo.sovrin.org/sdk/deb xenial master" \
#    && apt-get update && apt-get install -y \
#        libindy-crypto=0.4.5 \
#        libindy=1.13.0~1420 \
#        libsovtoken=1.0.2~92 \
#    && rm -rf /var/lib/apt/lists/*

#RUN mkdir -p /etc/indy && echo "ENABLED_PLUGINS = ['sovtoken', 'sovtokenfees']" > /etc/indy/indy_config.py \
#    && pip3 install -U pipenv zipp==1.2.0

# TODO workaround (suggested by http://click.pocoo.org/5/python3/)
# to use pipenv's dependency 'click' (http://click.pocoo.org)
# check for alternatives
#ENV LC_ALL=C.UTF-8
#ENV LANG=C.UTF-8

#RUN if [ "$u_id" != "0" ]; then \
#        useradd -ms /bin/bash -u $u_id $u_name; \
#    fi
#USER $u_id

# TODO CMD ENTRYPOINT ...
#ENV CI_ENV_VERSION=0.21.0
