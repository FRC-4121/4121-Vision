# syntax=docker/dockerfile:1

#docker build -t team4121-vision-nouser:00.01 --force-rm --squash --network host -f team4121-vision-nouser.dockerfile .
#
FROM ubuntu:22.04
LABEL maintainer="victor.j.griswold@gmail.com"

RUN apt-get update && apt-get install -y \
    software-properties-common

RUN apt-get update && apt-get install -y \
	vim \
	nano \
    git \
    libsecret-1-0 \
    libsecret-1-dev \
    libsecret-tools \
    sudo \
    build-essential \
    cmake \
    ninja-build \
    libtool \
    automake \
    diffstat \
    texinfo \
    gawk \
    chrpath \
    dos2unix \
    wget \
    unzip \
    socat \
    locales \
    doxygen \
    libsdl1.2-dev \
    v4l2loopback-dkms \
    v4l2loopback-utils \
    ffmpeg \
    gstreamer1.0-opencv \
    python3 \
    python3-pip \
    python3-pyqt5 \
    libqt5x11extras5
    
RUN ln -sf /bin/bash /bin/sh
RUN locale-gen en_US.UTF-8 \
    && update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

# This logic is necessary because 'docker' is somehow blocking normal installation of the git libsecret support files.
# To work around this, we must manually install the necessary source files.
# The last line clears the apt package-list cache (would normally be done above, but it is still needed by 'apt download' here).
RUN mkdir /tmp/git_libsecret \
    && chmod o+w /tmp/git_libsecret \
    && cd /tmp/git_libsecret \
    && apt-get download git \
    && dpkg -x `ls` . \
    && mv ./usr/share/doc/git/contrib/credential/libsecret/Makefile /usr/share/doc/git/contrib/credential/libsecret \
    && mv ./usr/share/doc/git/contrib/credential/libsecret/git-credential-libsecret.c /usr/share/doc/git/contrib/credential/libsecret \
    && cd /usr/share/doc/git/contrib/credential/libsecret \
    && make \
    && rm -rf /tmp/git_libsecret \
    && rm -rf /var/lib/apt/lists/*
 
# Any user may now run the following to enable 'libsecret' support:
#
# git config --global credential.helper /usr/share/doc/git/contrib/credential/libsecret/git-credential-libsecret

RUN pip3 install numpy
RUN pip3 install opencv-contrib-python
RUN pip3 install robotpy-cscore
RUN pip3 install apriltag
RUN pip3 install wpilib

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US
ENV LC_ALL=en_US.UTF-8

WORKDIR /src
