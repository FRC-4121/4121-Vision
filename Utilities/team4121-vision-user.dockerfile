# syntax=docker/dockerfile:1

#docker build -t team4121-vision-${USER}:00.02 --force-rm --squash --network host --build-arg USERNAME=${USER} --build-arg PUID=${UID} --build-arg PGID=`id -g ${USER}` -f team4121-vision-user.dockerfile .
#docker run -v $PWD:/home/${USER} --detach-keys='ctrl-[,z' -it --rm --network host team4121-vision-${USER}:00.02 /bin/bash
#
FROM team4121-vision-nouser:00.02
LABEL maintainer="victor.j.griswold@gmail.com"

ARG PGID
ARG PUID
ARG USERNAME
ENV IMAGEUSER=$USERNAME

RUN groupadd --gid ${PGID} ${USERNAME} \
    && useradd --uid ${PUID} --gid ${PGID} --home-dir /home/${USERNAME} ${USERNAME} \
    && mkdir /home/${USERNAME} \
    && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME} \
    && usermod -G sudo,audio,video ${USERNAME}
RUN echo "${USERNAME}:${USERNAME}" | chpasswd

USER ${USERNAME}
WORKDIR /home/${USERNAME}
