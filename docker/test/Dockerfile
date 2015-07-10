# DOCKER IMAGE FOR TESTING DATACATS
FROM ubuntu:14.04

MAINTAINER boxkite

RUN locale-gen en_US.UTF-8 && \
echo 'LANG="en_US.UTF-8"' > /etc/default/locale

USER root

RUN apt-get update -y
RUN apt-get -y install wget git python-virtualenv
RUN wget -qO- http://get.docker.io | bash
RUN useradd -G docker -m datacats
RUN echo 'datacats ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER datacats
RUN virtualenv /home/datacats/venv
USER root
COPY ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD bash
